from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=5, max_length=1000)
    employee_id: int = Field(gt=0)
    status: Literal["pending", "in_progress", "completed"]


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    employee_id: int
    status: str

    model_config = ConfigDict(from_attributes=True)