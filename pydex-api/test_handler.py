import requests
import pytest

docstring_url = "https://dev.codex.api.openimagegenius.com/add_docstring"
api_key = ""
with open(".test_api_key", "r") as f:
    api_key = f.read().strip()


def test_handler():
    response = requests.post(
        docstring_url,
        headers={"Authorization": api_key},
        json={
             "data": \
"""def sum(a, b):
    return a + b
""",
        },
    )
    print(response.json())
    assert response.status_code == 200


def test_handler_unauthorized():
    response = requests.post(docstring_url, headers={"Authorization": "invalid"})
    print(response.json())
    assert response.status_code == 403
