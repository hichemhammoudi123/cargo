"""Common response schemas."""
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class SuccessData(BaseModel):
    success: bool = True
    data: dict | list | None = None


class PaginatedResponse(BaseModel):
    success: bool = True
    data: list
    pagination: dict
