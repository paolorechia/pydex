import os
import openai
import logging

# model="code-davinci-002"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class OpenAICodex:
    def __init__(self) -> None:
        self.api_key = os.environ["OPENAI_API_KEY"]
        openai.api_key = self.api_key
        self.completion_model = "code-cushman-001"
        self.edition_model = "code-davinci-edit-001"
        self.moderation_model = "text-moderation-latest"
        self.user_id = ""

    def __enter__(self, user_id):
        self.user_id = user_id
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.user_id = ""
        if exc_type:
            logger.error("Traceback: %s", traceback)
            raise exc_type(exc_value)

    def is_safe_content(self, content):
        logger.info("Checking if content is safe: %s", content)
        response = openai.Moderation.create(content)
        logger.info("Response: %s", response)
        return response["results"][0]["flagged"] == False

    def complete(self, prompt):
        if not self.is_safe_content(prompt):
            raise ValueError("Content is not safe.")

        logger.info("Completing prompt: %s", prompt)
        completion = openai.Completion.create(
            model=self.completion_model,
            prompt=prompt,
            max_tokens=100,
            temperature=0.5,
            user=self.user_id,
        )
        logger.info("Completion: %s", completion)
        # For now, assume just one choice is available
        return completion["choices"][0]

    def edit(self, input_, instruction, temperature=0.5):
        if not self.is_safe_content(input_):
            raise ValueError("Content is not safe.")

        logger.info("Editing input: %s", input_)
        edition = openai.Edit.create(
            model=self.edition_model,
            input=input_,
            instruction=instruction,
            temperature=temperature,
            user=self.user_id,
        )
        logger.info("Edition: %s", edition)
        # For now, assume just one choice is available
        return edition["choices"][0]
