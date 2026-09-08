

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()


books = [
    {
        "id": 1,
        "title": "Think Python",
        "author": "Allen B. Downey",
        "publisher": "O'Reilly Media",
        "published_date": "2021-01-01",
        "page_count": 1234,
        "language": "English"
    },
    {
        "id": 2,
        "title": "Django By Example",
        "author": "Antonio Mele",
        "publisher": "Packt Publishing Ltd",
        "published_date": "2022-01-19",
        "page_count": 1023,
        "language": "English"
    },
    {
        "id": 3,
        "title": "The Web Socket Handbook",
        "author": "Alex Diaconu",
        "publisher": "Xinyu Wang",
        "published_date": "2021-01-01",
        "page_count": 3677,
        "language": "English"
    }
]


class Book(BaseModel):
    id: int
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str


class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str


@app.get("/books")
async def get_all_books():
    return books


@app.get("/books/{book_id}")
async def get_book_by_id(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book Not Found"
    )


@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book(book_data: Book):
    new_book = book_data.model_dump()
    books.append(new_book)
    return new_book


@app.patch("/books/{book_id}")
async def update_book(
    book_id: int,
    book_update: BookUpdateModel
):
    for book in books:
        if book["id"] == book_id:
            book["title"] = book_update.title
            book["author"] = book_update.author
            book["publisher"] = book_update.publisher
            book["page_count"] = book_update.page_count
            book["language"] = book_update.language

            return book

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book Not Found"
    )


@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            return {"message": "Book deleted successfully"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book Not Found"
    )


@app.delete("/books")
async def delete_all_books():
    books.clear()
    return {"message": "All books deleted successfully"}

