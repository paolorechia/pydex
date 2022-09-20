import json

import boto3
import pytest

lambda_name = "pydex-api-dev-addUser"

# By default, we don't want to test this function
# Comment the next line to test it
@pytest.mark.skip
def test_add_user():
    lambda_client = boto3.client("lambda")
    response = lambda_client.invoke(
        FunctionName=lambda_name,
        InvocationType="RequestResponse",
        Payload=b'{"body": "test"}',
    )
    print(response)
    payload = response.get("Payload").read()
    j = json.loads(payload)
    print(j)
    assert j.get("errorMessage") is None
