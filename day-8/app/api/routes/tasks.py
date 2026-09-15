from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Employee, Task
from app.db.session import get_session
from app.schemas.task import TaskCreate, TaskResponse

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_session)
):
    employee = db.get(
        Employee,
        task_data.employee_id
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    task = Task(
        title=task_data.title,
        description=task_data.description,
        employee_id=task_data.employee_id,
        status=task_data.status
    )

    db.add(task)

    try:
        db.commit()
        db.refresh(task)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task could not be created"
        )

    return task