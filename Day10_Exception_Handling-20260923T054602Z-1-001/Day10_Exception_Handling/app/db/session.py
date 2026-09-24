# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session, sessionmaker

# from app.core.config import settings


# engine = create_engine(
#     settings.DATABASE_URL,
#     echo=False,
#     pool_pre_ping=True,
# )


# SessionLocal = sessionmaker(
#     bind=engine,
#     autoflush=False,
#     autocommit=False,
# )


# def get_session():
#     session = SessionLocal()

#     try:
#         yield session
#     finally:
#         session.close() 


# synchronous code : 
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

def get_session():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()