from pydantic import BaseModel, EmailStr


class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    department: str


class EmployeeUpdate(BaseModel):
    name: str
    email: EmailStr
    department: str


class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    department: str

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    employee_id: int


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    employee_id: int

    class Config:
        from_attributes = True