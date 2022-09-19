import database_models as models
from pydantic import BaseModel, validator
from uuid import UUID


class Request(BaseModel):
    data: str
    request_type: str

    @validator('request_type')
    def request_type_validator(cls, v):
        if v.lower() not in models.REQUEST_TYPES:
            raise ValueError(f"Request type {v} is not recognized.")
        return v


