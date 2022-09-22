from dataclasses import dataclass


class Metadata:
    class UserTable:
        primary_key = "api_token"


@dataclass
class UserModel:
    api_token: str
    unique_user_id: str
    google_user_id: str

    def dict(self):
        return {
            "api_token": self.api_token,
            "unique_user_id": self.unique_user_id,
            "google_user_id": self.google_user_id,
        }
