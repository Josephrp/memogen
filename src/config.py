# ./src/config.py
from autogen import config_list_from_json
from autogen.cache import Cache
import os


llm_config = {"model": "gpt-4o", 
              "api_key": "your_api_key_here", 
              "max_tokens": 4000 , # change this according to your needs
              "temperature": 0.7, #change this according to your needs
    }


filter_criteria = {"model": ["gptonic"]}
### AZURE 
# llm_config =     {
#         "model": "your_deployment_name_here", # mine is "tonicgpt"
#         "api_key": "your_api_key_here",
#         "base_url": "your_deployment_endpoint_here", # https://eastus2.api.cognitive.microsoft.com/
#         "api_type": "azure",
#         "api_version": "your_api_version_herre", # eg "2024-02-01" for gpt-4o
#         "max_tokens": 1800 ,# change this according to your needs
#         "temperature": 0.7, #change this according to your needs
#    }
