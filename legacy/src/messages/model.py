from pydantic import BaseModel


class PostMessageRequest(BaseModel):
    message: str
    lat: float | None = None
    lon: float | None = None
    is_point: bool | None = None
    language: str | None = "en"


class PostMessageResponse(BaseModel):
    response: str
    ward: str | None = None
