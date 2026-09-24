from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Task


class TaskRepository:

    def __init__(self, db: Session):
        self.db = db

    # ========================================================
    # GET BY ID
    # ========================================================

    def get_by_id(
        self,
        task_id: int,
    ) -> Task | None:

        return self.db.get(
            Task,
            task_id,
        )

    # ========================================================
    # GET ALL
    # ========================================================

    def get_all(
        self,
        offset: int,
        limit: int,
    ) -> list[Task]:

        statement = (
            select(Task)
            .order_by(Task.id)
            .offset(offset)
            .limit(limit)
        )

        return list(
            self.db.scalars(statement).all()
        )

    # ========================================================
    # GET BY EMPLOYEE
    # ========================================================

    def get_by_employee(
        self,
        employee_id: int,
        offset: int,
        limit: int,
    ) -> list[Task]:

        statement = (
            select(Task)
            .where(
                Task.employee_id == employee_id
            )
            .order_by(Task.id)
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
        task: Task,
    ) -> Task:

        self.db.add(task)

        return task

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        task: Task,
    ) -> Task:

        return task

    # ========================================================
    # DELETE
    # ========================================================

    def delete(
        self,
        task: Task,
    ) -> None:

        self.db.delete(task)