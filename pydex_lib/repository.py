import logging
import os
from typing import Optional

from pydex_lib.database_models import Metadata, UserModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EnvironmentInfo:
    def __init__(self) -> None:
        # tables
        self.user_table_name = os.environ["USER_TABLE_NAME"]
        self.google_user_id_index_name = os.environ["GOOGLE_USER_ID_INDEX_NAME"]
        self.unique_user_id_index_name = os.environ["UNIQUE_USER_ID_INDEX_NAME"]


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
    """
    Repository for persisting data in DynamoDB.
    """

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
        logger.info("Table name: %s", self.environment.user_table_name)
        logger.info("DDB Item: %s", to_dynamodb_strings(new_user.dict()))
        item = {
            Metadata.UserTable.primary_key: {"S": new_user.api_token},
            "unique_user_id": {"S": new_user.unique_user_id},
        }
        self.ddb.put_item(TableName=self.environment.user_table_name, Item=item)
        logger.info("User saved")

    def get_user_by_google_user_id(self, google_user_id: str) -> Optional[UserModel]:
        logger.info("Requesting user by google_user_id: %s", google_user_id)
        response = self.ddb.query(
            TableName=self.environment.user_table_name,
            IndexName=self.environment.google_user_id_index_name,
            KeyConditionExpression="google_user_id = :gui",
            ExpressionAttributeValues={":gui": {"S": google_user_id}},
        )
        logger.info("Response from DynamoDB: %s", response)
        existing_users = response["Items"]
        if len(existing_users) > 1:
            logger.info("Multiple users found, something went wrong :(")
            raise IndexError("Multiple users error")
        elif len(existing_users) == 1:
            user = existing_users[0]
            logger.info("User found, user: %s", str(user))
            return UserModel(**flatten_response(user))
        return None

    def get_user_by_unique_user_id(self, unique_user_id: str) -> Optional[UserModel]:
        logger.info("Requesting user by unique_user_id: %s", unique_user_id)
        response = self.ddb.query(
            TableName=self.environment.user_table_name,
            IndexName=self.environment.unique_user_id_index_name,
            KeyConditionExpression="unique_user_id = :uui",
            ExpressionAttributeValues={":uui": {"S": unique_user_id}},
        )
        logger.info("Response from DynamoDB: %s", response)
        existing_users = response["Items"]
        if len(existing_users) > 1:
            logger.info("Multiple users found, something went wrong :(")
            raise IndexError("Multiple users error")
        elif len(existing_users) == 1:
            user = existing_users[0]
            logger.info("User found, user: %s", str(user))
            return UserModel(**flatten_response(user))
        return None
