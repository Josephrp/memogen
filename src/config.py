# ./src/config.py

from autogen.cache import Cache

llm_config = {"model": "gpt-4-turbo", "api_key": "sk-proj-Zb3QBEwIi9lsjWRWrfJPT3BlbkFJMZnaXZDAvolaJHG2n5J2" }

import os

def load_env_file(env_path):
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value