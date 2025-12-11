"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BookBase(BaseModel):
    """Base book schema with common fields."""

    model_config = ConfigDict(from_attributes=True)

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Book title",
        examples=["The Great Gatsby"],
    )
    author: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Author name",
        examples=["F. Scott Fitzgerald"],
    )
    year: Optional[int] = Field(
        None,
        ge=1000,
        le=datetime.now().year,
        description="Publication year",
        examples=[1925],
    )

    @field_validator("title", "author")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Strip whitespace from string fields.

        Args:
            v: Input string value

        Returns:
            Stripped string
        """
        return v.strip() if v else v


class BookCreate(BookBase):
    """Schema for creating a new book."""

    pass


class BookUpdate(BaseModel):
    """Schema for updating an existing book."""

    model_config = ConfigDict(from_attributes=True)

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Book title",
        examples=["Updated Title"],
    )
    author: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Author name",
        examples=["Updated Author"],
    )
    year: Optional[int] = Field(
        None,
        ge=1000,
        le=datetime.now().year,
        description="Publication year",
        examples=[2023],
    )


class BookResponse(BookBase):
    """Schema for book response."""

    id: int = Field(..., description="Book ID", examples=[1])
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
