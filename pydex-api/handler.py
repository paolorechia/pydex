import json
import logging
import os
import secrets
from uuid import uuid4

import boto3
import requests

from lib.authorizer import create_policy, find_resources
from lib.codex import OpenAICodex
from lib.database_models import UserModel
from lib.repository import Repository
from lib.request_helper import build_pydex_response
from lib.request_models import Request

stage = os.environ["STAGE"]
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

db = Repository(boto3.client("dynamodb"))

http_session = requests.Session()


def pydex(event, context):
    logger.info("Event: %s", event)

    try:
        body = json.loads(event.get("body"))
    except json.JSONDecodeError as e:
        return build_pydex_response(400, "Invalid JSON body")

    logger.info("Decoded body: %s", body)
    path_parameter = event.get("pathParameters", {})
    request_type = path_parameter.get("request_type")

    logger.info("Request Type: %s", request_type)
    try:
        request = Request(request_type=request_type, data=body.get("data"))
        request.validate()
    except ValueError as e:
        logger.exception(e)
        return build_pydex_response(400, "Invalid request")

    user_id = event.get("requestContext", {}).get("authorizer", {}).get("user")

    if request_type == "add_docstring":
        input_function = request.data

        with OpenAICodex(user_id=user_id, session=http_session) as codex:
            edition = codex.edit(input_=input_function, instruction="Add docstring")
            return build_pydex_response(200, edition)

    return build_pydex_response(400, "Invalid request")


def authorizer(event, context):
    logger.info("Event: %s", event)
    resources = find_resources(event, stage)

    token = event.get("authorizationToken")
    if token:
        maybe_user = db.get_user_by_api_token(token)
        if maybe_user:
            allow_policy = create_policy(resources, effect="Allow")
            allow_policy["context"] = {"user": maybe_user.unique_user_id}
            logger.info("Authorization granted: %s", allow_policy)
            return allow_policy

    deny_policy = create_policy(resources, effect="Deny")
    logger.info("Authorization denied: %s", deny_policy)
    return deny_policy


def add_user(event, context):
    logger.info("Event: %s", event)
    token_size = 32
    user_id = str(uuid4())
    api_token = secrets.token_urlsafe(token_size)

    db.save_user(UserModel(api_token=api_token, unique_user_id=user_id))
    return {"statusCode": 200}
