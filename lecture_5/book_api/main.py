"""FastAPI application with book collection endpoints."""

from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, Query, status
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from book_api.database import engine, get_db
from book_api.exceptions import BookNotFoundException, DuplicateBookException

from . import models, schemas

models.Base.metadata.create_all(bind=engine)  # type: ignore

app = FastAPI(
    title="Book Collection API",
    description="A simple API to manage book collections",
    version="0.1.0",
)


def get_book_or_404(db: Session, book_id: int) -> models.Book:
    """Get book by ID or raise 404 error.

    Args:
        db: Database session
        book_id: ID of the book to retrieve

    Returns:
        Book instance if found

    Raises:
        BookNotFoundException: If book is not found
    """
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise BookNotFoundException(book_id)
    return book


def apply_filters(
    query: Any,
    title: Optional[str] = None,
    author: Optional[str] = None,
    year: Optional[int] = None,
) -> Any:
    """Apply search filters to SQLAlchemy query.

    Args:
        query: SQLAlchemy query object
        title: Title search term (partial match, case-insensitive)
        author: Author search term (partial match, case-insensitive)
        year: Exact publication year

    Returns:
        Filtered SQLAlchemy query
    """
    if title:
        query = query.filter(models.Book.title.ilike(f"%{title}%"))
    if author:
        query = query.filter(models.Book.author.ilike(f"%{author}%"))
    if year:
        query = query.filter(models.Book.year == year)
    return query


# ========== Endpoints ==========
@app.post(
    "/books/",
    response_model=schemas.BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new book",
    response_description="The created book",
)
def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_db),
) -> models.Book:
    """Create a new book in the collection.

    Args:
        book: Book data to create
        db: Database session

    Returns:
        Created book with ID

    Raises:
        DuplicateBookException: If book with same title and author already exists
    """
    existing = (
        db.query(models.Book)
        .filter(
            models.Book.title.ilike(book.title),
            models.Book.author.ilike(book.author)
        )
        .first()
    )

    if existing:
        raise DuplicateBookException(book.title, book.author)

    db_book = models.Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@app.get(
    "/books/",
    response_model=List[schemas.BookResponse],
    summary="Get all books",
    response_description="List of books",
)
def read_books(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    sort_by: str = Query(
        "id", description="Field to sort by (id, title, author, year)"
    ),
    sort_order: str = Query("asc", description="Sort order (asc, desc)"),
    db: Session = Depends(get_db),
) -> List[models.Book]:
    """Get all books with pagination and sorting.

    Args:
        skip: Number of books to skip (for pagination)
        limit: Maximum number of books to return
        sort_by: Field to sort by (id, title, author, year)
        sort_order: Sort order (asc or desc)
        db: Database session

    Returns:
        List of books sorted by specified field
    """
    valid_sort_fields = {"id", "title", "author", "year"}
    if sort_by not in valid_sort_fields:
        sort_by = "id"

    order_by_field = getattr(models.Book, sort_by)
    if sort_order.lower() == "desc":
        order_by_field = order_by_field.desc()

    query = db.query(models.Book).order_by(order_by_field)
    books = query.offset(skip).limit(limit).all()
    return books


@app.get(
    "/books/{book_id}",
    response_model=schemas.BookResponse,
    summary="Get book by ID",
    response_description="The requested book",
)
def read_book(
    book_id: int,
    db: Session = Depends(get_db),
) -> models.Book:
    """Get a specific book by its ID.

    Args:
        book_id: ID of the book to retrieve
        db: Database session

    Returns:
        Book with the specified ID

    Raises:
        HTTPException: 404 if book is not found
    """
    return get_book_or_404(db, book_id)


@app.delete(
    "/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a book",
)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a book by ID.

    Args:
        book_id: ID of the book to delete
        db: Database session

    Raises:
        BookNotFoundException: If book is not found
    """
    book = get_book_or_404(db, book_id)
    db.delete(book)
    db.commit()


@app.put(
    "/books/{book_id}",
    response_model=schemas.BookResponse,
    summary="Update book details",
    response_description="The updated book",
)
def update_book(
    book_id: int,
    book_update: schemas.BookUpdate,
    db: Session = Depends(get_db),
) -> models.Book:
    """Update book details.

    Args:
        book_id: ID of the book to update
        book_update: Fields to update
        db: Database session

    Returns:
        Updated book

    Raises:
        BookNotFoundException: If book is not found
    """
    book = get_book_or_404(db, book_id)

    update_data = book_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book


@app.get(
    "/books/search/",
    response_model=List[schemas.BookResponse],
    summary="Search books",
    response_description="List of matching books",
)
def search_books(
    title: Optional[str] = Query(None, min_length=1, description="Title search term"),
    author: Optional[str] = Query(None, min_length=1, description="Author search term"),
    year: Optional[int] = Query(None, ge=1000, le=2100, description="Publication year"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    sort_by: str = Query(
        "id",
        description="Field to sort by (id, title, author, year)",
    ),
    sort_order: str = Query("asc", description="Sort order (asc, desc)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: Session = Depends(get_db),
) -> List[models.Book]:
    """Search books by title, author, or year.

    Args:
        title: Search term for book title (partial match)
        author: Search term for author name (partial match)
        year: Exact publication year
        skip: Number of books to skip (for pagination)
        limit: Maximum number of books to return
        sort_by: Field to sort by (id, title, author, year)
        sort_order: Sort order (asc or desc)
        db: Database session

    Returns:
        List of matching books
    """
    query = db.query(models.Book)
    query = apply_filters(query, title, author, year)

    valid_sort_fields = {"id", "title", "author", "year"}
    if sort_by not in valid_sort_fields:
        sort_by = "id"

    order_by_field = getattr(models.Book, sort_by)
    if sort_order.lower() == "desc":
        order_by_field = order_by_field.desc()

    query = query.order_by(order_by_field)

    return query.offset(skip).limit(limit).all()


@app.get(
    "/stats/",
    summary="Get book collection statistics",
    response_description="Book collection statistics",
)
def get_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get statistics about the book collection.

    Args:
        db: Database session

    Returns:
        Dictionary with statistics including total books and books by year
    """
    total_books = db.query(models.Book).count()

    books_by_year_result = (
        db.query(models.Book.year, func.count(models.Book.id))
        .filter(models.Book.year.isnot(None))
        .group_by(models.Book.year)
        .all()
    )

    books_by_year = dict(books_by_year_result)

    return {
        "total_books": total_books,
        "books_by_year": books_by_year,
        "years_covered": sorted(books_by_year.keys()),
    }


@app.get("/health", include_in_schema=False)
def health_check(db: Session = Depends(get_db)) -> dict[str, str]:
    """Health check endpoint (excluded from OpenAPI schema).

    Args:
        db: Database session

    Returns:
        Health status information
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy",
        "database": db_status,
        "version": "0.1.0",
    }
