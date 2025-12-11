"""Custom exceptions for the application."""

from fastapi import HTTPException, status


class BookNotFoundException(HTTPException):
    """Raised when a book is not found."""

    def __init__(self, book_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )


class DuplicateBookException(HTTPException):
    """Raised when trying to create a duplicate book."""

    def __init__(self, title: str, author: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Book '{title}' by {author} already exists",
        )


class ValidationException(HTTPException):
    """Raised when validation fails."""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )
