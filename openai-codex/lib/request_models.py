from lib.database_models import REQUEST_TYPES
from dataclasses import dataclass


@dataclass
class Request:
    data: str
    request_type: str

    def validate(self):
        if type(self.data) != str or type(self.request_type) != str:
            raise ValueError("Non string data or request_type")
        if self.request_type.lower() not in REQUEST_TYPES:
            raise ValueError(f"Request type {self.request_typev} is not recognized.")
        if len(self.data) > 1024:
            raise ValueError("Data is too long")
