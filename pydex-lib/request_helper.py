import json


def build_pydex_response(status_code, response):
    """
    Builds a response for PyDex.

    :param status_code: The status code to return.
    :param response: The response body.
    :return: The response.
    """
    return {"statusCode": status_code, "body": json.dumps({"response": response})}


def build_error_message_body(error):
    """Return error message body."""
    return json.dumps({"message_type": "error", "data": error})


def build_rate_limited_response():
    """
    Build an HTTP 429 response
    """

    return {
        "statusCode": 429,
        "body": json.dumps(
            {"message_type": "rate_limit", "data": "Too many requests. Try again soon."}
        ),
    }
