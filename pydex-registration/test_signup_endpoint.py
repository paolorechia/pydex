import requests
import pytest

endpoint = "https://dev.signup.codex.openimagegenius.com/signup"


def test_signup_get():
    response = requests.get(endpoint)
    print(response)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/html"
    assert "google" in response.content.decode()


def test_signup_post():
    response = requests.post(endpoint, json={"token": "test"})
    print(response)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/html"
    assert "Authorized" in response.content.decode()
