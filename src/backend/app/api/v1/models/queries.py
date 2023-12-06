from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Range(BaseModel):
    min: Optional[float]
    max: Optional[float]


class DateRange(BaseModel):
    min: Optional[date]
    max: Optional[date]


class DatetimeRange(BaseModel):
    min: Optional[datetime]
    max: Optional[datetime]


class QueryBase(BaseModel):
    created_range: Optional[DateRange]
    updated_range: Optional[DatetimeRange]
