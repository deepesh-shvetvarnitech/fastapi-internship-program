from pydantic import BaseModel, ConfigDict, Field


class DepartmentCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )

    code: str | None = Field(
        default=None,
        min_length=2,
        max_length=20,
    )


class DepartmentUpdate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )

    code: str | None = Field(
        default=None,
        min_length=2,
        max_length=20,
    )


class DepartmentResponse(BaseModel):
    id: int
    name: str
    code: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )