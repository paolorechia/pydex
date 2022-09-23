import logging
import os

import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class OpenAICodex:
    """
    Used for making calls to the OpenAI API
    """

    def __init__(self, user_id, session) -> None:
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.completion_model = "code-cushman-001"
        self.edition_model = "code-davinci-edit-001"
        self.moderation_model = "text-moderation-latest"
        self.user_id = user_id
        self.session = session

    def _call_api(self, endpoint, data):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        url = f"https://api.openai.com/v1/{endpoint}"
        logger.info("Calling API: %s with data: %s", url, data)
        response = requests.post(
            url,
            headers=headers,
            json=data,
        )
        logger.info("Status code: %s", response.status_code)

        json_response = response.json()
        logger.info("Response: %s", json_response)
        return json_response

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            logger.error("Traceback: %s", traceback)
            raise exc_type(exc_value)

    def is_safe_content(self, content):
        logger.info("Checking if content is safe: %s", content)
        response = self._call_api(
            "moderations",
            {
                "model": self.moderation_model,
                "input": content,
            },
        )
        logger.info("Response: %s", response)
        return response["results"][0]["flagged"] == False

    def complete(self, prompt):
        if not self.is_safe_content(prompt):
            raise ValueError("Content is not safe.")

        logger.info("Completing prompt: %s", prompt)
        completion = self._call_api(
            "completions",
            data={
                "model": self.completion_model,
                "prompt": prompt,
                "max_tokens": 100,
                "temperature": 0.5,
                "user": self.user_id,
            },
        )
        logger.info("Completion: %s", completion)
        # For now, assume just one choice is available
        return completion["choices"][0]

    def edit(self, input_, instruction, temperature=0.5):
        if not self.is_safe_content(input_):
            raise ValueError("Content is not safe.")

        logger.info("Editing input: %s", input_)
        edition = self._call_api(
            "edits",
            {
                "model": self.edition_model,
                "input": input_,
                "instruction": instruction,
                "temperature": temperature,
                "user": self.user_id,
            },
        )
        logger.info("Edition: %s", edition)
        # For now, assume just one choice is available
        return edition["choices"][0]
