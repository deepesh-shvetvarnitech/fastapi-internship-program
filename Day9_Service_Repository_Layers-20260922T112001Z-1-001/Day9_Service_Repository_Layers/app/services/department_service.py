from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Department
from app.repositories.department_repository import DepartmentRepository
from app.schemas.department import DepartmentCreate, DepartmentUpdate


class DepartmentService:

    def __init__(self, db: Session):

        self.db = db

        self.department_repository = DepartmentRepository(db)

    # ========================================================
    # CREATE DEPARTMENT
    # ========================================================

    def create_department(
        self,
        department_data: DepartmentCreate,
    ) -> Department:

        # Business Rule:
        # Department code must be unique.

        if department_data.code is not None:

            existing_department = (
                self.department_repository.get_by_code(
                    department_data.code
                )
            )

            if existing_department is not None:
                raise ValueError(
                    "Department code already exists"
                )

        department = Department(
            name=department_data.name,
            code=department_data.code,
        )

        try:

            self.department_repository.create(
                department
            )

            self.db.commit()
            self.db.refresh(department)

        except IntegrityError:

            self.db.rollback()

            raise ValueError(
                "Department could not be created because "
                "of a database constraint"
            )

        return department

    # ========================================================
    # GET DEPARTMENT
    # ========================================================

    def get_department(
        self,
        department_id: int,
    ) -> Department:

        department = (
            self.department_repository.get_by_id(
                department_id
            )
        )

        if department is None:
            raise ValueError(
                "Department not found"
            )

        return department

    # ========================================================
    # LIST DEPARTMENTS
    # ========================================================

    def get_departments(
        self,
        page: int,
        page_size: int,
    ) -> list[Department]:

        offset = (page - 1) * page_size

        return self.department_repository.get_all(
            offset=offset,
            limit=page_size,
        )

    # ========================================================
    # UPDATE DEPARTMENT
    # ========================================================

    def update_department(
        self,
        department_id: int,
        department_data: DepartmentUpdate,
    ) -> Department:

        department = (
            self.department_repository.get_by_id(
                department_id
            )
        )

        if department is None:
            raise ValueError(
                "Department not found"
            )

        # Business Rule:
        # Department code must remain unique.

        if department_data.code is not None:

            existing_department = (
                self.department_repository.get_by_code(
                    department_data.code
                )
            )

            if (
                existing_department is not None
                and existing_department.id != department_id
            ):
                raise ValueError(
                    "Department code already exists"
                )

        department.name = department_data.name
        department.code = department_data.code

        try:

            self.department_repository.update(
                department
            )

            self.db.commit()
            self.db.refresh(department)

        except IntegrityError:

            self.db.rollback()

            raise ValueError(
                "Department could not be updated because "
                "of a database constraint"
            )

        return department

    # ========================================================
    # DELETE DEPARTMENT
    # ========================================================

    def delete_department(
        self,
        department_id: int,
    ) -> None:

        department = (
            self.department_repository.get_by_id(
                department_id
            )
        )

        if department is None:
            raise ValueError(
                "Department not found"
            )

        try:

            self.department_repository.delete(
                department
            )

            self.db.commit()

        except IntegrityError:

            self.db.rollback()

            raise ValueError(
                "Department cannot be deleted because "
                "employees are assigned to it"
            )