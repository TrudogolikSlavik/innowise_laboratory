"""Database models."""

from typing import Any, Dict

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from .database import Base


class Book(Base):  # type: ignore
    """Book model representing a book in the collection.

    Attributes:
        id: Primary key
        title: Book title
        author: Author name
        year: Publication year (optional)
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """

    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    year = Column(Integer, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Book(id={self.id}, title='{self.title}', author='{self.author}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary.

        Returns:
            Dictionary representation of the book
        """
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
