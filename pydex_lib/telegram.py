import functools
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TelegramEnvironment:
    def __init__(self) -> None:
        self.token = os.environ["TELEGRAM_TOKEN"]
        self.chat_id = os.environ["TELEGRAM_CHAT_ID"]


class TelegramClient:
    def __init__(self, session, token, chat_id) -> None:
        self.session = session
        self.token = token
        self.chat_id = chat_id
        self.headers = {"Content-Type": "applicaton/json"}
        self.url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, message: str):
        logger.info("Sending message to telegram: %s", message)
        response = self.session.post(
            f"{self.url}/sendMessage", json={"chat_id": self.chat_id, "text": message}
        )
        logger.info("Telegram response: %s", response.json())


def get_telegram(http_session) -> TelegramClient:
    env = TelegramEnvironment()
    return TelegramClient(http_session, env.token, env.chat_id)


def telegram_on_error(http_session):
    def decorator_func(func):
        @functools.wraps(func)
        def wrapped_function(*args, **kwargs):
            telegram_client = get_telegram(http_session)
            try:
                func(*args, **kwargs)
            except Exception as e:
                telegram_client.send_message(f"Error: {e}")
                raise e
            return func(*args, **kwargs)

        return wrapped_function

    return decorator_func
