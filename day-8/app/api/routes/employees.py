from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Department, Employee
from app.db.session import get_session
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate
)

router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_session)
):
    department = db.get(
        Department,
        employee_data.department_id
    )

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    existing_employee = db.scalar(
        select(Employee).where(
            Employee.email == employee_data.email
        )
    )

    if existing_employee is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee email already exists"
        )

    employee = Employee(
        name=employee_data.name,
        email=employee_data.email,
        department_id=employee_data.department_id
    )

    db.add(employee)

    try:
        db.commit()
        db.refresh(employee)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee could not be created"
        )

    return employee


@router.get(
    "",
    response_model=list[EmployeeResponse]
)
def get_employees(
    db: Session = Depends(get_session)
):
    statement = select(Employee)
    employees = db.scalars(statement).all()

    return employees


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse
)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_session)
):
    employee = db.get(
        Employee,
        employee_id
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    return employee


@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse
)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_session)
):
    employee = db.get(
        Employee,
        employee_id
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    department = db.get(
        Department,
        employee_data.department_id
    )

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    existing_employee = db.scalar(
        select(Employee).where(
            Employee.email == employee_data.email,
            Employee.id != employee_id
        )
    )

    if existing_employee is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee email already exists"
        )

    employee.name = employee_data.name
    employee.email = employee_data.email
    employee.department_id = employee_data.department_id

    try:
        db.commit()
        db.refresh(employee)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee could not be updated"
        )

    return employee


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_session)
):
    employee = db.get(
        Employee,
        employee_id
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    db.delete(employee)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee cannot be deleted because related tasks exist"
        )

    return None