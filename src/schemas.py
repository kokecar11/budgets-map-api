from pydantic import BaseModel


class ResponseNotFound(BaseModel):
    detail: str = "Resource not found"
