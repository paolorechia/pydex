import os
import openai

with open(".codex_api_key", "r") as fp:
    os.environ["OPENAI_API_KEY"] = fp.read().strip()

# model="code-davinci-002"
completion_model = "code-cushman-001"
edition_model = "code-davinci-edit-001"

openai.api_key = os.getenv("OPENAI_API_KEY")
def complete():
    completion = openai.Completion.create(
        model=completion_model,
        prompt='"""Print hello world in Python"""',
        max_tokens=50,
        temperature=0,
    )
    print(completion)
    return completion

def edit():
    edition = openai.Edit.create(
        model=edition_model,
        input="print('hello world'",
        instruction="Fix syntax errors"
    )
    print(edition)
    return edition


edit()