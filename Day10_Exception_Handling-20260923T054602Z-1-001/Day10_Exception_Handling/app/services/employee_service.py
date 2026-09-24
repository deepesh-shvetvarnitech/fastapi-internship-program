# from sqlalchemy.exc import IntegrityError
# from sqlalchemy.orm import Session

# from app.db.models import Employee
# from app.repositories.department_repository import DepartmentRepository
# from app.repositories.employee_repository import EmployeeRepository
# from app.schemas.employee import EmployeeCreate, EmployeeUpdate


# class EmployeeService:

#     def __init__(self, db: Session):

#         self.db = db

#         self.employee_repository = EmployeeRepository(db)

#         self.department_repository = DepartmentRepository(db)

#     # ========================================================
#     # CREATE EMPLOYEE
#     # ========================================================

#     def create_employee(
#         self,
#         employee_data: EmployeeCreate,
#     ) -> Employee:

#         # Business Rule:
#         # Employee must belong to an existing department.

#         department = self.department_repository.get_by_id(
#             employee_data.department_id
#         )

#         if department is None:
#             raise ValueError(
#                 f"Department with ID "
#                 f"{employee_data.department_id} not found"
#             )

#         # Business Rule:
#         # Employee email must be unique.

#         existing_employee = (
#             self.employee_repository.get_by_email(
#                 str(employee_data.email)
#             )
#         )

#         if existing_employee is not None:
#             raise ValueError(
#                 "Employee with this email already exists"
#             )

#         employee = Employee(
#             name=employee_data.name,
#             email=str(employee_data.email),
#             department_id=employee_data.department_id,
#         )

#         try:

#             self.employee_repository.create(
#                 employee
#             )

#             self.db.commit()
#             self.db.refresh(employee)

#         except IntegrityError:

#             self.db.rollback()

#             raise ValueError(
#                 "Employee could not be created because "
#                 "of a database constraint"
#             )

#         return employee

#     # ========================================================
#     # GET EMPLOYEE
#     # ========================================================

#     def get_employee(
#         self,
#         employee_id: int,
#     ) -> Employee:

#         employee = self.employee_repository.get_by_id(
#             employee_id
#         )

#         if employee is None:
#             raise ValueError(
#                 "Employee not found"
#             )

#         return employee

#     # ========================================================
#     # LIST EMPLOYEES
#     # ========================================================

#     def get_employees(
#         self,
#         page: int,
#         page_size: int,
#     ) -> list[Employee]:

#         offset = (page - 1) * page_size

#         return self.employee_repository.get_all(
#             offset=offset,
#             limit=page_size,
#         )

#     # ========================================================
#     # UPDATE EMPLOYEE
#     # ========================================================

#     def update_employee(
#         self,
#         employee_id: int,
#         employee_data: EmployeeUpdate,
#     ) -> Employee:

#         employee = self.employee_repository.get_by_id(
#             employee_id
#         )

#         if employee is None:
#             raise ValueError(
#                 "Employee not found"
#             )

#         # Business Rule:
#         # Department must exist.

#         department = self.department_repository.get_by_id(
#             employee_data.department_id
#         )

#         if department is None:
#             raise ValueError(
#                 f"Department with ID "
#                 f"{employee_data.department_id} not found"
#             )

#         # Business Rule:
#         # Email must remain unique.

#         existing_employee = (
#             self.employee_repository.get_by_email(
#                 str(employee_data.email)
#             )
#         )

#         if (
#             existing_employee is not None
#             and existing_employee.id != employee_id
#         ):
#             raise ValueError(
#                 "Another employee already uses this email"
#             )

#         employee.name = employee_data.name
#         employee.email = str(employee_data.email)
#         employee.department_id = (
#             employee_data.department_id
#         )

#         try:

#             self.employee_repository.update(
#                 employee
#             )

#             self.db.commit()
#             self.db.refresh(employee)

#         except IntegrityError:

#             self.db.rollback()

#             raise ValueError(
#                 "Employee could not be updated because "
#                 "of a database constraint"
#             )

#         return employee

#     # ========================================================
#     # DELETE EMPLOYEE
#     # ========================================================

#     def delete_employee(
#         self,
#         employee_id: int,
#     ) -> None:

#         employee = self.employee_repository.get_by_id(
#             employee_id
#         )

#         if employee is None:
#             raise ValueError(
#                 "Employee not found"
#             )

#         try:

#             self.employee_repository.delete(
#                 employee
#             )

#             self.db.commit()

#         except IntegrityError:

#             self.db.rollback()

#             raise ValueError(
#                 "Employee cannot be deleted because "
#                 "related records exist"
#             )



from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    DepartmentNotFoundError,
    DuplicateEmailError,
    EmployeeDeleteConflictError,
    EmployeeNotFoundError,
)
from app.db.models import Employee
from app.repositories.department_repository import DepartmentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
)


class EmployeeService:

    def __init__(self, db: Session):
        self.db = db

        self.employee_repository = EmployeeRepository(
            db
        )

        self.department_repository = DepartmentRepository(
            db
        )

    # ========================================================
    # CREATE EMPLOYEE
    # ========================================================

    def create_employee(
        self,
        employee_data: EmployeeCreate,
    ) -> Employee:

        department = (
            self.department_repository.get_by_id(
                employee_data.department_id
            )
        )

        if department is None:
            raise DepartmentNotFoundError(
                employee_data.department_id
            )

        existing_employee = (
            self.employee_repository.get_by_email(
                str(employee_data.email)
            )
        )

        if existing_employee is not None:
            raise DuplicateEmailError(
                str(employee_data.email)
            )

        employee = Employee(
            name=employee_data.name,
            email=str(employee_data.email),
            department_id=employee_data.department_id,
        )

        try:
            self.employee_repository.create(
                employee
            )

            self.db.commit()
            self.db.refresh(employee)

        except IntegrityError:
            self.db.rollback()

            # Database remains the final authority
            raise DuplicateEmailError(
                str(employee_data.email)
            )

        return employee

    # ========================================================
    # GET EMPLOYEE
    # ========================================================

    def get_employee(
        self,
        employee_id: int,
    ) -> Employee:

        employee = (
            self.employee_repository.get_by_id(
                employee_id
            )
        )

        if employee is None:
            raise EmployeeNotFoundError(
                employee_id
            )

        return employee

    # ========================================================
    # LIST EMPLOYEES
    # ========================================================

    def get_employees(
        self,
        page: int,
        page_size: int,
    ) -> list[Employee]:

        offset = (page - 1) * page_size

        return self.employee_repository.get_all(
            offset=offset,
            limit=page_size,
        )

    # ========================================================
    # UPDATE EMPLOYEE
    # ========================================================

    def update_employee(
        self,
        employee_id: int,
        employee_data: EmployeeUpdate,
    ) -> Employee:

        employee = (
            self.employee_repository.get_by_id(
                employee_id
            )
        )

        if employee is None:
            raise EmployeeNotFoundError(
                employee_id
            )

        department = (
            self.department_repository.get_by_id(
                employee_data.department_id
            )
        )

        if department is None:
            raise DepartmentNotFoundError(
                employee_data.department_id
            )

        existing_employee = (
            self.employee_repository.get_by_email(
                str(employee_data.email)
            )
        )

        if (
            existing_employee is not None
            and existing_employee.id != employee_id
        ):
            raise DuplicateEmailError(
                str(employee_data.email)
            )

        employee.name = employee_data.name
        employee.email = str(employee_data.email)
        employee.department_id = (
            employee_data.department_id
        )

        try:
            self.employee_repository.update(
                employee
            )

            self.db.commit()
            self.db.refresh(employee)

        except IntegrityError:
            self.db.rollback()

            raise DuplicateEmailError(
                str(employee_data.email)
            )

        return employee

    # ========================================================
    # DELETE EMPLOYEE
    # ========================================================

    def delete_employee(
        self,
        employee_id: int,
    ) -> None:

        employee = (
            self.employee_repository.get_by_id(
                employee_id
            )
        )

        if employee is None:
            raise EmployeeNotFoundError(
                employee_id
            )

        try:
            self.employee_repository.delete(
                employee
            )

            self.db.commit()

        except IntegrityError:
            self.db.rollback()

            raise EmployeeDeleteConflictError()
