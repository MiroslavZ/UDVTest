from enum import Enum

from pydantic import BaseModel, Field


class Merge(Enum):
    DELETE = 0
    APPEND = 1


class ConvertRequest(BaseModel):
    from_currency: str = Field(..., max_length=3, min_length=3, regex="[A-Z]")
    to_currency: str = Field(..., max_length=3, min_length=3, regex="[A-Z]")
    amount: float = Field(...)


class UpdateExchangeRateRequest(BaseModel):
    currency_pair: str = Field(..., max_length=6, min_length=6, regex="[A-Z]")
    new_rate: float = Field(...)
    merge: Merge = Field(...)
