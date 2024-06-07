# ./src/config.py
from autogen import config_list_from_json
from autogen.cache import Cache
import os


def load_env_file(env_path):
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

load_env_file('./.env')
# llm_config = {"model": "gpt-4o", "api_key": "sk-proj-Zb3QBEwIi9lsjWRWrfJPT3BlbkFJMZnaXZDAvolaJHG2n5J2", "max_tokens": 4000 }

## AZURE 
filter_criteria = {"model": ["gptonic"]}

llm_config =     {
        "model": "gptonic",
        "api_key": "b140d810af0640d6a3b337c8b9d6522d",
        "base_url": "https://eastus2.api.cognitive.microsoft.com/",
        "api_type": "azure",
        "api_version": "2024-02-01"
    }
