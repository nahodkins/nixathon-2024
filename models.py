from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    status: str


class MessageModel(BaseModel):
    message: str
    created: bool = False
