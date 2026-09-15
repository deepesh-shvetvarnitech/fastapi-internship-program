from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ...db.session import get_session
from ...db.models import Employee
from ...schemas import EmployeeCreate, EmployeeUpdate, EmployeeResponse


router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_session)
):
    existing_employee = (
        db.query(Employee)
        .filter(Employee.email == employee.email)
        .first()
    )

    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee with this email already exists"
        )

    new_employee = Employee(
        name=employee.name,
        email=employee.email,
        department=employee.department
    )

    try:
        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee could not be created"
        )

    return new_employee


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK
)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_session)
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    return employee


@router.get(
    "/",
    response_model=list[EmployeeResponse],
    status_code=status.HTTP_200_OK
)
def get_employees(
    db: Session = Depends(get_session)
):
    employees = db.query(Employee).all()

    return employees


@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK
)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_session)
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    employee.name = employee_data.name
    employee.email = employee_data.email
    employee.department = employee_data.department

    try:
        db.commit()
        db.refresh(employee)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    db.delete(employee)
    db.commit()

    return None