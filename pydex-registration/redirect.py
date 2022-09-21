"""Google redirect handler."""
import logging
import os
import urllib.parse as parser
from datetime import datetime, timezone
from uuid import uuid4

import boto3
from google.auth.transport import requests
from google.oauth2 import id_token

# Careful, this import must come before google.auth.transport
from requests import Session

from pydex_lib import database_models as models
from pydex_lib import repository as repo_module
from pydex_lib import telegram
from pydex_lib.telegram import telegram_on_error
from pydex_lib.rate_limiter import rate_limited

dynamodb_client = boto3.client("dynamodb")
environment = repo_module.EnvironmentInfo()
repository = repo_module.Repository(dynamodb_client, environment)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

dynamo_db_client = boto3.client("dynamodb")

http_session = Session()
telegram_client = telegram.get_telegram(http_session)

google_oauth_app_id = os.environ["GOOGLE_OAUTH_APP_ID"]
stage = os.environ["STAGE"]


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
    user_google_email = id_info["email"]

    logging.info("Looking for existing user...")
    try:
        user = repository.get_user_by_google_user_id(google_user_id)
    except IndexError:
        logger.info("Multiple users found, something went wrong :(")
        return {
            "statusCode": 409,
            "body": html_failure_page.format(
                "Multiple users found, conflict. Please contact support for help"
            ),
            "headers": {"Content-Type": "text/html"},
        }
    if user:
        unique_user_id = user.unique_user_id
    else:
        logger.info("User not found, new user should be created :)")
        unique_user_id = str(uuid4())
        clashed_user = "TemporarySentinel"
        attempts = 0
        while clashed_user and attempts <= 3:
            clashed_user = repository.get_user_by_unique_id(unique_user_id)

            if clashed_user:
                unique_user_id = str(uuid4())
                attempts += 1

            if attempts > 3:
                return {
                    "statusCode": 503,
                    "body": html_failure_page.format(
                        "Could not process your request at this time, please try again later."
                    ),
                    "headers": {"Content-Type": "text/html"},
                }

            logger.info("Creating new user :)")
            creation_time = datetime.now(tz=timezone.utc)
            creation_time_iso = creation_time.isoformat()
            creation_time_timestamp = creation_time.timestamp()
            repository.save_user(
                models.UserModel(
                    unique_user_id=unique_user_id,
                    google_user_id=google_user_id,
                    user_google_email=user_google_email,
                    creation_time_iso=creation_time_iso,
                    creation_time_timestamp=creation_time_timestamp,
                )
            )
            telegram_client.send_message(f"New user created: {unique_user_id}")

    body = {
        "message": "Authorized successfully!",
        "unique_user_id": unique_user_id,
        "google_user_id": google_user_id,
        "user_email": user_google_email,
    }
    logger.info("Successful, authenticated user: %s", str(body))
    telegram_client.send_message(f"User authenticated: {unique_user_id}")

    response = {
        "statusCode": 200,
        "body": html_success_page.format(app_endpoints[stage]),
        "headers": {
            "Set-Cookie": f"token={token}; Domain=openimagegenius.com; Secure",
            "Content-Type": "text/html",
        },
    }

    return response
