# MemoGen  

MemoGen is an advanced application that allows users to generate high-quality memos of various types through a fully automated process. Utilizing state-of-the-art AI-driven components, MemoGen handles the writing, outlining, and reviewing of memos. The final output is a detailed and well-structured document in DOCX format.  

## Features

- **Automated Memo Creation:** Generates memos with minimal user input.  
- **Multi-Agent Review System:** Ensures quality through multiple AI reviewers.  
- **Supports Various Memo Types:** Accounting, Financial, Technical, Policy, and more.  
- **DOCX Output:** Final document is saved in a widely used format.  
- **Self-Reflection:** Built-in quality control mechanisms for continuous improvement.  
- **MIT Licensed:** Open and accessible for modification.  

## How It Works  

MemoGen uses a combination of language models and AI-driven review agents to produce high-quality memos. Here's an overview of the process:  

1. **User Input:** The user provides the topic, audience, and type of memo.  
2. **Outline Creation:** An outline for the memo is generated based on the provided inputs.  
3. **Section Writing:** Each section of the memo is written with the help of multiple AI agents.  
4. **Review and Reflection:** The content goes through a review process by different reviewers, ensuring the final output is polished and accurate.  
5. **Document Compilation:** The individual sections are combined into a final DOCX document, ready for download.  

## How to Use  

- [Join our Discord Community](https://discord.gg/zDFhhGZrcz)  !

## How to Use

### Running MemoGen
When you start MemoGen, you will be prompted with three questions:  

1. **Enter the topic for the memo:**  
   - In this question, it's worthwhile to input a long, context-rich topic. Several lines or even paragraphs of detailed information will help the AI generate an accurate memo.  

2. **Enter the audience for the memo:**  
   - Here, you can be concise but descriptive. Providing specific details about the audience will help tailor the memo appropriately.  
3. **Enter the type of memo:**  
   - A single word or a few words describing the type of memo (e.g., "Accounting", "Technical") is sufficient.  

After providing the necessary inputs, press Enter. Once the process is complete, your long-form memo will be available in `./src/result/result.docx`. This document is your final memo in DOCX format.

### Installation

#### Pre-Installation : Run Docker

- install and run `Docker` if it's not already there on startup by [following these instructions](https://docs.docker.com/engine/install/)

- add your user to the `Docker` user group by running this command :
  - on Windows :
    - `net localgroup docker-users "your-user-id" /ADD`
      your-user-id is your local Windows user name. You can determine this by looking at the folder name under C:\Users\ .
  - on Linux :
    - [follow these instructions](https://docs.docker.com/engine/install/linux-postinstall/)

#### Pre-Installation : Install Poetry

you'll need to install Poetry. Poetry is a tool for dependency management and packaging in Python. It ensures that you have a consistent environment across different setups.

1. **Using the Official Installer**:

   Open your terminal and run the following command:

  - On Windows :

   ```bash
   curl -sSL https://install.python-poetry.org | python -
   ```

  - On MacOS/Linux :

   ```bash
   curl -sSL https://install.python-poetry.org | python3 - 
   ```

1. **Clone the Repository**

   Clone the repository to a local machine:

   ```sh
   git clone https://github.com/Josephrp/memogen
   cd memogen
   ```

2. **Set your OpenAI API Key**

currently we're providing two ways to plug in your llm:

**Using Open AI :**
    - edit the `./src/config/config.py` file using a text editor and replace your api_key_here with your api key (keep the quotes!)

`llm_config = {"model": "gpt-4-turbo", "api_key": "your_api_key_here" }`

**Using Azure:**
    - edit the `./src/OAI_CONFIG_LIST.json.example` file using a text editor and save it as `OAI_CONFIG_LIST.json` (without the `.example`at the end !)

```json
[
    {
        "model": "deployment_name",
        "api_key": "your_api_key_here",
        "base_url": "https://eastus2.api.cognitive.microsoft.com/",
        "api_type": "azure",
        "api_version": "2024-02-01"
    }
]
```

**In both cases:**
    - make sure you ["comment out"](https://www.datacamp.com/tutorial/python-block-comment) the method you are **not** using in `./src/config/config.py` !

3. **Install and Run**

   - On the command line :

      ```sh
      poetry install
      ```

      then :

      ```sh
      poetry run python main.py
      ```

#### Troubleshooting

If you encounter any issues during installation, refer to the [Poetry documentation](https://python-poetry.org/docs/#installation) for detailed guidance and troubleshooting tips.

1. **Adding Poetry to Your Path**:

   You might need to add Poetry to your PATH. The installation script should provide instructions on how to do this. Typically, you might need to add the following line to your shell configuration file (e.g., `.bashrc`, `.zshrc`):

   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

   After adding the above line, reload your shell configuration:

   ```bash
   source ~/.bashrc  # or `source ~/.zshrc` depending on your shell
   ```

## Contributing  

Thank you for considering contributing to MemoGen! We welcome all types of contributions, whether it's bug reports, feature suggestions, or code improvements.  
  
### How to Contribute

1. **Fork the Repository:**  
   - Navigate to our GitLab repository: [MemoGen on GitLab](https://git.tonic-ai.com/positonic/memogen/memogen).  
   - Click on the "Fork" button to create your own copy of the repository.  
   - Please read the [CONTRIBUTING.md](CONTRIBUTING.md) and our our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) and the process for submitting pull/merge requests.

## Project Structure  

```
memogen/  
├── src/  
│   ├── agents_writer.py  
│   ├── config/  
│   │   └── llm_config.py  
│   ├── main.py  
│   ├── prompts.py  
│   ├── result/  
│   │   └── intermediate_results/  
│   ├── utils.py  
└── requirements.txt  
```

### Acknowledgements  

We would like to acknowledge the use of the following tools and libraries:  

- [AutoGen](https://github.com/microsoft/autogen)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/)
- [.docx](https://github.com/python-openxml/python-docx)

### Join Our Community  

We invite all contributors to join our builder's community on Discord! It's a great place to introduce yourself, share what you're working on, and get involved in exciting new projects. Whether you're a seasoned developer or just starting out, our community is here to help.  

- **Discord Link:** [Join our Discord Community](https://discord.gg/zDFhhGZrcz)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details.  

By using MemoGen, you agree to the terms specified in the MIT License. Enjoy your automated memo creation experience!
