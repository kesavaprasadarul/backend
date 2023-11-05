"""Example Schema for data validation."""
from pydantic import BaseModel


class Example(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
