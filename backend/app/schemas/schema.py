from typing import Optional

from pydantic import BaseModel, field_validator

from app.utils.helper import normalize_input_url


class WebsiteRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def clean_url(cls, value: str) -> str:
        value = normalize_input_url(value)
        if not value:
            raise ValueError("URL must not be empty")
        return value


class Prediction(BaseModel):
    prediction: str
    confidence: Optional[float] = None
