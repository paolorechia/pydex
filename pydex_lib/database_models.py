from dataclasses import dataclass


class Metadata:
    class UserTable:
        primary_key = "api_token"


@dataclass
class UserModel:
    api_token: str
    unique_user_id: str


REQUEST_TYPES = frozenset(["add_docstring"])
