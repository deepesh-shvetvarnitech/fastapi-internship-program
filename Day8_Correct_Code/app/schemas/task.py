from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TaskStatus = Literal[
    "pending",
    "in_progress",
    "completed",
]


class TaskCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=200,
    )

    description: str | None = None

    employee_id: int = Field(
        gt=0,
    )

    status: TaskStatus = "pending"


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    employee_id: int
    status: TaskStatus

    model_config = ConfigDict(
        from_attributes=True
    )