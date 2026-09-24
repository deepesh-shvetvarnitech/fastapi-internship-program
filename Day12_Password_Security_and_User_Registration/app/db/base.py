from app.db.models import Base
from app.db import models
from app.db.session import engine


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


# ---------- for alembic migration
'''
from app.db.models import Base
from app.db import models
# from app.db.session import engine

'''

# def create_tables() -> None:
#     Base.metadata.create_all(bind=engine)