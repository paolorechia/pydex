import os
import logging
import requests

from jinja2 import Environment, PackageLoader, select_autoescape
from pydex_lib.telegram import telegram_on_error

env = Environment(
    loader=PackageLoader("template_app", "templates"), autoescape=select_autoescape()
)

urls = {
    "dev": "https://dev.codex.api.openimagegenius.com/signup",
    "prod": "https://codex.api.openimagegenius.com/signup",
}

signup_template = env.get_template("signup.html")
stage = os.environ["STAGE"]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

http_session = requests.Session()


@telegram_on_error(http_session)
def signup(event, context):
    logger.info("Event: %s", event)
    html = signup_template.render(
        url=urls[stage], google_app_id=os.environ["GOOGLE_OAUTH_ID"]
    )
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": html,
    }
