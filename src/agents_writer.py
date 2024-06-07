from autogen import AssistantAgent
from autogen.cache import Cache
from autogen.agentchat.contrib.math_user_proxy_agent  import MathUserProxyAgent
from src.config import llm_config
import os

from src.prompts import  writer_system_message, critic_system_message, financial_reviewer_system_message, outliner_system_message, quality_system_message, layman_system_message

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

# --------  Tools

# @file_writer_agent.register_for_execution()
# @file_writer_agent.register_for_llm(description="Writes a text string to a markdown file")
# def write_text_to_markdown(text, file_name, directory='./src/result/intermediate_results'):
#     """
#     Writes a text string to a markdown file, ensuring the directory exists.

#     Args:
#         text (str): The raw text content to be written to the markdown file.
#         file_name (str): The name of the markdown file.
#         directory (str): The directory where the markdown file will be saved. Default is './output_folder'.
#     """
#     # Ensure the directory exists
#     os.makedirs(directory, exist_ok=True)
    
#     # Full path to the markdown file
#     file_path = os.path.join(directory, file_name)
    
#     # Write the text content to the markdown file
#     with open(file_path, 'w', encoding='utf-8') as file:
#         file.write(text)
    
#     print(f'Text has been written to {file_path}')

# @file_writer_agent.register_for_execution()
# @file_writer_agent.register_for_llm(description="Parses a markdown string into several markdown strings divided by titles, then saves each text string as a separate markdown document in a folder.")
# def parse_markdown(markdown_str, output_folder="./src/result/intermediate_results"):
#     """
#     Parses a markdown string into several markdown strings divided by titles,
#     then saves each text string as a separate markdown document in a folder.

#     Args:
#         markdown_str (str): The markdown content as a string.
#         output_folder (str): The folder to save the numbered markdown files.

#     Returns:
#         List of filenames of the created markdown documents.
#     """
#     # Regex pattern to match markdown titles (assuming titles start with #)
#     title_pattern = re.compile(r'(#+\s.*\n)')
    
#     # Find all titles and their start positions
#     matches = list(title_pattern.finditer(markdown_str))
    
#     # Ensure the output folder exists
#     os.makedirs(output_folder, exist_ok=True)
    
#     filenames = []
    
#     # Iterate over the matches and extract content
#     for i in range(len(matches)):
#         start_pos = matches[i].start()
#         end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(markdown_str)
        
#         section_str = markdown_str[start_pos:end_pos]
        
#         # Write the section to a separate markdown file
#         filename = os.path.join(output_folder, f'section_{i + 1}.md')
#         with open(filename, 'w', encoding='utf-8') as f:
#             f.write(section_str)
        
#         filenames.append(filename)
    
#     return filenames

# @file_writer_agent.register_for_execution()
# @file_writer_agent.register_for_llm(description="Reads a markdown file and returns its raw text content.")
# def read_markdown_file_to_text(file_path):
#     """
#     Reads a markdown file and returns its raw text content.

#     Args:
#         file_path (str): The path to the markdown file.

#     Returns:
#         str: The raw text content extracted from the markdown file.
#     """
#     # Read the markdown file
#     with open(file_path, 'r', encoding='utf-8') as file:
#         markdown_string = file.read()

#     # Convert markdown to HTML
#     html = markdown.markdown(markdown_string)
    
#     # Use BeautifulSoup to extract text from HTML
#     soup = BeautifulSoup(html, 'html.parser')
#     text = soup.get_text()
    
#     return text

# def replace_specific_text_in_markdown(file_name: str, old_text: str, new_text: str , markdown_directory: str = "./src/result/intermediate_results"):
#     """
#     Opens a markdown file from a directory, replaces specified text, and saves/overrides the file.

#     Args:
#         markdown_directory (str): The directory containing the markdown file.
#         file_name (str): The name of the markdown file to be modified.
#         old_text (str): The text to search for and replace in the markdown file.
#         new_text (str): The text to replace the old text with in the markdown file.
    
#     Returns:
#         None
#     """
#     # Construct the full file path
#     file_path = os.path.join(markdown_directory, file_name)
    
#     # Ensure the file exists in the specified directory
#     if not os.path.isfile(file_path):
#         raise ValueError(f"The specified markdown file does not exist: {file_path}")

#     # Read the content of the markdown file
#     with open(file_path, 'r', encoding='utf-8') as file:
#         content = file.read()

#     # Replace the specified text
#     updated_content = content.replace(old_text, new_text)

#     # Save the updated content back to the same file, overriding it
#     with open(file_path, 'w', encoding='utf-8') as file:
#         file.write(updated_content)

#     print(f"Replaced text in {file_path} and saved the updated file.")

# def replace_all_text_in_markdown(markdown_directory: str, file_name: str, new_text: str):
#     """
#     Opens a markdown file from a directory, replaces all text with new text, and saves/overrides the file.

#     Args:
#         markdown_directory (str): The directory containing the markdown file.
#         file_name (str): The name of the markdown file to be modified.
#         new_text (str): The new text to replace the existing content in the markdown file.
    
#     Returns:
#         None
#     """
#     # Construct the full file path
#     file_path = os.path.join(markdown_directory, file_name)
    
#     # Ensure the file exists in the specified directory
#     if not os.path.isfile(file_path):
#         raise ValueError(f"The specified markdown file does not exist: {file_path}")

#     # Save the new content to the same file, overriding it
#     with open(file_path, 'w', encoding='utf-8') as file:
#         file.write(new_text)

#     print(f"Replaced all text in {file_path} and saved the updated file.")

# def replace_section_in_markdown(file_name: str, title: str, new_text: str, markdown_directory: str = ".src/result/intermediate_results"):
#     """
#     Opens a markdown file from a directory, finds a given title, and replaces all text
#     until the next title or subtitle with the text provided, then saves/overrides the file.

#     Args:
#         markdown_directory (str): The directory containing the markdown file.
#         file_name (str): The name of the markdown file to be modified.
#         title (str): The title of the section to replace.
#         new_text (str): The new text to replace the existing content in the section.
    
#     Returns:
#         None
#     """
#     # Construct the full file path
#     file_path = os.path.join(markdown_directory, file_name)
    
#     # Ensure the file exists in the specified directory
#     if not os.path.isfile(file_path):
#         raise ValueError(f"The specified markdown file does not exist: {file_path}")
    
#     # Read the content of the markdown file
#     with open(file_path, 'r', encoding='utf-8') as file:
#         content = file.read()

#     # Create a regex pattern to find the title and the subsequent content
#     title_pattern = re.compile(r'^(#+\s+' + re.escape(title) + r'\s*\n)', re.MULTILINE)
#     match = title_pattern.search(content)
    
#     if not match:
#         raise ValueError(f"Title '{title}' not found in the markdown file.")
    
#     # Find the start and end positions of the section to replace
#     start_pos = match.start()
#     end_pos = len(content)
    
#     next_title_pattern = re.compile(r'^#+\s+', re.MULTILINE)
#     next_match = next_title_pattern.search(content, pos=match.end())
    
#     if next_match:
#         end_pos = next_match.start()
    
#     # Create the new content by replacing the old section with the new text
#     new_content = content[:match.end()] + new_text + content[end_pos:]
    
#     # Save the updated content back to the same file, overriding it
#     with open(file_path, 'w', encoding='utf-8') as file:
#         file.write(new_content)

#     print(f"Section under title '{title}' replaced and file saved at {file_path}.")
