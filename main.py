# src/main.py

import autogen
from autogen import GroupChat, GroupChatManager
from src.agents_writer import layman_reviewer, financial_reviewer, quality_reviewer , outliner,  meta_reviewer, critic, writer
from src.utils import parse_markdown, process_markdown_files_in_directory, read_markdown_file_to_text, write_text_to_markdown
from autogen import initiate_chats
from autogen.cache import Cache
from src.config import llm_config
import logging
import os
import re
from autogen.agentchat.conversable_agent import initiate_chats
# ---------- Init


# load_env_file('/.env')

# chroma_client = chromadb.HttpClient(host='localhost', port=8000)

topic = ""
audience = ""
memo_type = ""


# --------- User Input

def get_user_inputs():
    """Prompt and get inputs from the user for topic, audience, and type of memo with clear instructions."""
    print("Welcome to the Memo Production System. Please provide the following information:")

    topic = input("1. Enter the topic for the memo (e.g., Artificial Intelligence in Modern Healthcare, Accounting Memo To Explain the Benefits of Going Public): ")

    audience = input("2. Enter the audience for the memo (e.g., Healthcare Professionals and Administrators): ")

    memo_type = input("3. Enter the type of memo (e.g., Accounting, Financial, Technical, Policy...): ")

    print("\nThank you! Creating the memo based on the provided details...\n")

    return topic, audience, memo_type

# --------- Agents 

from autogen import AssistantAgent
from src.prompts import get_system_messages
from src.config import llm_config
import os

# Fetch all system messages using the appropriate function
messages = get_system_messages(audience="general", memo_type="General")
# -------- Writer

writer = AssistantAgent(
    name="Writer",
    system_message=messages["writer_system_message"],
    llm_config=llm_config,
)

outliner = AssistantAgent(
    name="Writer",
    system_message=messages["outliner_system_message"],
    llm_config=llm_config,
)

# -------- Reviewers

critic = AssistantAgent(
    name="Critic",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    llm_config=llm_config,
    system_message=messages["critic_system_message"],
)

layman_reviewer = AssistantAgent(
    name="Layman Reviewer",
    description="A reviewer that makes sure a laywoman would fully understand the content provided to her.",
    llm_config=llm_config,
    system_message=messages["layman_system_message"],
)

financial_reviewer = AssistantAgent(
    name="Financial Reviewer",
    description='A reviewer that makes sure financial justification are credible',
    llm_config=llm_config,
    system_message=messages["financial_reviewer_system_message"],
)

quality_reviewer = AssistantAgent(
    name="Quality Assurance Reviewer",
    description="a reviewer that makes sure that claims are well justified",
    llm_config=llm_config,
    system_message=messages["quality_system_message"],
)

meta_reviewer = AssistantAgent(
    name="Meta Reviewer",
    llm_config=llm_config,
    system_message="You are a meta reviewer, you aggragate and review "
    "the work of other reviewers and give a final suggestion on the content.",
)


# --------- Main Application Logic

def reflection_message(recipient, messages, sender, config):
    return f'''Review the following content. \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}'''

review_chats = [
    {
     "recipient": layman_reviewer,
     "message": reflection_message,
     "summary_method": "reflection_with_llm",
     "summary_args": {"summary_prompt" :
        "Return review into as JSON object only:"
        "{'Reviewer': '', 'Review': ''}. Here Reviewer should be your role",},
     "max_turns": 1},
    {
    "recipient": financial_reviewer, "message": reflection_message,
     "summary_method": "reflection_with_llm",
     "summary_args": {"summary_prompt" :
        "Return review into as JSON object only:"
        "{'Reviewer': '', 'Review': ''}.",},
     "max_turns": 1},
    {"recipient": quality_reviewer, "message": reflection_message,
     "summary_method": "reflection_with_llm",
     "summary_args": {"summary_prompt" :
        "Return review into as JSON object only:"
        "{'reviewer': '', 'review': ''}",},
     "max_turns": 1},
     {"recipient": meta_reviewer,
      "message": "Aggregrate feedback from all reviewers and give final suggestions on the writing.",
     "max_turns": 1},
]

critic.register_nested_chats(
    review_chats,
    trigger=writer,
)


class AutoMemoProduction:
    def __init__(self, topic, audience, memo_type):
        logging.info(f"Initializing AgentManager")
        self.topic = topic
        self.audience = audience
        self.memo_type = memo_type

    def create_outline(self):
        message=f"Create an outline for a {self.memo_type} memo on the topic {self.topic} optimized for the audience: {self.audience}."
        outline =outliner.generate_reply(messages=[{"content": message, "role": "user"}])
        logging.info(f"Outline created: {outline}")
        return outline

    def parse_outline_to_markdown_chunks(self, outline_str):
        filenames = parse_markdown(outline_str)
        logging.info(f"Parsed markdown files: {filenames}")
        return filenames

    def write_sections(self, markdown_filenames):  
        def custom_speaker_selection_func(last_speaker, groupchat):  
            messages = groupchat.messages  
            if len(messages) <= 1:  
                return writer  
            if last_speaker is writer:  
                return critic  
            if last_speaker in [layman_reviewer, financial_reviewer, quality_reviewer, meta_reviewer]:  
                return critic if last_speaker != meta_reviewer else writer  
            if last_speaker is critic:  
                return "random" if len(messages) < 3 else meta_reviewer  
            else:  
                return "random"  
    
        # for filename in markdown_filenames:  
        for index, filename in enumerate(markdown_filenames):  
            current_content = read_markdown_file_to_text(filename)  
            
            # Read previous section  
            previous_content = ""  
            if index > 0:  
                previous_filename = markdown_filenames[index - 1]  
                previous_content = read_markdown_file_to_text(previous_filename)  
            
            # Read next section  
            next_content = ""  
            if index < len(markdown_filenames) - 1:  
                next_filename = markdown_filenames[index + 1]  
                next_content = read_markdown_file_to_text(next_filename)  
            
            # Construct message based on position in the list  
            if index == 0:  
                # First section  
                message = (  
                    f"NEXT SECTION:\n\n"  
                    f"{next_content}\n\n"
                    f"---\n\n"   
                    f"FOCUS SECTION :\n\n"  
                    f"{current_content}\n\n"    
                    f"Produce a simple and short introduction for this {self.memo_type} memo on the topic of {self.topic} optimized for {self.audience} provided above:"  
                )  
            elif index == len(markdown_filenames) - 1:  
                # Last section  
                message = (  
                    f"PREVIOUS SECTION:\n\n"  
                    f"{previous_content}\n\n"  
                    f"---\n\n"  
                    f"FOCUS SECTION :\n\n"  
                    f"{current_content}\n\n"  
                    f"Produce a detailed section based on the section of {self.memo_type} memo on the topic of {self.topic} optimized for {self.audience} provided above:"  
                )  
            else:  
                # Middle sections  
                message = (
                    f"PREVIOUS SECTION:\n\n"    
                    f"{previous_content}\n\n"  
                    f"---\n\n"
                    f"NEXT SECTION:\n\n"  
                    f"{next_content}\n\n"  
                    f"---\n\n"  
                    f"FOCUS SECTION :\n\n"    
                    f"{current_content}\n\n"  
                    f"---\n\n"  
                    f"Produce a detailed section based on the section of {self.memo_type} memo on the topic of {self.topic} optimized for {self.audience} provided above:"  
                )  
                      
            # Initialize GroupChat  
            groupchat = GroupChat(  
                agents=[writer, critic, layman_reviewer, financial_reviewer, quality_reviewer, meta_reviewer],  
                messages=[],  
                max_round=2,  
                speaker_selection_method=custom_speaker_selection_func,  
            )  
            
            manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)  
            # Start chat with writer  
            result = writer.initiate_chat(manager, message=message)  
            final_message = manager.chat_messages[writer][-1]['content']
            write_text_to_markdown(final_message, filename)  

            # try:  
            #     # Access the chat history and find the last message from 'Writer'  
            #     chat_history = result.chat_history 
            #     if chat_history:  
            #         last_message = None  
            #         for entry in reversed(chat_history):  
            #             if entry.get("role") == writer.name:  
            #                 last_message = entry.get("content")  
            #                 break  
                    
            #         if last_message:  
            #             write_text_to_markdown(last_message, filename)  
            #             logging.info(f"Completed writing section for {filename}")  
            #         else:  
            #             logging.error(f"No message from  {writer.name} found in chat history for {filename}")  
            #     else:  
            #         logging.error(f"No chat history found in result for {filename}")  
            # except Exception as e:  
            #     logging.error(f"Failed to process chat result for {filename}: {e}")  
            # write_text_to_markdown(result['sender':'Writer']['response'], filename)  
            # logging.info(f"Completed writing section for {filename}")  
    

    def combine_sections_to_docx(self, markdown_directory, docx_path):
        process_markdown_files_in_directory(markdown_directory, docx_path)
        logging.info(f"Combined markdown sections into docx: {docx_path}")

    def run(self):
        outline = self.create_outline()
        markdown_filenames = self.parse_outline_to_markdown_chunks(outline)
        self.write_sections(markdown_filenames)
        self.combine_sections_to_docx("./src/result/intermediate_results", "./src/result/result.docx")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    topic, audience, memo_type = get_user_inputs()
    producer = AutoMemoProduction(topic=topic, audience=audience, memo_type=memo_type)
    producer.run()


