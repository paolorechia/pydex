from pydantic import BaseModel

class Metadata:
    class UserTable:
        primary_key = "unique_user_id"


class UserModel(BaseModel):
    api_token: str
    unique_user_id: str

REQUEST_TYPES = frozenset(["add_docstring"])