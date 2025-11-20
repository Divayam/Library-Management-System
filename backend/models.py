"""
Pydantic models for request/response validation.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


class BookBase(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    isbn: Optional[str] = None
    total_copies: int = Field(..., ge=1)


class BookCreate(BookBase):
    available_copies: Optional[int] = None

    @validator("available_copies", always=True)
    def default_available(cls, value, values):  # noqa: D417
        total = values.get("total_copies", 0)
        if value is None:
            return total
        if value > total:
            raise ValueError("available_copies cannot exceed total_copies")
        return value


class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr


class BorrowRecordCreate(BaseModel):
    student_id: int = Field(..., gt=0)
    book_id: int = Field(..., gt=0)
    borrow_date: date = Field(default_factory=date.today)
    status: str = Field(default="borrowed")


class BorrowRecordReturn(BaseModel):
    record_id: int = Field(..., gt=0)
    return_date: date = Field(default_factory=date.today)


class TimestampedModel(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

