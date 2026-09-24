from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Department


class DepartmentRepository:

    def __init__(self, db: Session):
        self.db = db

    # ========================================================
    # GET BY ID
    # ========================================================

    def get_by_id(
        self,
        department_id: int,
    ) -> Department | None:

        return self.db.get(
            Department,
            department_id,
        )

    # ========================================================
    # GET BY CODE
    # ========================================================

    def get_by_code(
        self,
        code: str,
    ) -> Department | None:

        statement = select(Department).where(
            Department.code == code
        )

        return self.db.scalar(statement)

    # ========================================================
    # GET ALL
    # ========================================================

    def get_all(
        self,
        offset: int,
        limit: int,
    ) -> list[Department]:

        statement = (
            select(Department)
            .order_by(Department.id)
            .offset(offset)
            .limit(limit)
        )

        return list(
            self.db.scalars(statement).all()
        )

    # ========================================================
    # CREATE
    # ========================================================

    def create(
        self,
        department: Department,
    ) -> Department:

        self.db.add(department)

        return department

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        department: Department,
    ) -> Department:

        return department

    # ========================================================
    # DELETE
    # ========================================================

    def delete(
        self,
        department: Department,
    ) -> None:

        self.db.delete(department)