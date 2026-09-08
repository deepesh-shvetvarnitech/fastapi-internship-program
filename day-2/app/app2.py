
from fastapi import FastAPI, Header
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/greet/{name}")
async def greet_name(name: str):
    return {"message": f"Hello {name}"}


@app.get("/greet")
async def greet_query(name: str):
    return {"message": f"Hello {name}"}


@app.get("/greet/{name}/details")
async def greet_with_age(name: str, age: int):
    return {
        "message": f"Hello {name}",
        "age": age
    }


@app.get("/welcome")
async def welcome(name: str = "Guest", age: int = 0):
    return {
        "message": f"Hello {name}",
        "age": age
    }


class Book(BaseModel):
    title: str
    author: str


@app.post("/create_book")
async def create_book(book: Book):
    return {
        "title": book.title,
        "author": book.author
    }


@app.get("/get_headers")
async def get_headers(
    accept: str | None = Header(None),
    content_type: str | None = Header(None),
    user_agent: str | None = Header(None),
    host: str | None = Header(None)
):
    return {
        "Accept": accept,
        "Content-Type": content_type,
        "User-Agent": user_agent,
        "Host": host
    }

