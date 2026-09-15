# Day-7 FastAPI SQLAlchemy PostgreSQL

## Project Overview

This project demonstrates SQLAlchemy 2.x integration with FastAPI and PostgreSQL.

## Technologies Used

- Python
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- Psycopg
- Pydantic Settings
- Uvicorn

## Concepts Covered

- Database configuration
- Environment variables
- SQLAlchemy Engine
- SQLAlchemy Session
- Session lifecycle
- Dependency with yield
- Declarative ORM models
- Primary Keys
- Foreign Keys
- Relationships
- Bidirectional relationships
- SQLAlchemy Base
- Metadata
- Automatic table creation

## Project Structure

```text
day-7/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   └── db/
│       ├── __init__.py
│       ├── base.py
│       ├── models.py
│       └── session.py
├── .env
├── .gitignore
├── README.md
└── requirements.txt