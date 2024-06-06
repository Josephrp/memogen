from autogen import AssistantAgent, ConversableAgent, UserProxyAgent
from autogen.coding import LocalCommandLineCodeExecutor
from autogen.cache import Cache
from autogen.agentchat.contrib.math_user_proxy_agent  import MathUserProxyAgent
from src.config import llm_config
from docx import Document
from docx.text.paragraph import Paragraph
import os
from typing import Optional, List, Tuple
from markdown2 import markdown
from bs4 import BeautifulSoup
from src.prompts import file_writer_agent_system_message, writer_system_message, critic_system_message, financial_reviewer_system_message, outliner_system_message, quality_system_message, layman_system_message

# -------- CODEX

executor = LocalCommandLineCodeExecutor(
    timeout=3600,
    work_dir="./src/codex",
)


file_writer_agent = ConversableAgent(
    name="file_writer_agent",
    system_message = file_writer_agent_system_message,
    llm_config=llm_config,
    code_execution_config={"executor": executor},
    human_input_mode="NEVER",
    default_auto_reply=
    "Please continue. If everything is done, reply 'TERMINATE'.",
)


# -------- Writer

writer = AssistantAgent(
    name="Writer",
    system_message=writer_system_message,
    llm_config=llm_config,
)

outliner = AssistantAgent(
    name="Writer",
    system_message=outliner_system_message,
    llm_config=llm_config,
)

# -------- Reviewers

critic = AssistantAgent(
    name="Critic",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    llm_config=llm_config,
    system_message=critic_system_message,
)

layman_reviewer = AssistantAgent(
    name="Layman Reviewer",
    description="A reviewer that makes sure a laywoman would fully understand the content provided to her.",
    llm_config=llm_config,
    system_message=layman_system_message,
)

financial_reviewer = AssistantAgent(
    name="Financial Reviewer",
    description='A reviewer that makes sure financial justification are credible',
    llm_config=llm_config,
    system_message=financial_reviewer_system_message,
)

quality_reviewer = AssistantAgent(
    name="Quality Assurance Reviewer",
    description="a reviewer that makes sure that claims are well justified",
    llm_config=llm_config,
    system_message=quality_system_message,
)

meta_reviewer = AssistantAgent(
    name="Meta Reviewer",
    llm_config=llm_config,
    system_message="You are a meta reviewer, you aggragate and review "
    "the work of other reviewers and give a final suggestion on the content.",
)

# --------  Math


mathproxyagent = MathUserProxyAgent(
    name="mathproxyagent",
    human_input_mode="NEVER",
    code_execution_config={"use_docker": False},
)

# --------  Planner



planner = AssistantAgent(
    name="planner",
    llm_config=llm_config,
    # the default system message of the AssistantAgent is overwritten here
    system_message="You are a helpful AI assistant. You suggest coding and reasoning steps for another AI assistant to accomplish a task. Do not suggest concrete code. For any action beyond writing code or reasoning, convert it to a step that can be implemented by writing code. For example, browsing the web can be implemented by writing code that reads and prints the content of a web page. Finally, inspect the execution result. If the plan is not good, suggest a better plan. If the execution is wrong, analyze the error and suggest a fix.",
)

planner_user = UserProxyAgent(
    name="planner_user",
    max_consecutive_auto_reply=0,  # terminate without auto-reply
    human_input_mode="NEVER",
    code_execution_config={
        "use_docker": False
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
)

def ask_planner(message):
    planner_user.initiate_chat(planner, message=message)
    # return the last message received from the planner
    return planner_user.last_message()["content"]

assistant = AssistantAgent(
    name="assistant",
    llm_config={
        "temperature": 0,
        "timeout": 600,
        "cache_seed": 42,
        "config_list": llm_config,
        "functions": [
            {
                "name": "ask_planner",
                "description": "ask planner to: 1. get a plan for finishing a task, 2. verify the execution result of the plan and potentially suggest new plan.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "question to ask planner. Make sure the question include enough context, such as the code and the execution result. The planner does not know the conversation between you and the user, unless you share the conversation with the planner.",
                        },
                    },
                    "required": ["message"],
                },
            },
        ],
    },
)

# create a UserProxyAgent instance named "user_proxy"
user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    # is_termination_msg=lambda x: "content" in x and x["content"] is not None and x["content"].rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "planning",
        "use_docker": False,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
    function_map={"ask_planner": ask_planner},
)


# --------  Tools


@file_writer_agent.register_for_execution()
@file_writer_agent.register_for_llm(description="Reads and loads the data from a .docx file as plain text and returns the complete file content as plain text.")
def read_docx_as_plain_text(filepath: str = '.src/result/result.docx') -> Optional[str]:
    """
    Reads and loads the data from a .docx file as plain text and returns the complete file content as plain text.

    :param filepath: The path to the .docx file to be read.
    :return: The plain text content of the .docx file, or None if the file cannot be read.
    """
    try:
        # Load the Document
        doc = Document(filepath)
        
        # Initialize an empty string to hold the text
        full_text = []
        
        # Iterate through each paragraph in the document
        for para in doc.paragraphs:
            full_text.append(para.text)
        
        # Join all paragraphs into a single string separated by newlines
        result_text = "\n".join(full_text)
        
        return result_text
    except Exception as e:
        print(f"An error occurred while reading the .docx file: {e}")
        return None
    
@file_writer_agent.register_for_execution()
@file_writer_agent.register_for_llm(description="Appends text to the end of a given title in a .docx file (before the next title) and saves the updated document.")
def append_text_to_title( title: str, text_to_append: str, doc_path: str= '.src/result/result.docx', save_path: Optional[str] = None ) -> None:
    """
    Converts markdown to .docx and appends text to the end of a given title in a .docx file (before the next title) and saves the updated document.

    :param title: The title to search for in the document.
    :param text_to_append: The text to append to the end of the section with the specified title.
    :return: None
    """
    try:
        # Convert markdown text to Docx-suitable format
        formatted_text = markdown_to_docx_format(text_to_append)
     
    try:
        # Load the Document
        doc = Document(doc_path)
        
        # Iterate through paragraphs to find the title
        found_title = False
        insertion_point = None

        for i, para in enumerate(doc.paragraphs):
            if found_title:
                if para.style.name.startswith('Heading'):
                    # We have reached the next title
                    insertion_point = i
                    break
            elif para.text.strip() == title:
                found_title = True

        # If the title is found, insert the text
        if found_title:
            if insertion_point is None:
                # Append to the end of the document if no next title is found
                doc.add_paragraph(formatted_text)
            else:
                # Insert before the next title
                doc.paragraphs.insert(insertion_point, Paragraph(text_to_append, doc))
        
        # Save the updated document
        if save_path is None:
            save_path = doc_path
        doc.save(save_path)
        print(f"Document updated and saved at: {save_path}")

    except Exception as e:
        print(f"An error occurred while processing the .docx file: {e}")

# # Example usage
# doc_path = ".src/result/result.docx"
# title_to_search = "Introduction"
# text_to_append = "This is the appended text."
# append_text_to_title(doc_path, title_to_search, text_to_append)

@file_writer_agent.register_for_execution()
@file_writer_agent.register_for_llm(description="Replaces the text between the specified title and the next title in a .docx file with new text.")
def replace_section_with_text(title: str, new_text: str, doc_path: str= '.src/result/result.docx',  save_path: Optional[str] = None) -> None:
    """
    Converts Markdown text and Replaces the text between the specified title and the next title in a .docx file with new text.

    :param doc_path: The path to the .docx file to be read.
    :param title: The title that marks the beginning of the section to replace.
    :param new_text: The new text to insert in place of the specified section.
    :param save_path: The path to save the updated .docx file. If None, overwrites the original file.
    :return: None
    """
    try:
        # Convert markdown text to Docx-suitable format
        formatted_text = markdown_to_docx_format(new_text)
     
    try:
        # Load the Document
        doc = Document(doc_path)
        
        # Initialize variables to track the section boundaries
        section_start = None
        section_end = None

        # Find the title and the boundaries of the section to replace
        for i, para in enumerate(doc.paragraphs):
            if section_start is not None and para.style.name.startswith('Heading'):
                section_end = i
                break
            if para.text.strip() == title:
                section_start = i

        # If the title is found, replace the section
        if section_start is not None:
            # Remove old section paragraphs
            if section_end is None:
                # If no next title, clear till the end of the document
                section_end = len(doc.paragraphs)
            for _ in range(section_end - section_start - 1):
                del doc.paragraphs[section_start + 1]
                
            # Insert new text
            new_paragraphs = formatted_text.split("\n")
            for new_para in new_paragraphs:
                doc.paragraphs[section_start].insert_paragraph_before(new_para)
            del doc.paragraphs[section_start]  # Remove the old title paragraph as the new ones include the title

        # Save the updated document
        if save_path is None:
            save_path = doc_path
        doc.save(save_path)
        print(f"Document updated and saved at: {save_path}")

    except Exception as e:
        print(f"An error occurred while processing the .docx file: {e}")

@file_writer_agent.register_for_execution()
@file_writer_agent.register_for_llm(description="Converts markdown content to a single string with python-docx compatible formatting.")
def markdown_to_docx_format(markdown_text: str) -> str:
    """
    Converts markdown content to a single string with python-docx compatible formatting.

    :param markdown_text: The raw text containing markdown elements.
    :return: A single string with the complete text, formatted for further processing.
    """
    try:
        # Convert markdown to HTML
        html = markdown(markdown_text)
        
        # Parse HTML using BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        formatted_text = ""

        # Define mapping for header tags
        header_map = {
            'h1': ('Heading 1', 1),
            'h2': ('Heading 2', 2),
            'h3': ('Heading 3', 3),
            'h4': ('Heading 4', 4),
            'h5': ('Heading 5', 5),
            'h6': ('Heading 6', 6)
        }
        
        # Helper function to add text with possible styling
        def add_styled_text(element):
            text = ''
            if element.name == 'strong':
                text += '**' + element.text + '**'
            elif element.name == 'em':
                text += '*' + element.text + '*'
            elif element.name == 'code':
                text += '`' + element.text + '`'
            else:
                text += element.text
            return text

        # Iterate through HTML elements
        for tag in soup.contents:
            if tag.name in header_map:
                formatted_text += f"\n\n{header_map[tag.name][0]}: {tag.text.strip()}\n"
            elif tag.name == 'p':
                p_text = ''.join(add_styled_text(child) for child in tag.children)
                formatted_text += f"\n{p_text}\n"
            elif tag.name == 'ul':
                for li in tag.find_all('li'):
                    formatted_text += f"\n- {li.text.strip()}"
            elif tag.name == 'ol':
                for li in tag.find_all('li'):
                    formatted_text += f"\n1. {li.text.strip()}"
            elif tag.name == 'pre':
                code_block = tag.find('code')
                if code_block:
                    formatted_text += f"\n\n```\n{code_block.text}\n```\n"

        return formatted_text.strip()


@file_writer_agent.register_for_execution()
@file_writer_agent.register_for_llm(description="Converts markdown text to docx format and writes it to a .docx file.")
def write_markdown_to_docx(markdown_text: str, doc_path: str, save_path: Optional[str] = None) -> None:
    """
    Converts markdown text to docx format and writes it to a .docx file.

    :param markdown_text: The raw text containing markdown elements.
    :param doc_path: The path to the existing .docx file.
    :param save_path: The path to save the updated .docx file. If None, overwrites the original file.
    :return: None
    """
    try:
        # Convert markdown text to Docx-suitable format
        formatted_text = markdown_to_docx_format(markdown_text)
        
        # Load the Document
        doc = Document(doc_path)
        
        # Split the formatted text into paragraphs based on newline separators
        paragraphs = formatted_text.split('\n\n')
        
        for paragraph in paragraphs:
            if ': ' in paragraph:
                # Check for headers
                header_type, text = paragraph.split(': ', 1)
                doc.add_heading(text.strip(), level=header_type[-1])
            elif paragraph.startswith('```') and paragraph.endswith('```'):
                # Check for code blocks
                code_text = paragraph.strip('```').strip()
                doc.add_paragraph(code_text, style='Quote')
            else:
                # Handle bullet points and other text
                lines = paragraph.split('\n')
                for line in lines:
                    if line.startswith('- '):
                        doc.add_paragraph(line.strip('- '), style='List Bullet')
                    elif line.startswith('1. '):
                        doc.add_paragraph(line.strip('1. '), style='List Number')
                    else:
                        doc.add_paragraph(line)

        # Save the updated document
        if save_path is None:
            save_path = doc_path
        doc.save(save_path)
        print(f"Document updated and saved at: {save_path}")

    except Exception as e:
        print(f"An error occurred while processing the .docx file: {e}")

# # Example usage
# doc_path = ".src/result/result.docx"
# title_to_search = "Introduction"
# new_section_text = """
# This is the new content to replace the section.
# You can add multiple paragraphs as needed.
# """
# replace_section_with_text(doc_path, title_to_search, new_section_text)

# @file_writer_agent.register_for_execution()
# @file_writer_agent.register_for_llm(description="Converts markdown content to a .docx file with appropriate headers and text formatting.")
# def markdown_to_docx(markdown_text: str, doc_path: str) -> None:
#     """
#     Converts markdown content to a .docx file with appropriate headers and text formatting.

#     :param markdown_text: The raw text containing markdown elements.
#     :param doc_path: The path to save the generated .docx file.
#     :return: None
#     """
#     try:
#         # Convert markdown to HTML
#         html = markdown(markdown_text)
        
#         # Parse HTML using BeautifulSoup
#         soup = BeautifulSoup(html, 'html.parser')
        
#         # Create a new Document
#         doc = Document()
        
#         # Define mapping for header tags
#         header_map = {
#             'h1': 'Heading 1',
#             'h2': 'Heading 2',
#             'h3': 'Heading 3',
#             'h4': 'Heading 4',
#             'h5': 'Heading 5',
#             'h6': 'Heading 6'
#         }
        
#         # Helper function to add text with possible styling
#         def add_styled_text(p, element):
#             if element.name == 'strong':
#                 run = p.add_run(element.text)
#                 run.bold = True
#             elif element.name == 'em':
#                 run = p.add_run(element.text)
#                 run.italic = True
#             elif element.name == 'code':
#                 run = p.add_run(element.text)
#                 run.font.name = 'Courier New'
#             else:
#                 p.add_run(element.text)

#         # Iterate through HTML elements
#         for tag in soup.contents:
#             if tag.name in header_map:
#                 doc.add_heading(tag.text.strip(), level=int(tag.name[-1]))
#             elif tag.name == 'p':
#                 p = doc.add_paragraph()
#                 for child in tag.children:
#                     add_styled_text(p, child)
#             elif tag.name == 'ul':
#                 for li in tag.find_all('li'):
#                     doc.add_paragraph(li.text.strip(), style='List Bullet')
#             elif tag.name == 'ol':
#                 for li in tag.find_all('li'):
#                     doc.add_paragraph(li.text.strip(), style='List Number')
#             elif tag.name == 'pre':
#                 code_block = tag.find('code')
#                 if code_block:
#                     doc.add_paragraph(code_block.text, style='Code')

#         # Save the document
#         doc.save(doc_path)
#         print(f"Document saved at: {doc_path}")

#     except Exception as e:
#         print(f"An error occurred while processing the markdown text: {e}")


        
# @file_writer_agent.register_for_execution()
# @file_writer_agent.register_for_llm(description="create a docx from plain text with the right format for correctly rendering a docx")
# def create_docx_from_script(script: str, filename: str = 'result.docx', directory: str = '.src/result') -> None:
#     """
#     Creates a .docx file from a given script and saves it to the specified directory.

#     :param script: The text content to be saved in the .docx file.
#     :param filename: The name of the .docx file to be created. Default is 'result.docx'.
#     :param directory: The directory where the .docx file will be saved. Default is '.src/result'.
#     :return: None

#     Example usage
#     script_text = "
#     This is an example script that will be saved into the .docx file.
#     You can add more content here as needed.
#     "
#     create_docx_from_script(script_text)
#     """
#     # Create directory if it does not exist
#     if not os.path.exists(directory):
#         os.makedirs(directory)
    
#     # Create a new Document
#     doc = Document()
    
#     # Add the script to the document
#     doc.add_paragraph(script)
    
#     # Construct the full path
#     full_path = os.path.join(directory, filename)
    
#     # Save the document
#     doc.save(full_path)
#     print(f"Document saved at: {full_path}")


# code_executor_agent = ConversableAgent(
#     name="code_executor_agent",
#     llm_config=False,
#     code_execution_config={"executor": executor},
#     human_input_mode="ALWAYS",
#     default_auto_reply=
#     "Please continue. If everything is done, reply 'TERMINATE'.",
# )