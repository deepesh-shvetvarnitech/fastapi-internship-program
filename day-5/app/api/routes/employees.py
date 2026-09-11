from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)

employees = [
    {
        "id": 1,
        "name": "Rahul",
        "email": "rahul@gmail.com",
        "department": "IT"
    },
    {
        "id": 2,
        "name": "Aman",
        "email": "aman@gmail.com",
        "department": "HR"
    }
]


class Employee(BaseModel):
    name: str
    email: str
    department: str


@router.get("/", summary="Get all employees")
def get_employees():
    return employees


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create employee")
def create_employee(employee: Employee):
    new_employee = {
        "id": len(employees) + 1,
        **employee.model_dump()
    }

    employees.append(new_employee)

    return new_employee


@router.get("/{employee_id}", summary="Get employee by ID")
def get_employee(employee_id: int):
    for employee in employees:
        if employee["id"] == employee_id:
            return employee

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Employee not found"
    )


@router.put("/{employee_id}", summary="Update employee")
def update_employee(employee_id: int, employee: Employee):
    for index, existing_employee in enumerate(employees):
        if existing_employee["id"] == employee_id:
            employees[index] = {
                "id": employee_id,
                **employee.model_dump()
            }

            return employees[index]

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Employee not found"
    )


@router.patch("/{employee_id}", summary="Partially update employee")
def patch_employee(employee_id: int, employee: Employee):
    for index, existing_employee in enumerate(employees):
        if existing_employee["id"] == employee_id:
            update_data = employee.model_dump(exclude_unset=True)

            employees[index].update(update_data)

            return employees[index]

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Employee not found"
    )


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete employee"
)
def delete_employee(employee_id: int):
    for index, employee in enumerate(employees):
        if employee["id"] == employee_id:
            employees.pop(index)
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Employee not found"
    )