from pydantic import BaseModel, Field, validator, conint, confloat
from enum import Enum
from config import settings

class SummarizeStatus(str, Enum):
    success = "success"
    fallback = "fallback"
    cache = "cache"

class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=settings.MIN_TEXT_LENGTH, max_length=settings.MAX_TEXT_LENGTH)

    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty')
        return v.strip()

class SummarizeResponse(BaseModel):
    summary: str
    status: SummarizeStatus
    execution_time: float
    model_used: str | None = None
    cached: bool = False