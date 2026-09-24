# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session

# from app.db.models import Employee, Task
# from app.db.session import get_session
# from app.schemas.task import TaskCreate, TaskResponse


# router = APIRouter(
#     prefix="/tasks",
#     tags=["Tasks"],
# )

# # Create Task

# @router.post(
#     "",
#     response_model=TaskResponse,
#     status_code=status.HTTP_201_CREATED,
# )
# def create_task(
#     task_data: TaskCreate,
#     db: Session = Depends(get_session),
# ):
#     employee = db.get(
#         Employee,
#         task_data.employee_id,
#     )

#     if employee is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Employee not found",
#         )

#     task = Task(
#         title=task_data.title,
#         description=task_data.description,
#         employee_id=task_data.employee_id,
#         status=task_data.status,
#     )

#     db.add(task)

#     try:
#         db.commit()
#         db.refresh(task)

#     except Exception:
#         db.rollback()
#         raise

#     return task

# --------------------------------------------------------------
# Day - 9 :  Service + Repository Layers
#---------------------------------------------------------------


# from fastapi import (
#     APIRouter,
#     Depends,
#     HTTPException,
#     Query,
#     status,
# )
# from sqlalchemy.orm import Session

# from app.db.session import get_session
# from app.schemas.task import (
#     TaskCreate,
#     TaskResponse,
#     TaskUpdate,
# )
# from app.services.task_service import TaskService


# router = APIRouter(
#     prefix="/tasks",
#     tags=["Tasks"],
# )


# # ============================================================
# # CREATE TASK
# # ============================================================

# @router.post(
#     "",
#     response_model=TaskResponse,
#     status_code=status.HTTP_201_CREATED,
# )
# def create_task(
#     task_data: TaskCreate,
#     db: Session = Depends(get_session),
# ):

#     service = TaskService(db)

#     try:

#         return service.create_task(
#             task_data
#         )

#     except ValueError as exc:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=str(exc),
#         )


# # ============================================================
# # GET TASK BY ID
# # ============================================================

# @router.get(
#     "/{task_id}",
#     response_model=TaskResponse,
# )
# def get_task(
#     task_id: int,
#     db: Session = Depends(get_session),
# ):

#     service = TaskService(db)

#     try:

#         return service.get_task(
#             task_id
#         )

#     except ValueError as exc:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=str(exc),
#         )


# # ============================================================
# # LIST TASKS
# # ============================================================

# @router.get(
#     "",
#     response_model=list[TaskResponse],
# )
# def get_tasks(
#     page: int = Query(1, ge=1),
#     page_size: int = Query(
#         20,
#         ge=1,
#         le=100,
#     ),
#     db: Session = Depends(get_session),
# ):

#     service = TaskService(db)

#     return service.get_tasks(
#         page=page,
#         page_size=page_size,
#     )


# # ============================================================
# # GET TASKS BY EMPLOYEE
# # ============================================================

# @router.get(
#     "/employee/{employee_id}",
#     response_model=list[TaskResponse],
# )
# def get_employee_tasks(
#     employee_id: int,
#     page: int = Query(1, ge=1),
#     page_size: int = Query(
#         20,
#         ge=1,
#         le=100,
#     ),
#     db: Session = Depends(get_session),
# ):

#     service = TaskService(db)

#     try:

#         return service.get_employee_tasks(
#             employee_id=employee_id,
#             page=page,
#             page_size=page_size,
#         )

#     except ValueError as exc:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=str(exc),
#         )


# # ============================================================
# # UPDATE TASK
# # ============================================================

# @router.put(
#     "/{task_id}",
#     response_model=TaskResponse,
# )
# def update_task(
#     task_id: int,
#     task_data: TaskUpdate,
#     db: Session = Depends(get_session),
# ):

#     service = TaskService(db)

#     try:

#         return service.update_task(
#             task_id=task_id,
#             task_data=task_data,
#         )

#     except ValueError as exc:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=str(exc),
#         )


# # ============================================================
# # DELETE TASK
# # ============================================================

# @router.delete(
#     "/{task_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
# )
# def delete_task(
#     task_id: int,
#     db: Session = Depends(get_session),
# ):

#     service = TaskService(db)

#     try:

#         service.delete_task(
#             task_id
#         )

#     except ValueError as exc:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=str(exc),
#         )

#     return None 


# -----------------------------------------------------------------
# Day 10 - Error Handling
#----------------------------------------------------------------
from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.task import (
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)
from app.services.task_service import TaskService


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


# ============================================================
# CREATE
# ============================================================

@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_session),
):
    service = TaskService(db)

    return service.create_task(
        task_data
    )


# ============================================================
# LIST
# ============================================================

@router.get(
    "",
    response_model=list[TaskResponse],
)
def get_tasks(
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
    service = TaskService(db)

    return service.get_tasks(
        page=page,
        page_size=page_size,
    )


# ============================================================
# EMPLOYEE TASKS
# ============================================================

@router.get(
    "/employee/{employee_id}",
    response_model=list[TaskResponse],
)
def get_employee_tasks(
    employee_id: int,
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
    service = TaskService(db)

    return service.get_employee_tasks(
        employee_id=employee_id,
        page=page,
        page_size=page_size,
    )


# ============================================================
# GET BY ID
# ============================================================

@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
def get_task(
    task_id: int,
    db: Session = Depends(get_session),
):
    service = TaskService(db)

    return service.get_task(
        task_id
    )


# ============================================================
# UPDATE
# ============================================================

@router.put(
    "/{task_id}",
    response_model=TaskResponse,
)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_session),
):
    service = TaskService(db)

    return service.update_task(
        task_id=task_id,
        task_data=task_data,
    )


# ============================================================
# DELETE
# ============================================================

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_session),
):
    service = TaskService(db)

    service.delete_task(
        task_id
    )

    return None