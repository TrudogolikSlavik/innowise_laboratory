"""Tests for book API endpoints."""

from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from book_api.database import Base, get_db
from book_api.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    """Override dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database() -> Generator[None, None, None]:
    """Set up fresh database for each test."""
    Base.metadata.create_all(bind=engine)  # type: ignore
    yield
    Base.metadata.drop_all(bind=engine)  # type: ignore


def test_create_book() -> None:
    """Test creating a new book."""
    response = client.post(
        "/books/",
        json={"title": "Test Book", "author": "Test Author", "year": 2023},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Book"
    assert data["author"] == "Test Author"
    assert data["year"] == 2023
    assert "id" in data


def test_get_books() -> None:
    """Test getting all books."""
    # Create a book first
    client.post(
        "/books/",
        json={"title": "Test Book", "author": "Test Author", "year": 2023},
    )

    response = client.get("/books/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1  # type: ignore
    assert data[0]["title"] == "Test Book"


def test_search_books() -> None:
    """Test searching books."""
    client.post(
        "/books/",
        json={"title": "Python Programming", "author": "Guido", "year": 2020},
    )
    client.post(
        "/books/",
        json={"title": "FastAPI Guide", "author": "Sebastian", "year": 2022},
    )

    response = client.get("/books/search/?title=Python")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Python Programming"


def test_delete_book() -> None:
    """Test deleting a book."""
    # Create a book first
    create_response = client.post(
        "/books/",
        json={"title": "To Delete", "author": "Author", "year": 2023},
    )
    book_id = create_response.json()["id"]

    # Delete the book
    delete_response = client.delete(f"/books/{book_id}")
    assert delete_response.status_code == 204

    # Verify book is deleted
    get_response = client.get("/books/")
    data = get_response.json()
    assert len(data) == 0


def test_update_book() -> None:
    """Test updating a book."""
    # Create a book first
    create_response = client.post(
        "/books/",
        json={"title": "Old Title", "author": "Old Author", "year": 2020},
    )
    book_id = create_response.json()["id"]

    # Update the book
    update_response = client.put(
        f"/books/{book_id}",
        json={"title": "New Title", "author": "New Author", "year": 2023},
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "New Title"
    assert data["author"] == "New Author"
    assert data["year"] == 2023
