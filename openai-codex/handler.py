import boto3
import logging
import os
from lib.authorizer import create_policy, find_resources
from lib.repository import Repository
from lib.database_models import UserModel
from lib.codex import OpenAICodex
from uuid import uuid4
import secrets
import json

stage = os.environ["STAGE"]
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

db = Repository(boto3.client("dynamodb"))


def pydex(event, context):
    logger.info("Event: %s", event)
    path_parameter = event.get("pathParameters", {})
    docstring = path_parameter.get("docstring")
    body = json.loads(event.get("body"))

    # if docstring:
    #     return {"statusCode": 200, "body": json.dumps(edit(docstring))}
    return {"statusCode": 200}


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
