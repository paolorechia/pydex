import requests
import pytest

url = "https://dev.codex.api.openimagegenius.com"
api_key = ""
with open(".test_api_key", "r") as f:
    api_key = f.read().strip()


def test_handler():
    response = requests.post(url, headers={"Authorization": api_key})
    assert response.status_code == 200


def test_handler_unauthorized():
    response = requests.post(url, headers={"Authorization": "invalid"})
    assert response.status_code == 401
