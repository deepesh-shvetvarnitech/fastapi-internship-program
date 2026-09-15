from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...db.session import get_session
from ...db.models import Task, Employee
from ...schemas import TaskCreate, TaskResponse


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_session)
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == task.employee_id)
        .first()
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    new_task = Task(
        title=task.title,
        description=task.description,
        employee_id=task.employee_id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task