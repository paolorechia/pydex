from dataclasses import dataclass

from pydex_lib.database_models import REQUEST_TYPES


@dataclass
class Request:
    """
    Dataclass for storing data from request
    """

    data: str
    request_type: str

    def validate(self):
        """
        Validates data from request
        :return:
        """
        if type(self.data) != str or type(self.request_type) != str:
            raise ValueError("Non string data or request_type")
        if self.request_type.lower() not in REQUEST_TYPES:
            raise ValueError(f"Request type {self.request_type} is not recognized.")
        if len(self.data) > 1024:
            raise ValueError("Data is too long")

    def dict(self):
        """
        Converts dataclass to dictionary
        :return:
        """
        return {"data": self.data, "request_type": self.request_type}
