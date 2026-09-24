from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Task
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:

    def __init__(self, db: Session):

        self.db = db

        self.task_repository = TaskRepository(db)

        self.employee_repository = EmployeeRepository(db)

    # ========================================================
    # CREATE TASK
    # ========================================================

    def create_task(
        self,
        task_data: TaskCreate,
    ) -> Task:

        # Business Rule:
        # Task must belong to an existing employee.

        employee = self.employee_repository.get_by_id(
            task_data.employee_id
        )

        if employee is None:
            raise ValueError(
                f"Employee with ID "
                f"{task_data.employee_id} not found"
            )

        task = Task(
            title=task_data.title,
            description=task_data.description,
            employee_id=task_data.employee_id,
            status=task_data.status,
        )

        try:

            self.task_repository.create(
                task
            )

            self.db.commit()
            self.db.refresh(task)

        except IntegrityError:

            self.db.rollback()

            raise ValueError(
                "Task could not be created because "
                "of a database constraint"
            )

        return task

    # ========================================================
    # GET TASK
    # ========================================================

    def get_task(
        self,
        task_id: int,
    ) -> Task:

        task = self.task_repository.get_by_id(
            task_id
        )

        if task is None:
            raise ValueError(
                "Task not found"
            )

        return task

    # ========================================================
    # LIST TASKS
    # ========================================================

    def get_tasks(
        self,
        page: int,
        page_size: int,
    ) -> list[Task]:

        offset = (page - 1) * page_size

        return self.task_repository.get_all(
            offset=offset,
            limit=page_size,
        )

    # ========================================================
    # GET EMPLOYEE TASKS
    # ========================================================

    def get_employee_tasks(
        self,
        employee_id: int,
        page: int,
        page_size: int,
    ) -> list[Task]:

        employee = self.employee_repository.get_by_id(
            employee_id
        )

        if employee is None:
            raise ValueError(
                "Employee not found"
            )

        offset = (page - 1) * page_size

        return self.task_repository.get_by_employee(
            employee_id=employee_id,
            offset=offset,
            limit=page_size,
        )

    # ========================================================
    # UPDATE TASK
    # ========================================================

    def update_task(
        self,
        task_id: int,
        task_data: TaskUpdate,
    ) -> Task:

        task = self.task_repository.get_by_id(
            task_id
        )

        if task is None:
            raise ValueError(
                "Task not found"
            )

        # Business Rule:
        # New employee must exist.

        employee = self.employee_repository.get_by_id(
            task_data.employee_id
        )

        if employee is None:
            raise ValueError(
                f"Employee with ID "
                f"{task_data.employee_id} not found"
            )

        task.title = task_data.title
        task.description = task_data.description
        task.employee_id = task_data.employee_id
        task.status = task_data.status

        try:

            self.task_repository.update(
                task
            )

            self.db.commit()
            self.db.refresh(task)

        except IntegrityError:

            self.db.rollback()

            raise ValueError(
                "Task could not be updated because "
                "of a database constraint"
            )

        return task

    # ========================================================
    # DELETE TASK
    # ========================================================

    def delete_task(
        self,
        task_id: int,
    ) -> None:

        task = self.task_repository.get_by_id(
            task_id
        )

        if task is None:
            raise ValueError(
                "Task not found"
            )

        try:

            self.task_repository.delete(
                task
            )

            self.db.commit()

        except IntegrityError:

            self.db.rollback()

            raise ValueError(
                "Task could not be deleted because "
                "of a database constraint"
            )