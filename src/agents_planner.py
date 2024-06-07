# src/agents_planner.py

from autogen import AssistantAgent, UserProxyAgent
from src.config import llm_config
from src.prompts import overall_planner_system_message


# --------  Planner

overall_planner = AssistantAgent(
    name="overall_planner",
    llm_config=llm_config,
    # the default system message of the AssistantAgent is overwritten here
    system_message=overall_planner_system_message,
)

overall_planner_user = UserProxyAgent(
    name="overall_planner_user",
    max_consecutive_auto_reply=0,  # terminate without auto-reply
    human_input_mode="NEVER",
    code_execution_config={
        "use_docker": True
    }, 
)

def overall_task_planner(message):
    overall_planner_user.initiate_chat(overall_planner, message=message)
    # return the last message received from the planner
    return overall_planner_user.last_message()["content"]

overall_assistant = AssistantAgent(
    name="assistant",
    llm_config={
        "temperature": 0,
        "timeout": 600,
        "cache_seed": 42,
        "config_list": llm_config,
        "functions": [
            {
                "name": "overall_task_planner",
                "description": "ask planner to: 1. get a plan for finishing a task, 2. verify the execution result of the plan and potentially suggest new plan.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "question to ask planner. Make sure the question include enough context, such as the code and the execution result. The planner does not know the conversation between you and the user, unless you share the conversation with the planner.",
                        },
                    },
                    "required": ["message"],
                },
            },
        ],
    },
)

# create a UserProxyAgent instance named "user_proxy"
overall_user_proxy = UserProxyAgent(
    name="overall_user_proxy",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    # is_termination_msg=lambda x: "content" in x and x["content"] is not None and x["content"].rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "./src/codex",
        "use_docker": True,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
    function_map={"overall_task_planner": overall_task_planner},
)
