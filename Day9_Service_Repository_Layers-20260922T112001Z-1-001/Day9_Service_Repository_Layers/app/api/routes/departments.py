# from fastapi import APIRouter, Depends, HTTPException, Query, status
# from sqlalchemy import select
# from sqlalchemy.exc import IntegrityError
# from sqlalchemy.orm import Session

# from app.db.models import Department
# from app.db.session import get_session
# from app.schemas.department import (
#     DepartmentCreate,
#     DepartmentResponse,
#     DepartmentUpdate,
# )


# router = APIRouter(
#     prefix="/departments",
#     tags=["Departments"],
# )


# # ============================================================
# # CREATE DEPARTMENT
# # ============================================================

# @router.post(
#     "",
#     response_model=DepartmentResponse,
#     status_code=status.HTTP_201_CREATED,
# )
# def create_department(
#     department_data: DepartmentCreate,
#     db: Session = Depends(get_session),
# ):
#     # Check duplicate department code

#     if department_data.code is not None:
#         existing_department = db.scalar(
#             select(Department).where(
#                 Department.code == department_data.code
#             )
#         )

#         if existing_department is not None:
#             raise HTTPException(
#                 status_code=status.HTTP_409_CONFLICT,
#                 detail="Department code already exists",
#             )

#     department = Department(
#         name=department_data.name,
#         code=department_data.code,
#     )

#     db.add(department)

#     try:
#         db.commit()
#         db.refresh(department)

#     except IntegrityError:
#         db.rollback()

#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Department could not be created because of a database constraint",
#         )

#     return department


# # ============================================================
# # GET DEPARTMENT BY ID
# # ============================================================

# @router.get(
#     "/{department_id}",
#     response_model=DepartmentResponse,
# )
# def get_department(
#     department_id: int,
#     db: Session = Depends(get_session),
# ):
#     department = db.get(
#         Department,
#         department_id,
#     )

#     if department is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Department not found",
#         )

#     return department


# # ============================================================
# # LIST DEPARTMENTS
# # ============================================================

# @router.get(
#     "",
#     response_model=list[DepartmentResponse],
# )
# def get_departments(
#     page: int = Query(1, ge=1),
#     page_size: int = Query(20, ge=1, le=100),
#     db: Session = Depends(get_session),
# ):
#     offset = (page - 1) * page_size

#     statement = (
#         select(Department)
#         .order_by(Department.id)
#         .offset(offset)
#         .limit(page_size)
#     )

#     departments = db.scalars(statement).all()

#     return departments


# # ============================================================
# # UPDATE DEPARTMENT
# # ============================================================

# @router.put(
#     "/{department_id}",
#     response_model=DepartmentResponse,
# )
# def update_department(
#     department_id: int,
#     department_data: DepartmentUpdate,
#     db: Session = Depends(get_session),
# ):
#     department = db.get(
#         Department,
#         department_id,
#     )

#     if department is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Department not found",
#         )

#     if department_data.code is not None:
#         existing_department = db.scalar(
#             select(Department).where(
#                 Department.code == department_data.code,
#                 Department.id != department_id,
#             )
#         )

#         if existing_department is not None:
#             raise HTTPException(
#                 status_code=status.HTTP_409_CONFLICT,
#                 detail="Department code already exists",
#             )

#     department.name = department_data.name
#     department.code = department_data.code

#     try:
#         db.commit()
#         db.refresh(department)

#     except IntegrityError:
#         db.rollback()

#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Department could not be updated",
#         )

#     return department


# # ============================================================
# # DELETE DEPARTMENT
# # ============================================================

# @router.delete(
#     "/{department_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
# )
# def delete_department(
#     department_id: int,
#     db: Session = Depends(get_session),
# ):
#     department = db.get(
#         Department,
#         department_id,
#     )

#     if department is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Department not found",
#         )

#     db.delete(department)

#     try:
#         db.commit()

#     except IntegrityError:
#         db.rollback()

#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail=(
#                 "Department cannot be deleted because "
#                 "employees are assigned to it"
#             ),
#         )

#     return None 

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.services.department_service import DepartmentService


router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


# ============================================================
# CREATE
# ============================================================

@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_department(
    department_data: DepartmentCreate,
    db: Session = Depends(get_session),
):

    service = DepartmentService(db)

    try:

        return service.create_department(
            department_data
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


# ============================================================
# GET BY ID
# ============================================================

@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def get_department(
    department_id: int,
    db: Session = Depends(get_session),
):

    service = DepartmentService(db)

    try:

        return service.get_department(
            department_id
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ============================================================
# LIST
# ============================================================

@router.get(
    "",
    response_model=list[DepartmentResponse],
)
def get_departments(
    page: int = Query(1, ge=1),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_session),
):

    service = DepartmentService(db)

    return service.get_departments(
        page=page,
        page_size=page_size,
    )


# ============================================================
# UPDATE
# ============================================================

@router.put(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    db: Session = Depends(get_session),
):

    service = DepartmentService(db)

    try:

        return service.update_department(
            department_id,
            department_data,
        )

    except ValueError as exc:

        detail = str(exc)

        if "not found" in detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=detail,
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


# ============================================================
# DELETE
# ============================================================

@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_department(
    department_id: int,
    db: Session = Depends(get_session),
):

    service = DepartmentService(db)

    try:

        service.delete_department(
            department_id
        )

    except ValueError as exc:

        detail = str(exc)

        if "not found" in detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=detail,
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )

    return None