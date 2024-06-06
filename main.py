import autogen
from src.agents import file_writer_agent, layman_reviewer, financial_reviewer, quality_reviewer , outliner,  meta_reviewer, critic, writer, planner_user, planner, user_proxy
from src.config import load_env_file
from autogen.graph_utils import visualize_speaker_transitions_dict

load_env_file('/.env')

# chroma_client = chromadb.HttpClient(host='localhost', port=8000)



def reflection_message(recipient, messages, sender, config):
    return f'''Review the following content.
            \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}'''

review_chats = [
    {
     "recipient": layman_reviewer,
     "message": reflection_message,
     "summary_method": "reflection_with_llm",
     "summary_args": {"summary_prompt" :
        "Return review into as JSON object only:"
        "{'Reviewer': '', 'Review': ''}. Here Reviewer should be your role",},
     "max_turns": 1},
    {
    "recipient": financial_reviewer, "message": reflection_message,
     "summary_method": "reflection_with_llm",
     "summary_args": {"summary_prompt" :
        "Return review into as JSON object only:"
        "{'Reviewer': '', 'Review': ''}.",},
     "max_turns": 1},
    {"recipient": quality_reviewer, "message": reflection_message,
     "summary_method": "reflection_with_llm",
     "summary_args": {"summary_prompt" :
        "Return review into as JSON object only:"
        "{'reviewer': '', 'review': ''}",},
     "max_turns": 1},
     {"recipient": meta_reviewer,
      "message": "Aggregrate feedback from all reviewers and give final suggestions on the writing.",
     "max_turns": 1},
]

critic.register_nested_chats(
    review_chats,
    trigger=writer,
)


res = critic.initiate_chat(
    recipient=writer,
    message=task,
    max_turns=4,
    summary_method="last_msg"
)

# the assistant receives a message from the user, which contains the task description
user_proxy.initiate_chat(
    assistant,
    message="""Suggest a fix to an open good first issue of flaml""",
)

# print(res.summary)
