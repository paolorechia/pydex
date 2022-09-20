import os
from unittest.mock import patch

import pytest


@patch.dict(os.environ, {"STAGE": "dev"})
def test_signup_render():
    from signup import signup

    response = signup({}, {})
    assert response["statusCode"] == 200
    assert response["headers"]["Content-Type"] == "text/html"
    assert "https://dev.codex.api.openimagegenius.com/redirect" in response["body"]
