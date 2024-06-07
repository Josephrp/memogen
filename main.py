# src/main.py

import autogen
from src.agents_writer import file_writer_agent, layman_reviewer, financial_reviewer, quality_reviewer , outliner,  meta_reviewer, critic, writer
from src.agents_docx import docx_planner, docx_planner_user, docx_file_writer_agent, docx_user_proxy, process_markdown_files_in_directory
from src.agents_markdown import markdown_assistant, markdown_file_writer_agent, markdown_planner, markdown_planner_user, parse_markdown, read_markdown_file_to_text, write_text_to_markdown
from src.agents_planner import overall_assistant, overall_planner, overall_planner_user, overall_user_proxy
from src.config import load_env_file
from autogen.graph_utils import visualize_speaker_transitions_dict
from autogen.agentchat.groupchat import GroupChat
import logging
load_env_file('/.env')

# chroma_client = chromadb.HttpClient(host='localhost', port=8000)


class AutoMemoProduction:
    def __init__(self, topic, audience):
        logging.info(f"Initializing AgentManager for topic: {topic}")
        self.topic = topic
        self.audience = audience

    def create_outline(self):
        outliner.initiate_chat(
            writer.name,
            message=f"Create an outline for a memo on the topic: {self.topic} for the audience: {self.audience}.",
        )
        outline = outliner.last_message().get("content", "")
        logging.info(f"Outline created: {outline}")
        return outline

    def parse_outline_to_markdown_chunks(self, outline_str):
        filenames = parse_markdown(outline_str)
        logging.info(f"Parsed markdown files: {filenames}")
        return filenames

    def write_sections(self, markdown_filenames):
        for filename in markdown_filenames:
            file_content = read_markdown_file_to_text(filename)
            writer.initiate_chat(
                file_writer_agent.name,
                message=f"Write a detailed section based on the following outline:\n{file_content}",
            )
            result = writer.last_message().get("content", "")
            write_text_to_markdown(result, filename)
            logging.info(f"Completed writing section for {filename}")

    def combine_sections_to_docx(self, markdown_directory, docx_path):
        process_markdown_files_in_directory(markdown_directory, docx_path)
        logging.info(f"Combined markdown sections into docx: {docx_path}")

    def run(self):
        outline = self.create_outline()
        markdown_filenames = self.parse_outline_to_markdown_chunks(outline)
        self.write_sections(markdown_filenames)
        self.combine_sections_to_docx("./src/result/intermediate_results", "./src/result/final_memo.docx")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    topic = "Artificial Intelligence in Modern Healthcare"
    audience = "Healthcare Professionals and Administrators"

    producer = AutoMemoProduction(topic=topic, audience=audience)
    producer.run()


