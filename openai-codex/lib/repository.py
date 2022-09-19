import logging
import os
from typing import Optional

from .database_models import Metadata, UserModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EnvironmentInfo:
    def __init__(self) -> None:
        # tables
        self.user_table_name = os.environ["USER_TABLE_NAME"]


def flatten_response(dynamodb_dict_response):
    """Converts a DynamoDB response to a flat dictionary."""
    flat_dict = {}
    for key, item in dynamodb_dict_response.items():
        type_ = [key for key in item.keys()][0]
        flat_dict[key] = item[type_]
    return flat_dict


def to_dynamodb_strings(model_dict_instance):
    """Converts a pydantic model to a DynamoDB string dictionary."""
    to_dynamo = {}
    for key, item in model_dict_instance.items():
        to_dynamo[key] = {"S": item}
    return to_dynamo


class Repository:
    def __init__(self, dynamo_client):
        self.ddb = dynamo_client
        self.environment = EnvironmentInfo()

    def get_user_by_api_token(self, api_token: str) -> Optional[UserModel]:
        logger.info("Requesting user by unique user id: %s", api_token)
        response = self.ddb.get_item(
            TableName=self.environment.user_table_name,
            Key={Metadata.UserTable.primary_key: {"S": api_token}},
        )
        logger.info("Response from 'Dynamo': %s", response)
        user = response.get("Item")
        if user:
            return UserModel(**flatten_response(user))
        return None

    def save_user(self, new_user: UserModel) -> None:
        logger.info("Saving user to Dynamo: %s", str(new_user))
        self.ddb.put_item(
            TableName=self.environment.user_table_name,
            Item={
                Metadata.UserTable.primary_key: {"S": new_user.api_token},
                "unique_user_id": {"S": new_user.unique_user_id},
            },
        )
        logger.info("User saved")
