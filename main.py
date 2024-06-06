import autogen
from src.agents import SEO_reviewer, legal_reviewer, ethics_reviewer, meta_reviewer, critic, writer
from src.config import load_env_file


load_env_file('/.env')

# chroma_client = chromadb.HttpClient(host='localhost', port=8000)



def reflection_message(recipient, messages, sender, config):
    return f'''Review the following content.
            \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}'''

review_chats = [
    {
     "recipient": SEO_reviewer,
     "message": reflection_message,
     "summary_method": "reflection_with_llm",
     "summary_args": {"summary_prompt" :
        "Return review into as JSON object only:"
        "{'Reviewer': '', 'Review': ''}. Here Reviewer should be your role",},
     "max_turns": 1},
    {
    "recipient": legal_reviewer, "message": reflection_message,
     "summary_method": "reflection_with_llm",
     "summary_args": {"summary_prompt" :
        "Return review into as JSON object only:"
        "{'Reviewer': '', 'Review': ''}.",},
     "max_turns": 1},
    {"recipient": ethics_reviewer, "message": reflection_message,
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
    max_turns=2,
    summary_method="last_msg"
)

print(res.summary)
