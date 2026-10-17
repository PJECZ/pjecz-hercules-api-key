"""
Custom pagination response models for FastAPI
"""

from collections.abc import Sequence
from typing import Generic, TypeVar

from fastapi_pagination import LimitOffsetPage
from pydantic import Field

T = TypeVar("T")


class CustomPage(LimitOffsetPage[T], Generic[T]):
    """Limit-offset page with the API's standard response envelope."""

    success: bool = True
    message: str = "Success"
    items: Sequence[T] = Field(serialization_alias="data")
