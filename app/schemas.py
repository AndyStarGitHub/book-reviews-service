from pydantic import BaseModel, Field
from typing import List, Optional


class BookCreate(BaseModel):
    title: str
    author: str
    year: int
    genres: List[str] = []


class BookRead(BaseModel):
    id: str
    title: str
    author: str
    year: int
    genres: List[str]


class BookList(BaseModel):
    id: str
    title: str
    author: str
    year: int
    genres: List[str]
    created_at: str
    avg_rating: Optional[float] = None
    reviews: Optional[list] = None


class BooksPage(BaseModel):
    total: int
    page: int
    size: int
    items: List[BookRead]


class ReviewAddFromBook(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    text: str


class ReviewCreate(BaseModel):
    book_id: str
    rating: int = Field(..., ge=1, le=5)
    text: str


class ReviewRead(BaseModel):
    book_id: str
    rating: int
    text: str
    id: str


class ReviewsPage(BaseModel):
    total: int
    page: int
    size: int
    items: List[ReviewRead]


class BookReadLong(BaseModel):
    id: str
    title: str
    author: str
    year: int
    genres: List[str]
    avg_rating: Optional[float] = None
    reviews: Optional[List[ReviewRead]] = None


class BookSearchItem(BaseModel):
    id: str
    title: str
    author: str
    year: int
    genres: List[str]
    created_at: str
    avg_rating: Optional[float] = None


class SearchPage(BaseModel):
    total: int
    page: int
    size: int
    items: List[BookSearchItem]


class TopRatedBook(BaseModel):
    book_id: str
    title: Optional[str] = None
    author: Optional[str] = None
    avg_rating: float


class TopRatedResponse(BaseModel):
    top: List[TopRatedBook]
