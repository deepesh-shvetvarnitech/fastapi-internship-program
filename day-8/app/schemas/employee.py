from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmployeeCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    department_id: int = Field(gt=0)


class EmployeeUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    department_id: int = Field(gt=0)


class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    department_id: int

    model_config = ConfigDict(from_attributes=True)