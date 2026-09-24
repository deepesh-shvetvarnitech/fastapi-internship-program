# from fastapi import APIRouter, Depends, HTTPException, Query, status
# from sqlalchemy import select
# from sqlalchemy.exc import IntegrityError
# from sqlalchemy.orm import Session

# from app.db.models import Department, Employee
# from app.db.session import get_session
# from app.schemas.employee import (
#     EmployeeCreate,
#     EmployeeResponse,
#     EmployeeUpdate,
# )


# router = APIRouter(
#     prefix="/employees",
#     tags=["Employees"],
# )


# # ============================================================
# # CREATE EMPLOYEE
# # ============================================================

# @router.post(
#     "",
#     response_model=EmployeeResponse,
#     status_code=status.HTTP_201_CREATED,
# )
# def create_employee(
#     employee_data: EmployeeCreate,
#     db: Session = Depends(get_session),
# ):
#     # --------------------------------------------------------
#     # 1. Verify department exists
#     # --------------------------------------------------------

#     department = db.get(
#         Department,
#         employee_data.department_id,
#     )

#     if department is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=(
#                 f"Department with ID "
#                 f"{employee_data.department_id} not found"
#             ),
#         )

#     # --------------------------------------------------------
#     # 2. Check duplicate employee email
#     # --------------------------------------------------------

#     existing_employee = db.scalar(
#         select(Employee).where(
#             Employee.email == str(employee_data.email)
#         )
#     )

#     if existing_employee is not None:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Employee with this email already exists",
#         )

#     # --------------------------------------------------------
#     # 3. Create employee
#     # --------------------------------------------------------

#     employee = Employee(
#         name=employee_data.name,
#         email=str(employee_data.email),
#         department_id=employee_data.department_id,
#     )

#     db.add(employee)

#     try:
#         db.commit()
#         db.refresh(employee)

#     except IntegrityError:
#         db.rollback()

#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Employee could not be created because of a database constraint",
#         )

#     return employee


# # ============================================================
# # GET EMPLOYEE BY ID
# # ============================================================

# @router.get(
#     "/{employee_id}",
#     response_model=EmployeeResponse,
# )
# def get_employee(
#     employee_id: int,
#     db: Session = Depends(get_session),
# ):
#     employee = db.get(
#         Employee,
#         employee_id,
#     )

#     if employee is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Employee not found",
#         )

#     return employee


# # ============================================================
# # LIST EMPLOYEES
# # ============================================================

# @router.get(
#     "",
#     response_model=list[EmployeeResponse],
# )
# def get_employees(
#     page: int = Query(
#         default=1,
#         ge=1,
#         description="Page number",
#     ),
#     page_size: int = Query(
#         default=20,
#         ge=1,
#         le=100,
#         description="Number of employees per page",
#     ),
#     db: Session = Depends(get_session),
# ):
#     offset = (page - 1) * page_size

#     statement = (
#         select(Employee)
#         .order_by(Employee.id)
#         .offset(offset)
#         .limit(page_size)
#     )

#     employees = db.scalars(statement).all()

#     return employees


# # ============================================================
# # UPDATE EMPLOYEE
# # ============================================================

# @router.put(
#     "/{employee_id}",
#     response_model=EmployeeResponse,
# )
# def update_employee(
#     employee_id: int,
#     employee_data: EmployeeUpdate,
#     db: Session = Depends(get_session),
# ):
#     # --------------------------------------------------------
#     # 1. Find employee
#     # --------------------------------------------------------

#     employee = db.get(
#         Employee,
#         employee_id,
#     )

#     if employee is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Employee not found",
#         )

#     # --------------------------------------------------------
#     # 2. Verify department
#     # --------------------------------------------------------

#     department = db.get(
#         Department,
#         employee_data.department_id,
#     )

#     if department is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=(
#                 f"Department with ID "
#                 f"{employee_data.department_id} not found"
#             ),
#         )

#     # --------------------------------------------------------
#     # 3. Check duplicate email
#     # --------------------------------------------------------

#     existing_employee = db.scalar(
#         select(Employee).where(
#             Employee.email == str(employee_data.email),
#             Employee.id != employee_id,
#         )
#     )

#     if existing_employee is not None:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Another employee already uses this email",
#         )

#     # --------------------------------------------------------
#     # 4. Update employee
#     # --------------------------------------------------------

#     employee.name = employee_data.name
#     employee.email = str(employee_data.email)
#     employee.department_id = employee_data.department_id

#     try:
#         db.commit()
#         db.refresh(employee)

#     except IntegrityError:
#         db.rollback()

#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Employee could not be updated because of a database constraint",
#         )

#     return employee


# # ============================================================
# # DELETE EMPLOYEE
# # ============================================================

# @router.delete(
#     "/{employee_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
# )
# def delete_employee(
#     employee_id: int,
#     db: Session = Depends(get_session),
# ):
#     employee = db.get(
#         Employee,
#         employee_id,
#     )

#     if employee is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Employee not found",
#         )

#     db.delete(employee)

#     try:
#         db.commit()

#     except IntegrityError:
#         db.rollback()

#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Employee cannot be deleted because related records exist",
#         )

#     return None


######################################################################
# Day - 9 
######################################################################


# from fastapi import APIRouter, Depends, HTTPException, Query, status
# from sqlalchemy.orm import Session


# from sqlalchemy import select
# from sqlalchemy.exc import IntegrityError
# from app.db.models import Department, Employee
# from app.db.session import get_session

# from app.db.session import get_session
# from app.schemas.employee import (
#     EmployeeCreate,
#     EmployeeResponse,
#     EmployeeUpdate,
# )
# from app.services.employee_service import EmployeeService


# router = APIRouter(
#     prefix="/employees",
#     tags=["Employees"],
# )


# # ============================================================
# # CREATE
# # ============================================================

# @router.post(
#     "",
#     response_model=EmployeeResponse,
#     status_code=status.HTTP_201_CREATED,
# )
# def create_employee(
#     employee_data: EmployeeCreate,
#     db: Session = Depends(get_session),
# ):
#     service = EmployeeService(db)

#     try:
#         return service.create_employee(
#             employee_data
#         )

#     except ValueError as exc:
#         detail = str(exc)

#         if "already exists" in detail:
#             raise HTTPException(
#                 status_code=status.HTTP_409_CONFLICT,
#                 detail=detail,
#             )

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=detail,
#         )


# # ============================================================
# # GET BY ID
# # ============================================================

# @router.get(
#     "/{employee_id}",
#     response_model=EmployeeResponse,
# )
# def get_employee(
#     employee_id: int,
#     db: Session = Depends(get_session),
# ):
#     service = EmployeeService(db)

#     try:
#         return service.get_employee(
#             employee_id
#         )

#     except ValueError as exc:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=str(exc),
#         )


# # ============================================================
# # LIST
# # ============================================================

# @router.get(
#     "",
#     response_model=list[EmployeeResponse],
# )
# def get_employees(
#     page: int = Query(1, ge=1),
#     page_size: int = Query(
#         20,
#         ge=1,
#         le=100,
#     ),
#     db: Session = Depends(get_session),
# ):
#     service = EmployeeService(db)

#     return service.get_employees(
#         page=page,
#         page_size=page_size,
#     )


# # ============================================================
# # UPDATE
# # ============================================================

# @router.put(
#     "/{employee_id}",
#     response_model=EmployeeResponse,
# )
# def update_employee(
#     employee_id: int,
#     employee_data: EmployeeUpdate,
#     db: Session = Depends(get_session),
# ):
#     service = EmployeeService(db)

#     try:
#         return service.update_employee(
#             employee_id,
#             employee_data,
#         )

#     except ValueError as exc:
#         detail = str(exc)

#         if "email" in detail:
#             raise HTTPException(
#                 status_code=status.HTTP_409_CONFLICT,
#                 detail=detail,
#             )

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=detail,
#         )


# # ============================================================
# # DELETE
# # ============================================================

# @router.delete(
#     "/{employee_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
# )
# def delete_employee(
#     employee_id: int,
#     db: Session = Depends(get_session),
# ):
#     service = EmployeeService(db)

#     try:
#         service.delete_employee(
#             employee_id
#         )

#     except ValueError as exc:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=str(exc),
#         )

#     return None 




# ----------------------------------------------------
# Day 10 Error Handling
# ----------------------------------------------------

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
)
from app.services.employee_service import EmployeeService


router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_session),
):
    service = EmployeeService(db)

    return service.create_employee(
        employee_data
    )


@router.get(
    "",
    response_model=list[EmployeeResponse],
)
def get_employees(
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_session),
):
    service = EmployeeService(db)

    return service.get_employees(
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_session),
):
    service = EmployeeService(db)

    return service.get_employee(
        employee_id
    )


@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_session),
):
    service = EmployeeService(db)

    return service.update_employee(
        employee_id=employee_id,
        employee_data=employee_data,
    )


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_session),
):
    service = EmployeeService(db)

    service.delete_employee(
        employee_id
    )

    return None