## Installation


### Pre-Installation : Run Docker

- install and run `Docker` if it's not already there on startup by [following these instructions](https://docs.docker.com/engine/install/)

- add your user to the `Docker` user group by running this command :
  - on Windows : 
    - `net localgroup docker-users "your-user-id" /ADD`
      your-user-id is your local Windows user name. You can determine this by looking at the folder name under C:\Users\ .
  - on Linux : 
    - [follow these instructions](https://docs.docker.com/engine/install/linux-postinstall/)

### Pre-Installation : Install Poetry

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


### Installation Instructions

>> 🌟STAR and 🍴FORK this Repository, then follow the instructions below exactly.

1. **Clone the Repository**

   Clone the repository to a local machine:

   ```sh
   git clone https://github.com/Josephrp/AutoFinMemo
   cd AutoFinMemo
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


### Troubleshooting

If you encounter any issues during installation, refer to the [Poetry documentation](https://python-poetry.org/docs/#installation) for detailed guidance and troubleshooting tips.

2. **Adding Poetry to Your Path**:

   You might need to add Poetry to your PATH. The installation script should provide instructions on how to do this. Typically, you might need to add the following line to your shell configuration file (e.g., `.bashrc`, `.zshrc`):

   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

   After adding the above line, reload your shell configuration:

   ```bash
   source ~/.bashrc  # or `source ~/.zshrc` depending on your shell
   ```
