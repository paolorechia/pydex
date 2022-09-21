"""Google redirect handler."""
import logging
import os
import urllib.parse as parser
from uuid import uuid4
import secrets

# Careful, this import must come before google.auth.transport
from requests import Session

import boto3
from google.auth.transport import requests
from google.oauth2 import id_token
from jinja2 import Environment, PackageLoader, select_autoescape


from pydex_lib import database_models as models
from pydex_lib.repository import Repository
from pydex_lib import telegram
from pydex_lib.rate_limiter import rate_limited
from pydex_lib.telegram import telegram_on_error

db = Repository(boto3.client("dynamodb"))


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

http_session = Session()
telegram_client = telegram.get_telegram(http_session)

google_oauth_app_id = os.environ["GOOGLE_OAUTH_APP_ID"]
stage = os.environ["STAGE"]

env = Environment(
    loader=PackageLoader("template_app", "templates"), autoescape=select_autoescape()
)

newuser_template = env.get_template("newuser.html")
error_template = env.get_template("unauthorized.html")


def generate_user_id():
    return str(uuid4())


def generate_api_token(token_size=32):
    return secrets.token_urlsafe(token_size)


def retry_n_times(db_operation, max_attempts=3, key_generator=generate_user_id):
    clashed_user = "TemporarySentinel"
    attempts = 0
    unique_key = key_generator()
    while clashed_user and attempts <= max_attempts:
        clashed_user = db_operation(unique_key)

        if clashed_user:
            unique_key = clashed_user
            attempts += 1

        if not clashed_user:
            return unique_key
    return None


def could_not_process_request_error():
    return {
        "statusCode": 503,
        "body": error_template.render(
            error="Could not process your request at this time, please try again later."
        ),
        "headers": {"Content-Type": "text/html"},
    }


@telegram_on_error(http_session)
@rate_limited(
    event_key="requestContext.identity.sourceIp",
    prefix=f"google_oauth-{stage}",
    limit=5,
    period=60,
)
def google_redirect(event, context):
    try:
        body = event["body"]
        logger.info("Body: %s", body)
        parameters = parser.parse_qs(body, strict_parsing=True, max_num_fields=3)
        token = parameters["credential"][0]
    except (KeyError, ValueError, IndexError):
        return {"statusCode": 400, "body": "Bad Request"}

    client_id = google_oauth_app_id

    request = requests.Request()
    id_info = id_token.verify_oauth2_token(token, request, client_id)

    logger.info("Token is valid.")
    logger.info("Id info: %s", id_info)
    google_user_id = id_info["sub"]

    logging.info("Looking for existing user...")
    try:
        user = db.get_user_by_google_user_id(google_user_id)
    except IndexError:
        logger.info("Multiple users found, something went wrong :(")
        return {
            "statusCode": 409,
            "body": error_template.render(
                error="Multiple users found, conflict. Please contact support for help"
            ),
            "headers": {"Content-Type": "text/html"},
        }
    if user:
        unique_user_id = user.unique_user_id
    else:
        logger.info("User not found, new user should be created :)")
        unique_user_id = retry_n_times(
            db.get_user_by_unique_user_id, key_generator=generate_user_id
        )
        if not unique_user_id:
            return could_not_process_request_error()

        api_token = retry_n_times(
            db.get_user_by_api_token, key_generator=generate_api_token
        )
        if not api_token:
            return could_not_process_request_error()

        logger.info("Creating new user :)")

        new_user = models.UserModel(api_token=api_token, unique_user_id=unique_user_id)

        db.save_user(new_user)
        logger.info("New user created: %s", unique_user_id)
        telegram_client.send_message(f"New user created: {unique_user_id}")

    logger.info("Authentication successful, returning api key to frontend")

    response = {
        "statusCode": 200,
        "body": newuser_template.render(api_token=new_user.api_token),
        "headers": {
            "Set-Cookie": "Domain=openimagegenius.com; Secure",
            "Content-Type": "text/html",
        },
    }

    return response
