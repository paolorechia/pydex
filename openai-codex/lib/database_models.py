from pydantic import BaseModel

class Metadata:
    class UserTable:
        primary_key = "api_token"


class UserModel(BaseModel):
    api_token: str
    unique_user_id: str

REQUEST_TYPES = frozenset(["add_docstring"])