Day_9/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── session.py
│   │   └── models.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── employee.py
│   │   ├── department.py
│   │   └── task.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── employee_repository.py
│   │   ├── department_repository.py
│   │   └── task_repository.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── employee_service.py
│   │   ├── department_service.py
│   │   └── task_service.py
│   │
│   └── api/
│       ├── __init__.py
│       ├── router.py
│       │
│       └── routes/
│           ├── __init__.py
│           ├── employees.py
│           ├── departments.py
│           └── tasks.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md


########################################################################
Yes. I checked the progression you shared, and you have **already implemented most of the repository/service layer**. The main work now is to make the three resources consistent:

* Department → Repository + Service + Route
* Employee → Repository + Service + Route
* Task → Repository + Service + Route

There are also **three issues in the current code** that I recommend fixing now:

1. Your imports use inconsistent filenames: `departments_repository.py` vs `department_repository.py`.
2. `EmployeeService.update_employee()` bypasses `EmployeeRepository.update()`.
3. `tasks.py` is still Day 8 code and has not been moved to the Service/Repository architecture.
4. Your current `ValueError` → HTTP status handling is fragile; for Day 9, we can first keep it simple, but I'll make the route handling more reliable.

I would **not change your database models or database data** for this refactor.

---

# 1. Final structure I recommend

Keep your existing structure, but standardize the names:

```text
Day_9/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── session.py
│   │   └── models.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── employee.py
│   │   ├── department.py
│   │   └── task.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── employee_repository.py
│   │   ├── department_repository.py
│   │   └── task_repository.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── employee_service.py
│   │   ├── department_service.py
│   │   └── task_service.py
│   │
│   └── api/
│       ├── __init__.py
│       ├── router.py
│       │
│       └── routes/
│           ├── __init__.py
│           ├── employees.py
│           ├── departments.py
│           └── tasks.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

### Rename these if necessary

You currently have:

```text
departments_repository.py
departments_service.py
```

I recommend:

```text
department_repository.py
department_service.py
```

because your classes are:

```python
DepartmentRepository
DepartmentService
```

and your other resources are singular.

---

# 2. Repository layer

Your repositories are mostly correct. However, I recommend making all three consistent.

## `app/repositories/department_repository.py`

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Department


class DepartmentRepository:

    def __init__(self, db: Session):
        self.db = db

    # ========================================================
    # GET BY ID
    # ========================================================

    def get_by_id(
        self,
        department_id: int,
    ) -> Department | None:

        return self.db.get(
            Department,
            department_id,
        )

    # ========================================================
    # GET BY CODE
    # ========================================================

    def get_by_code(
        self,
        code: str,
    ) -> Department | None:

        statement = select(Department).where(
            Department.code == code
        )

        return self.db.scalar(statement)

    # ========================================================
    # GET ALL
    # ========================================================

    def get_all(
        self,
        offset: int,
        limit: int,
    ) -> list[Department]:

        statement = (
            select(Department)
            .order_by(Department.id)
            .offset(offset)
            .limit(limit)
        )

        return list(
            self.db.scalars(statement).all()
        )

    # ========================================================
    # CREATE
    # ========================================================

    def create(
        self,
        department: Department,
    ) -> Department:

        self.db.add(department)

        return department

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        department: Department,
    ) -> Department:

        return department

    # ========================================================
    # DELETE
    # ========================================================

    def delete(
        self,
        department: Department,
    ) -> None:

        self.db.delete(department)
```

### Important difference

Notice that I removed:

```python
self.db.commit()
self.db.refresh(...)
```

from the repository.

That's intentional.

---

# 3. Why remove `commit()` from Repository?

This is an important Day 9 concept.

You currently have:

```text
Service
   ↓
Repository
   ↓
commit()
```

Instead, we want:

```text
Service
   ↓
Repository
   ↓
db.add()
   ↓
Service
   ↓
commit()
```

The **service owns the business transaction**.

This becomes very important when one business operation touches multiple repositories.

For example:

```text
Create Employee
       │
       ├── DepartmentRepository
       │
       ├── EmployeeRepository
       │
       └── AuditRepository
              │
              ▼
           COMMIT
```

Either everything succeeds or everything can be rolled back.

That's a better foundation for production code.

---

# 4. Employee Repository

Replace your current employee repository with:

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Employee


class EmployeeRepository:

    def __init__(self, db: Session):
        self.db = db

    # ========================================================
    # GET BY ID
    # ========================================================

    def get_by_id(
        self,
        employee_id: int,
    ) -> Employee | None:

        return self.db.get(
            Employee,
            employee_id,
        )

    # ========================================================
    # GET BY EMAIL
    # ========================================================

    def get_by_email(
        self,
        email: str,
    ) -> Employee | None:

        statement = select(Employee).where(
            Employee.email == email
        )

        return self.db.scalar(statement)

    # ========================================================
    # GET ALL
    # ========================================================

    def get_all(
        self,
        offset: int,
        limit: int,
    ) -> list[Employee]:

        statement = (
            select(Employee)
            .order_by(Employee.id)
            .offset(offset)
            .limit(limit)
        )

        return list(
            self.db.scalars(statement).all()
        )

    # ========================================================
    # CREATE
    # ========================================================

    def create(
        self,
        employee: Employee,
    ) -> Employee:

        self.db.add(employee)

        return employee

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        employee: Employee,
    ) -> Employee:

        return employee

    # ========================================================
    # DELETE
    # ========================================================

    def delete(
        self,
        employee: Employee,
    ) -> None:

        self.db.delete(employee)
```

---

# 5. Task Repository

Replace your current repository with:

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Task


class TaskRepository:

    def __init__(self, db: Session):
        self.db = db

    # ========================================================
    # GET BY ID
    # ========================================================

    def get_by_id(
        self,
        task_id: int,
    ) -> Task | None:

        return self.db.get(
            Task,
            task_id,
        )

    # ========================================================
    # GET ALL
    # ========================================================

    def get_all(
        self,
        offset: int,
        limit: int,
    ) -> list[Task]:

        statement = (
            select(Task)
            .order_by(Task.id)
            .offset(offset)
            .limit(limit)
        )

        return list(
            self.db.scalars(statement).all()
        )

    # ========================================================
    # GET BY EMPLOYEE
    # ========================================================

    def get_by_employee(
        self,
        employee_id: int,
        offset: int,
        limit: int,
    ) -> list[Task]:

        statement = (
            select(Task)
            .where(
                Task.employee_id == employee_id
            )
            .order_by(Task.id)
            .offset(offset)
            .limit(limit)
        )

        return list(
            self.db.scalars(statement).all()
        )

    # ========================================================
    # CREATE
    # ========================================================

    def create(
        self,
        task: Task,
    ) -> Task:

        self.db.add(task)

        return task

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        task: Task,
    ) -> Task:

        return task

    # ========================================================
    # DELETE
    # ========================================================

    def delete(
        self,
        task: Task,
    ) -> None:

        self.db.delete(task)
```

---

# 6. Employee Service

Your current service is close, but let's make transaction handling consistent.

Replace:

```text
app/services/employee_service.py
```

with:

```python
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Employee
from app.repositories.department_repository import DepartmentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


class EmployeeService:

    def __init__(self, db: Session):

        self.db = db

        self.employee_repository = EmployeeRepository(db)

        self.department_repository = DepartmentRepository(db)

    # ========================================================
    # CREATE EMPLOYEE
    # ========================================================

    def create_employee(
        self,
        employee_data: EmployeeCreate,
    ) -> Employee:

        # Business Rule:
        # Employee must belong to an existing department.

        department = self.department_repository.get_by_id(
            employee_data.department_id
        )

        if department is None:
            raise ValueError(
                f"Department with ID "
                f"{employee_data.department_id} not found"
            )

        # Business Rule:
        # Employee email must be unique.

        existing_employee = (
            self.employee_repository.get_by_email(
                str(employee_data.email)
            )
        )

        if existing_employee is not None:
            raise ValueError(
                "Employee with this email already exists"
            )

        employee = Employee(
            name=employee_data.name,
            email=str(employee_data.email),
            department_id=employee_data.department_id,
        )

        try:

            self.employee_repository.create(
                employee
            )

            self.db.commit()
            self.db.refresh(employee)

        except IntegrityError:

            self.db.rollback()

            raise ValueError(
                "Employee could not be created because "
                "of a database constraint"
            )

        return employee

    # ========================================================
    # GET EMPLOYEE
    # ========================================================

    def get_employee(
        self,
        employee_id: int,
    ) -> Employee:

        employee = self.employee_repository.get_by_id(
            employee_id
        )

        if employee is None:
            raise ValueError(
                "Employee not found"
            )

        return employee

    # ========================================================
    # LIST EMPLOYEES
    # ========================================================

    def get_employees(
        self,
        page: int,
        page_size: int,
    ) -> list[Employee]:

        offset = (page - 1) * page_size

        return self.employee_repository.get_all(
            offset=offset,
            limit=page_size,
        )

    # ========================================================
    # UPDATE EMPLOYEE
    # ========================================================

    def update_employee(
        self,
        employee_id: int,
        employee_data: EmployeeUpdate,
    ) -> Employee:

        employee = self.employee_repository.get_by_id(
            employee_id
        )

        if employee is None:
            raise ValueError(
                "Employee not found"
            )

        # Business Rule:
        # Department must exist.

        department = self.department_repository.get_by_id(
            employee_data.department_id
        )

        if department is None:
            raise ValueError(
                f"Department with ID "
                f"{employee_data.department_id} not found"
            )

        # Business Rule:
        # Email must remain unique.

        existing_employee = (
            self.employee_repository.get_by_email(
                str(employee_data.email)
            )
        )

        if (
            existing_employee is not None
            and existing_employee.id != employee_id
        ):
            raise ValueError(
                "Another employee already uses this email"
            )

        employee.name = employee_data.name
        employee.email = str(employee_data.email)
        employee.department_id = (
            employee_data.department_id
        )

        try:

            self.employee_repository.update(
                employee
            )

            self.db.commit()
            self.db.refresh(employee)

        except IntegrityError:

            self.db.rollback()

            raise ValueError(
                "Employee could not be updated because "
                "of a database constraint"
            )

        return employee

    # ========================================================
    # DELETE EMPLOYEE
    # ========================================================

    def delete_employee(
        self,
        employee_id: int,
    ) -> None:

        employee = self.employee_repository.get_by_id(
            employee_id
        )

        if employee is None:
            raise ValueError(
                "Employee not found"
            )

        try:

            self.employee_repository.delete(
                employee
            )

            self.db.commit()

        except IntegrityError:

            self.db.rollback()

            raise ValueError(
                "Employee cannot be deleted because "
                "related records exist"
            )
```

Now all employee database writes follow:

```text
Service
 ↓
Repository
 ↓
db.add/delete
 ↓
Service
 ↓
commit
```

---

# 7. Department Service

Your existing Department Service is conceptually good. Replace it with this transaction-consistent version:

```python
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Department
from app.repositories.department_repository import DepartmentRepository
from app.schemas.department import DepartmentCreate, DepartmentUpdate


class DepartmentService:

    def __init__(self, db: Session):

        self.db = db

        self.department_repository = DepartmentRepository(db)

    # ========================================================
    # CREATE DEPARTMENT
    # ========================================================

    def create_department(
        self,
        department_data: DepartmentCreate,
    ) -> Department:

        # Business Rule:
        # Department code must be unique.

        if department_data.code is not None:

            existing_department = (
                self.department_repository.get_by_code(
                    department_data.code
                )
            )

            if existing_department is not None:
                raise ValueError(
                    "Department code already exists"
                )

        department = Department(
            name=department_data.name,
            code=department_data.code,
        )

        try:

            self.department_repository.create(
                department
            )

            self.db.commit()
            self.db.refresh(department)

        except IntegrityError:

            self.db.rollback()

            raise ValueError(
                "Department could not be created because "
                "of a database constraint"
            )

        return department

    # ========================================================
    # GET DEPARTMENT
    # ========================================================

    def get_department(
        self,
        department_id: int,
    ) -> Department:

        department = (
            self.department_repository.get_by_id(
                department_id
            )
        )

        if department is None:
            raise ValueError(
                "Department not found"
            )

        return department

    # ========================================================
    # LIST DEPARTMENTS
    # ========================================================

    def get_departments(
        self,
        page: int,
        page_size: int,
    ) -> list[Department]:

        offset = (page - 1) * page_size

        return self.department_repository.get_all(
            offset=offset,
            limit=page_size,
        )

    # ========================================================
    # UPDATE DEPARTMENT
    # ========================================================

    def update_department(
        self,
        department_id: int,
        department_data: DepartmentUpdate,
    ) -> Department:

        department = (
            self.department_repository.get_by_id(
                department_id
            )
        )

        if department is None:
            raise ValueError(
                "Department not found"
            )

        # Business Rule:
        # Department code must remain unique.

        if department_data.code is not None:

            existing_department = (
                self.department_repository.get_by_code(
                    department_data.code
                )
            )

            if (
                existing_department is not None
                and existing_department.id != department_id
            ):
                raise ValueError(
                    "Department code already exists"
                )

        department.name = department_data.name
        department.code = department_data.code

        try:

            self.department_repository.update(
                department
            )

            self.db.commit()
            self.db.refresh(department)

        except IntegrityError:

            self.db.rollback()

            raise ValueError(
                "Department could not be updated because "
                "of a database constraint"
            )

        return department

    # ========================================================
    # DELETE DEPARTMENT
    # ========================================================

    def delete_department(
        self,
        department_id: int,
    ) -> None:

        department = (
            self.department_repository.get_by_id(
                department_id
            )
        )

        if department is None:
            raise ValueError(
                "Department not found"
            )

        try:

            self.department_repository.delete(
                department
            )

            self.db.commit()

        except IntegrityError:

            self.db.rollback()

            raise ValueError(
                "Department cannot be deleted because "
                "employees are assigned to it"
            )
```

---

# 8. Task Service

Your Task Service is also close, but change it to use the transaction pattern consistently and add `TaskUpdate`.

Use:

```text
app/services/task_service.py
```

```python
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Task
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:

    def __init__(self, db: Session):

        self.db = db

        self.task_repository = TaskRepository(db)

        self.employee_repository = EmployeeRepository(db)

    # ========================================================
    # CREATE TASK
    # ========================================================

    def create_task(
        self,
        task_data: TaskCreate,
    ) -> Task:

        # Business Rule:
        # Task must belong to an existing employee.

        employee = self.employee_repository.get_by_id(
            task_data.employee_id
        )

        if employee is None:
            raise ValueError(
                f"Employee with ID "
                f"{task_data.employee_id} not found"
            )

        task = Task(
            title=task_data.title,
            description=task_data.description,
            employee_id=task_data.employee_id,
            status=task_data.status,
        )

        try:

            self.task_repository.create(
                task
            )

            self.db.commit()
            self.db.refresh(task)

        except IntegrityError:

            self.db.rollback()

            raise ValueError(
                "Task could not be created because "
                "of a database constraint"
            )

        return task

    # ========================================================
    # GET TASK
    # ========================================================

    def get_task(
        self,
        task_id: int,
    ) -> Task:

        task = self.task_repository.get_by_id(
            task_id
        )

        if task is None:
            raise ValueError(
                "Task not found"
            )

        return task

    # ========================================================
    # LIST TASKS
    # ========================================================

    def get_tasks(
        self,
        page: int,
        page_size: int,
    ) -> list[Task]:

        offset = (page - 1) * page_size

        return self.task_repository.get_all(
            offset=offset,
            limit=page_size,
        )

    # ========================================================
    # GET EMPLOYEE TASKS
    # ========================================================

    def get_employee_tasks(
        self,
        employee_id: int,
        page: int,
        page_size: int,
    ) -> list[Task]:

        employee = self.employee_repository.get_by_id(
            employee_id
        )

        if employee is None:
            raise ValueError(
                "Employee not found"
            )

        offset = (page - 1) * page_size

        return self.task_repository.get_by_employee(
            employee_id=employee_id,
            offset=offset,
            limit=page_size,
        )

    # ========================================================
    # UPDATE TASK
    # ========================================================

    def update_task(
        self,
        task_id: int,
        task_data: TaskUpdate,
    ) -> Task:

        task = self.task_repository.get_by_id(
            task_id
        )

        if task is None:
            raise ValueError(
                "Task not found"
            )

        # Business Rule:
        # New employee must exist.

        employee = self.employee_repository.get_by_id(
            task_data.employee_id
        )

        if employee is None:
            raise ValueError(
                f"Employee with ID "
                f"{task_data.employee_id} not found"
            )

        task.title = task_data.title
        task.description = task_data.description
        task.employee_id = task_data.employee_id
        task.status = task_data.status

        try:

            self.task_repository.update(
                task
            )

            self.db.commit()
            self.db.refresh(task)

        except IntegrityError:

            self.db.rollback()

            raise ValueError(
                "Task could not be updated because "
                "of a database constraint"
            )

        return task

    # ========================================================
    # DELETE TASK
    # ========================================================

    def delete_task(
        self,
        task_id: int,
    ) -> None:

        task = self.task_repository.get_by_id(
            task_id
        )

        if task is None:
            raise ValueError(
                "Task not found"
            )

        try:

            self.task_repository.delete(
                task
            )

            self.db.commit()

        except IntegrityError:

            self.db.rollback()

            raise ValueError(
                "Task could not be deleted because "
                "of a database constraint"
            )
```

---

# 9. Update Task schema

Your current Task schema needs `TaskUpdate`.

Use:

```text
app/schemas/task.py
```

```python
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


class TaskUpdate(BaseModel):

    title: str = Field(
        min_length=3,
        max_length=200,
    )

    description: str | None = None

    employee_id: int = Field(
        gt=0,
    )

    status: TaskStatus


class TaskResponse(BaseModel):

    id: int
    title: str
    description: str | None
    employee_id: int
    status: TaskStatus

    model_config = ConfigDict(
        from_attributes=True,
    )
```

---

# 10. Your biggest remaining problem: `tasks.py`

This is still Day 8 architecture:

```python
employee = db.get(...)
db.add(task)
db.commit()
```

We need to replace it.

Use this for:

```text
app/api/routes/tasks.py
```

```python
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.task import (
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)
from app.services.task_service import TaskService


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


# ============================================================
# CREATE TASK
# ============================================================

@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_session),
):

    service = TaskService(db)

    try:

        return service.create_task(
            task_data
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ============================================================
# GET TASK BY ID
# ============================================================

@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
def get_task(
    task_id: int,
    db: Session = Depends(get_session),
):

    service = TaskService(db)

    try:

        return service.get_task(
            task_id
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ============================================================
# LIST TASKS
# ============================================================

@router.get(
    "",
    response_model=list[TaskResponse],
)
def get_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_session),
):

    service = TaskService(db)

    return service.get_tasks(
        page=page,
        page_size=page_size,
    )


# ============================================================
# GET TASKS BY EMPLOYEE
# ============================================================

@router.get(
    "/employee/{employee_id}",
    response_model=list[TaskResponse],
)
def get_employee_tasks(
    employee_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_session),
):

    service = TaskService(db)

    try:

        return service.get_employee_tasks(
            employee_id=employee_id,
            page=page,
            page_size=page_size,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ============================================================
# UPDATE TASK
# ============================================================

@router.put(
    "/{task_id}",
    response_model=TaskResponse,
)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_session),
):

    service = TaskService(db)

    try:

        return service.update_task(
            task_id=task_id,
            task_data=task_data,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ============================================================
# DELETE TASK
# ============================================================

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_session),
):

    service = TaskService(db)

    try:

        service.delete_task(
            task_id
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    return None
```

---

# 11. Important route ordering issue

You should put:

```python
@router.get("/employee/{employee_id}")
```

**before**:

```python
@router.get("/{task_id}")
```

as shown above.

Otherwise `/employee/1` can potentially be interpreted as:

```text
task_id = "employee"
```

The explicit static route should come before the dynamic route.

This is a useful FastAPI routing concept for your intern.

---

# 12. Refactor `departments.py`

Your current Department route is still doing direct DB operations.

It should now be:

```python
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.services.department_service import DepartmentService


router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


# ============================================================
# CREATE
# ============================================================

@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_department(
    department_data: DepartmentCreate,
    db: Session = Depends(get_session),
):

    service = DepartmentService(db)

    try:

        return service.create_department(
            department_data
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


# ============================================================
# GET BY ID
# ============================================================

@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def get_department(
    department_id: int,
    db: Session = Depends(get_session),
):

    service = DepartmentService(db)

    try:

        return service.get_department(
            department_id
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ============================================================
# LIST
# ============================================================

@router.get(
    "",
    response_model=list[DepartmentResponse],
)
def get_departments(
    page: int = Query(1, ge=1),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_session),
):

    service = DepartmentService(db)

    return service.get_departments(
        page=page,
        page_size=page_size,
    )


# ============================================================
# UPDATE
# ============================================================

@router.put(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    db: Session = Depends(get_session),
):

    service = DepartmentService(db)

    try:

        return service.update_department(
            department_id,
            department_data,
        )

    except ValueError as exc:

        detail = str(exc)

        if "not found" in detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=detail,
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


# ============================================================
# DELETE
# ============================================================

@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_department(
    department_id: int,
    db: Session = Depends(get_session),
):

    service = DepartmentService(db)

    try:

        service.delete_department(
            department_id
        )

    except ValueError as exc:

        detail = str(exc)

        if "not found" in detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=detail,
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )

    return None
```

Now Department route contains no SQLAlchemy query.

---

# 13. Employee route

Your existing employee route is already mostly refactored correctly.

Keep it, with one improvement: use the service only.

The imports should be:

```python
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
)
from app.services.employee_service import EmployeeService
```

There should be **no**:

```python
from app.db.models import Employee
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
```

inside this route.

That's the whole point of the refactor.

---

# 14. `router.py`

Your current router is already correct.

Keep:

```python
from fastapi import APIRouter

from app.api.routes.departments import router as department_router
from app.api.routes.employees import router as employee_router
from app.api.routes.tasks import router as task_router


api_router = APIRouter()


api_router.include_router(
    department_router
)

api_router.include_router(
    employee_router
)

api_router.include_router(
    task_router
)
```

---

# 15. Business rules now have a clear home

Your Day 9 implementation should now have these rules.

### Department Service

```text
BR-D01
Department code must be unique.

BR-D02
Department must exist before update.

BR-D03
Department must exist before delete.

BR-D04
Department with dependent employees cannot be deleted.
```

### Employee Service

```text
BR-E01
Employee must belong to an existing department.

BR-E02
Employee email must be unique.

BR-E03
Employee must exist before update.

BR-E04
Employee must exist before delete.

BR-E05
Employee cannot be deleted when dependent records prevent deletion.
```

### Task Service

```text
BR-T01
Task must belong to an existing employee.

BR-T02
Employee must exist when changing task ownership.

BR-T03
Task must exist before update.

BR-T04
Task must exist before delete.

BR-T05
Task status must be one of:
       pending
       in_progress
       completed
```

The schema handles some of those rules:

```text
Pydantic
  ↓
input validation
```

while the service handles cross-entity rules:

```text
Service
  ↓
department exists?
employee exists?
email unique?
```

That's an important distinction.

---

# 16. Your final request flow

After implementing these files, creating an employee looks like:

```text
POST /api/v1/employees
          │
          ▼
EmployeeCreate
          │
          ▼
employees.py
          │
          ▼
EmployeeService
          │
          ├───────────────┐
          ▼               ▼
DepartmentRepository   EmployeeRepository
          │               │
          ▼               ▼
     department?       email?
          │               │
          └───────┬───────┘
                  ▼
          EmployeeRepository
                  │
                  ▼
               db.add()
                  │
                  ▼
          EmployeeService
                  │
                  ▼
             db.commit()
                  │
                  ▼
             PostgreSQL
```

That is the actual architectural improvement you're trying to learn in Day 9.

---

# 17. Testing after the refactor

Don't immediately test everything at once.

Use this sequence.

### Test 1 — Application startup

```powershell
uvicorn app.main:app --reload
```

Expected:

```text
Application startup complete.
```

No import errors.

---

### Test 2 — Swagger

Open:

```text
http://127.0.0.1:8000/docs
```

You should see:

```text
Departments
Employees
Tasks
```

---

### Test 3 — Department

```text
POST /api/v1/departments
```

```json
{
  "name": "Engineering",
  "code": "ENG"
}
```

Expected:

```text
201 Created
```

---

### Test 4 — Duplicate department

Send the same code:

```json
{
  "name": "Engineering 2",
  "code": "ENG"
}
```

Expected:

```text
409 Conflict
```

---

### Test 5 — Employee

Use a real department ID:

```json
{
  "name": "Arjun",
  "email": "arjun@gmail.com",
  "department_id": 1
}
```

Expected:

```text
201 Created
```

---

### Test 6 — Invalid department

```json
{
  "name": "Rahul",
  "email": "rahul@gmail.com",
  "department_id": 99999
}
```

Expected:

```text
404
Department with ID 99999 not found
```

---

### Test 7 — Task

Use an existing employee:

```json
{
  "title": "Implement authentication",
  "description": "Build JWT authentication",
  "employee_id": 1,
  "status": "pending"
}
```

Expected:

```text
201 Created
```

---

### Test 8 — Invalid employee

```json
{
  "title": "Test task",
  "description": "Testing business rule",
  "employee_id": 99999,
  "status": "pending"
}
```

Expected:

```text
404
Employee with ID 99999 not found
```

---

## One final architectural point

I would **not yet call this fully production-ready** even though it is now a good Day 9 layered architecture.

The next improvements should be:

```text
Day 9
Route
 ↓
Service
 ↓
Repository
 ↓
PostgreSQL
```

then progressively:

```text
Custom application exceptions
        ↓
Global exception handlers
        ↓
Proper transaction/UoW handling
        ↓
Repository interfaces
        ↓
Dependency injection for services
        ↓
Tests for Repository
        ↓
Tests for Service/business rules
        ↓
API integration tests
```

For your current learning stage, though, the most important thing is to **get this three-resource architecture working without changing your existing database**. The major missing piece in your current progression was `tasks.py`; after the files above, all three resources follow the same Route → Service → Repository pattern.
