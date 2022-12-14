import json


def build_pydex_response(status_code, response):
    """
    Builds a response for PyDex.

    :param status_code: The status code to return.
    :param response: The response body.
    :return: The response.
    """
    return {"statusCode": status_code, "body": json.dumps({"response": response})}


def build_pydex_error_response(status_code, message):
    """
    Builds a response for PyDex.

    :param status_code: The status code to return.
    :param response: The response body.
    :return: The response.
    """
    return {"statusCode": status_code, "body": build_error_message_body(message)}


def build_error_message_body(error):
    """Return error message body."""
    return json.dumps({"Message": error})


def build_rate_limited_response():
    """
    Build an HTTP 429 response
    """

    return {
        "statusCode": 429,
        "body": json.dumps({"Message": "Too many requests. Try again soon."}),
    }
