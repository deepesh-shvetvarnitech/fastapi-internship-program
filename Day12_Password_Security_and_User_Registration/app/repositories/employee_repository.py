from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Employee


class EmployeeRepository:

    def __init__(self, db: Session):
        self.db = db

    # ========================================================
    # GET BY ID
    # ========================================================

    def get_by_id(
        self,
        employee_id: int,
    ) -> Employee | None:

        return self.db.get(
            Employee,
            employee_id,
        )

    # ========================================================
    # GET BY EMAIL
    # ========================================================

    def get_by_email(
        self,
        email: str,
    ) -> Employee | None:

        statement = select(Employee).where(
            Employee.email == email
        )

        return self.db.scalar(statement)

    # ========================================================
    # GET ALL
    # ========================================================

    def get_all(
        self,
        offset: int,
        limit: int,
    ) -> list[Employee]:

        statement = (
            select(Employee)
            .order_by(Employee.id)
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
        employee: Employee,
    ) -> Employee:

        self.db.add(employee)

        return employee

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        employee: Employee,
    ) -> Employee:

        return employee

    # ========================================================
    # DELETE
    # ========================================================

    def delete(
        self,
        employee: Employee,
    ) -> None:

        self.db.delete(employee)