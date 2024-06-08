# ./src/config.py
from autogen import config_list_from_json
from autogen.cache import Cache
import os


# llm_config = {"model": "gpt-4o", "api_key": "your_api_key_here", "max_tokens": 4000 }

## AZURE 
filter_criteria = {"model": ["gptonic"]}

llm_config =     {
        "model": "your_deployment_name", # mine is "tonicgpt"
        "api_key": "your_api_key_here",
        "base_url": "your_url_here", # https://eastus2.api.cognitive.microsoft.com/
        "api_type": "azure",
        "api_version": "date_version", # eg "2024-02-01" for gpt-4o
        "max_tokens": 1600 # change this according to your needs
    }
