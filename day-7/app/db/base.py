from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def create_tables():
    from app.db import models
    from app.db.session import engine

    Base.metadata.create_all(bind=engine)