import os
from unittest.mock import MagicMock, patch

import pytest


@patch.dict(
    os.environ, {"STAGE": "dev", "TELEGRAM_TOKEN": "test", "TELEGRAM_CHAT_ID": "123"}
)
def test_signup_render():
    from signup import signup

    response = signup({}, {})
    print(response)
    assert response["statusCode"] == 200
    assert response["headers"]["Content-Type"] == "text/html"
    assert "https://dev.codex.api.openimagegenius.com/redirect" in response["body"]
