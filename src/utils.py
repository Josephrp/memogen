# /src/utils.py Tools

from markdown2 import markdown
from bs4 import BeautifulSoup
from docx import Document  
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_LINE_SPACING, WD_BREAK  
from docx.shared import Pt, Inches  
from docx.oxml.ns import qn  
from docx.oxml import OxmlElement  
from docx.enum.style import WD_STYLE_TYPE  
from docx.text.paragraph import Paragraph
from typing import Optional,  Dict, List, Tuple
import re
import os
import json


def ensure_styles(doc: Document):  
    """Ensure the necessary styles exist in the document."""  
    styles = doc.styles  
  
    if 'List Bullet' not in styles:  
        style = styles.add_style('List Bullet', WD_STYLE_TYPE.PARAGRAPH)  
        style.font.name = 'Arial'  
        style.font.size = Pt(11)  
      
    if 'List Number' not in styles:  
        style = styles.add_style('List Number', WD_STYLE_TYPE.PARAGRAPH)  
        style.font.name = 'Arial'  
        style.font.size = Pt(11)  
      
    # Add more styles as needed  
    return doc  

def write_text_to_markdown(text, file_name, directory='./src/result/intermediate_results'):
    """
    Writes a text string to a markdown file, ensuring the directory exists.

    Args:
        text (str): The raw text content to be written to the markdown file.
        file_name (str): The name of the markdown file.
        directory (str): The directory where the markdown file will be saved. Default is './output_folder'.
    """
    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)
    
      
    # Ensure the file_name does not contain any path segments  
    file_name = os.path.basename(file_name)  
  
    # Full path to the markdown file
    file_path = os.path.join(directory, file_name)

    # Convert text to string if it's a dictionary or list  
    if isinstance(text, dict):  
        text = json.dumps(text, indent=4)  # Pretty-print the JSON with indentation  
    elif isinstance(text, list):  
        text = '\n'.join(text)  # Convert list to a string with each element on a new line  
  
    # Write the text content to the markdown file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)
    
    print(f'Text has been written to {file_path}')

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
    except Exception as e:  
        print(f"An error occurred while converting markdown to docx format: {e}")  
        return ""  

def process_markdown_files_in_directory(markdown_directory: str = "./src/result/intermediate_results", docx_save_path: str = "./src/result/result.docx"):  
    """  
    Iterates over each markdown file in a directory and writes them to a .docx file.  
    Args:  
        markdown_directory (str): The directory containing markdown files.  
        docx_save_path (str): The path to save the combined .docx file.  
    Returns:  
        None  
    """  
    # Ensure the markdown directory exists  
    if not os.path.isdir(markdown_directory):  
        raise ValueError(f"The specified directory does not exist: {markdown_directory}")  
    # Create a new Document or load an existing one  
    if os.path.exists(docx_save_path):  
        doc = Document(docx_save_path)  
    else:  
        doc = Document()  
    # Iterate over each markdown file in the directory  
    for filename in os.listdir(markdown_directory):  
        if filename.endswith('.md'):  
            filepath = os.path.join(markdown_directory, filename)  
            # Read the markdown file content  
            with open(filepath, 'r', encoding='utf-8') as file:  
                markdown_text = file.read()  
            # Convert markdown text to docx format and append it to the document  
            formatted_text = markdown_to_docx_format(markdown_text)  
            paragraphs = formatted_text.split('\n\n')  
            for paragraph in paragraphs:  
                if ': ' in paragraph:  
                    try:  
                        # Check for headers  
                        header_type, text = paragraph.split(': ', 1)  
                        level = int(''.join(filter(str.isdigit, header_type)))  
                        doc.add_heading(text.strip(), level=level)  
                    except ValueError as ve:  
                        print(f"Header parsing error: {ve}, Paragraph: {paragraph}")  
                        doc.add_paragraph(paragraph)  
                elif paragraph.startswith('```') and paragraph.endswith('```'):  
                    # Check for code blocks  
                    code_text = paragraph.strip('```').strip()  
                    doc.add_paragraph(code_text, style='Quote')  
                else:  
                    # Handle bullet points and other text  
                    lines = paragraph.split('\n')  
                    for line in lines:  
                        if line.startswith('- '):  
                            doc.add_paragraph(line.strip('- '))  
                        elif line.startswith('1. '):  
                            doc.add_paragraph(line.strip('1. '))  
                        else:  
                            doc.add_paragraph(line)  
  
    # Save the combined document  
    doc.save(docx_save_path)  
    print(f"Combined document saved at: {docx_save_path}")  

def parse_markdown(markdown_str, output_folder="./src/result/intermediate_results"):
    """
    Parses a markdown string into several markdown strings divided by titles,
    then saves each text string as a separate markdown document in a folder.

    Args:
        markdown_str (str): The markdown content as a string.
        output_folder (str): The folder to save the numbered markdown files.

    Returns:
        List of filenames of the created markdown documents.
    """
    # Regex pattern to match markdown titles (assuming titles start with #)
    title_pattern = re.compile(r'(#+\s.*\n)')
    
    # Find all titles and their start positions
    matches = list(title_pattern.finditer(markdown_str))
    
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    filenames = []
    
    # Iterate over the matches and extract content
    for i in range(len(matches)):
        start_pos = matches[i].start()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(markdown_str)
        
        section_str = markdown_str[start_pos:end_pos]
        
        # Write the section to a separate markdown file
        filename = os.path.join(output_folder, f'section_{i + 1}.md')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(section_str)
        
        filenames.append(filename)
    
    return filenames

def read_markdown_file_to_text(file_path):
    """
    Reads a markdown file and returns its raw text content.

    Args:
        file_path (str): The path to the markdown file.

    Returns:
        str: The raw text content extracted from the markdown file.
    """
    # Read the markdown file
    with open(file_path, 'r', encoding='utf-8') as file:
        markdown_string = file.read()

    # Convert markdown to HTML
    html = markdown(markdown_string)
    
    # Use BeautifulSoup to extract text from HTML
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    
    return text
