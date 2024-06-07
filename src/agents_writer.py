# src/agents_writer.py

from autogen import AssistantAgent
from autogen.cache import Cache
# from autogen.agentchat.contrib.math_user_proxy_agent  import MathUserProxyAgent
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




# # --------  Math


# mathproxyagent = MathUserProxyAgent(
#     name="mathproxyagent",
#     human_input_mode="NEVER",
#     code_execution_config={"use_docker": False},
# )