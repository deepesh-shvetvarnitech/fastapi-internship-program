'''
                                                          Section A 
1) Validating and serializing request and response data
2) class ModelName(BaseModel):
3) BaseModel
4) FastAPI returns a 422 validation error
5) 201
6) 204
7) To define the expected response structure and filter fields
8) To avoid exposing sensitive or internal fields in responses
9) min_length=3
10) gt=0
11) The field can be a string or None
12) PUT
13) PATCH
14) Automatic validation and clear error messages
15) 422
16) Excludes the password field from the response
17) Consistent, clear, and REST-friendly names
18) To help API consumers understand expected data
19) 200–299
20) They may expose internal or sensitive fields

                                                             Section B
                                                        Question =1


Pydantic model FastAPI me request data ko define aur validate karne ke liye use hota hai. Ye check karta hai ki user ne correct data type aur valid values bheji hain ya nahi. Agar data invalid ho, FastAPI automatically validation error return karta hai.

Example:

salary: float = Field(gt=0)

Iska matlab salary 0 se greater honi chahiye.

                                                        Question = 2


Create/Update aur Response ke liye separate schemas use karna safer hota hai. Isse hum internal ya sensitive fields ko API response me expose hone se rok sakte hain.

Example: password create schema me ho sakta hai, lekin response schema me nahi hona chahiye.

                                                          Question = 3

Answer:
response_model API ke response ka structure define karta hai. Ye unwanted fields ko response se filter bhi kar sakta hai.

Benefit: API consumer ko consistent aur safe response milta hai.

                                                            Question = 4



200 → Request successfully complete hui aur response data available hai.
201 → New resource successfully create hua.
204 → Request successful hai lekin response body me koi content nahi hai.
422 → Request body validation fail hui.

                                                                 Section C
                                                              question =1

Issues:

EmployeeCreate input ke liye hai, response ke liye nahi.
password response me expose nahi hona chahiye.
is_admin internal/sensitive field ho sakta hai.
Fields par proper validation missing hai.
salary par positive/range validation honi chahiye.
email ko email format validate karna chahiye.

Improvement:
Separate EmployeeCreate aur EmployeeResponse models use karne chahiye.

                                                        question = 2
Issues:

dict use karne se automatic validation nahi milegi.
Required fields/type checking clear nahi hai.
API documentation weak hogi.
Invalid values business logic tak pahunch sakti hain.

Improvement:
EmployeeUpdate jaisa Pydantic model request body ke liye use karna chahiye.

                                                    question =  3

Successful employee creation ke liye 201 Created use karna better hai.

Reason: POST /employees ek new employee resource create karta hai.

                                                       question = 4 

Ye fields response me expose nahi karni chahiye:

password_hash
created_at ko expose karna generally okay hai, agar API consumer ko required ho.

password_hash ko hide karna important hai kyunki ye sensitive authentication information hai.


                                                 SECTION = D'''
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Path, status
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


app = FastAPI(
    title="Employee Management API",
    description=(
        "A beginner-friendly Employee Management API demonstrating "
        "Pydantic request validation, response models, CRUD operations, "
        "HTTP status codes, and API documentation."
    ),
    version="1.0.0",
)


MIN_SALARY = 10_000
MAX_SALARY = 10_000_000


EMPLOYEES = [
    {
        "id": 1,
        "name": "Rahul Sharma",
        "email": "rahul@example.com",
        "department": "Engineering",
        "salary": 75000,
        "joining_date": date(2024, 1, 15),
        "password": "secret123",
        "is_admin": False,
    },
    {
        "id": 2,
        "name": "Priya Patel",
        "email": "priya@example.com",
        "department": "HR",
        "salary": 60000,
        "joining_date": date(2023, 8, 10),
        "password": "secret456",
        "is_admin": True,
    },
    {
        "id": 3,
        "name": "Amit Kumar",
        "email": "amit@example.com",
        "department": "Finance",
        "salary": 65000,
        "joining_date": date(2022, 5, 20),
        "password": "secret789",
        "is_admin": False,
    },
]


class EmployeeCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Employee's full name",
        examples=["Neha Singh"],
    )

    email: EmailStr = Field(
        ...,
        description="Employee's valid email address",
        examples=["neha@example.com"],
    )

    department: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Employee department",
        examples=["Engineering"],
    )

    salary: float = Field(
        ...,
        ge=MIN_SALARY,
        le=MAX_SALARY,
        description="Employee annual salary",
        examples=[80000],
    )

    joining_date: date = Field(
        ...,
        description="Employee joining date and it cannot be in the future",
        examples=["2025-01-10"],
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Employee password",
        examples=["securepass123"],
    )

    is_admin: bool = Field(
        default=False,
        description="Whether the employee has admin privileges",
        examples=[False],
    )

    @field_validator("name", "department")
    @classmethod
    def validate_text(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty")

        return value

    @field_validator("joining_date")
    @classmethod
    def validate_joining_date(cls, value):
        if value > date.today():
            raise ValueError("Joining date cannot be in the future")

        return value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Neha Singh",
                "email": "neha@example.com",
                "department": "Engineering",
                "salary": 80000,
                "joining_date": "2025-01-10",
                "password": "securepass123",
                "is_admin": False,
            }
        }
    )


class EmployeeUpdate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Employee's full name",
        examples=["Neha Singh"],
    )

    email: EmailStr = Field(
        ...,
        description="Employee's valid email address",
        examples=["neha.updated@example.com"],
    )

    department: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Employee department",
        examples=["AI Engineering"],
    )

    salary: float = Field(
        ...,
        ge=MIN_SALARY,
        le=MAX_SALARY,
        description="Employee annual salary",
        examples=[90000],
    )

    joining_date: date = Field(
        ...,
        description="Employee joining date and it cannot be in the future",
        examples=["2025-01-10"],
    )

    @field_validator("name", "department")
    @classmethod
    def validate_text(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty")

        return value

    @field_validator("joining_date")
    @classmethod
    def validate_joining_date(cls, value):
        if value > date.today():
            raise ValueError("Joining date cannot be in the future")

        return value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Neha Singh",
                "email": "neha.updated@example.com",
                "department": "AI Engineering",
                "salary": 90000,
                "joining_date": "2025-01-10",
            }
        }
    )


class EmployeePartialUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Employee's full name",
        examples=["Neha Singh"],
    )

    email: Optional[EmailStr] = Field(
        default=None,
        description="Employee's valid email address",
        examples=["neha.updated@example.com"],
    )

    department: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50,
        description="Employee department",
        examples=["AI Engineering"],
    )

    salary: Optional[float] = Field(
        default=None,
        ge=MIN_SALARY,
        le=MAX_SALARY,
        description="Employee annual salary",
        examples=[95000],
    )

    joining_date: Optional[date] = Field(
        default=None,
        description="Employee joining date and it cannot be in the future",
        examples=["2025-01-10"],
    )

    @field_validator("name", "department")
    @classmethod
    def validate_text(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty")

        return value

    @field_validator("joining_date")
    @classmethod
    def validate_joining_date(cls, value):
        if value is not None and value > date.today():
            raise ValueError("Joining date cannot be in the future")

        return value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "department": "AI Engineering",
                "salary": 95000,
            }
        }
    )


class EmployeeResponse(BaseModel):
    id: int = Field(
        ...,
        description="Unique employee ID",
        examples=[1],
    )

    name: str = Field(
        ...,
        description="Employee's full name",
        examples=["Rahul Sharma"],
    )

    email: EmailStr = Field(
        ...,
        description="Employee's valid email address",
        examples=["rahul@example.com"],
    )

    department: str = Field(
        ...,
        description="Employee department",
        examples=["Engineering"],
    )

    salary: float = Field(
        ...,
        description="Employee annual salary",
        examples=[75000],
    )

    joining_date: date = Field(
        ...,
        description="Employee joining date",
        examples=["2024-01-15"],
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Rahul Sharma",
                "email": "rahul@example.com",
                "department": "Engineering",
                "salary": 75000,
                "joining_date": "2024-01-15",
            }
        },
    )


def find_employee(employee_id: int):
    for employee in EMPLOYEES:
        if employee["id"] == employee_id:
            return employee

    return None


def check_duplicate_email(
    email: str,
    exclude_employee_id: Optional[int] = None,
):
    for employee in EMPLOYEES:
        if (
            employee["email"].lower() == email.lower()
            and employee["id"] != exclude_employee_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )


@app.get(
    "/",
    tags=["General"],
    summary="API health message",
    description="Returns a message confirming that the Employee Management API is running.",
)
def home():
    return {
        "message": "Employee Management API is running"
    }


@app.post(
    "/employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Employees"],
    summary="Create a new employee",
    description="Create a new employee after validating the request body.",
)
def create_employee(employee: EmployeeCreate):
    check_duplicate_email(str(employee.email))

    new_id = max(
        [employee["id"] for employee in EMPLOYEES],
        default=0,
    ) + 1

    new_employee = {
        "id": new_id,
        "name": employee.name,
        "email": str(employee.email),
        "department": employee.department,
        "salary": employee.salary,
        "joining_date": employee.joining_date,
        "password": employee.password,
        "is_admin": employee.is_admin,
    }

    EMPLOYEES.append(new_employee)

    return new_employee


@app.get(
    "/employees",
    response_model=list[EmployeeResponse],
    status_code=status.HTTP_200_OK,
    tags=["Employees"],
    summary="Get all employees",
    description="Return all employees without exposing sensitive internal fields.",
)
def get_employees():
    return EMPLOYEES


@app.get(
    "/employees/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
    tags=["Employees"],
    summary="Get employee by ID",
    description="Return an employee using the employee ID.",
)
def get_employee(
    employee_id: int = Path(
        ...,
        gt=0,
        description="Unique employee ID",
        examples=[1],
    )
):
    employee = find_employee(employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    return employee


@app.put(
    "/employees/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
    tags=["Employees"],
    summary="Fully update an employee",
    description="Replace all editable information of an existing employee.",
)
def update_employee(
    employee: EmployeeUpdate,
    employee_id: int = Path(
        ...,
        gt=0,
        description="Unique employee ID",
        examples=[1],
    ),
):
    existing_employee = find_employee(employee_id)

    if existing_employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    check_duplicate_email(
        str(employee.email),
        exclude_employee_id=employee_id,
    )

    existing_employee["name"] = employee.name
    existing_employee["email"] = str(employee.email)
    existing_employee["department"] = employee.department
    existing_employee["salary"] = employee.salary
    existing_employee["joining_date"] = employee.joining_date

    return existing_employee


@app.patch(
    "/employees/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
    tags=["Employees"],
    summary="Partially update an employee",
    description="Update only the fields supplied by the client.",
)
def partial_update_employee(
    employee: EmployeePartialUpdate,
    employee_id: int = Path(
        ...,
        gt=0,
        description="Unique employee ID",
        examples=[1],
    ),
):
    existing_employee = find_employee(employee_id)

    if existing_employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    update_data = employee.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided",
        )

    if "email" in update_data:
        check_duplicate_email(
            str(update_data["email"]),
            exclude_employee_id=employee_id,
        )
        update_data["email"] = str(update_data["email"])

    existing_employee.update(update_data)

    return existing_employee


@app.delete(
    "/employees/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Employees"],
    summary="Delete an employee",
    description="Delete an existing employee by employee ID.",
)
def delete_employee(
    employee_id: int = Path(
        ...,
        gt=0,
        description="Unique employee ID",
        examples=[1],
    )
):
    employee = find_employee(employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    EMPLOYEES.remove(employee)

    return None                                                 
