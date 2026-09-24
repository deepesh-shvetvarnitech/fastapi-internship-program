Absolutely. Since **Day 9 established Route → Service → Repository**, Day 10 is the right point to introduce a proper **application-level exception architecture**.

One important improvement from the Day 9 design: **don't keep using `ValueError` + checking message strings** such as `"not found" in detail`. That becomes fragile very quickly. For Day 10, we'll replace those with explicit custom exceptions and let **global exception handlers** convert them into consistent HTTP responses.

Your target architecture becomes:

```text
HTTP Request
    │
    ▼
FastAPI Route
    │
    ▼
Service Layer
    │
    ├── raises EmployeeNotFoundError
    ├── raises DuplicateEmailError
    ├── raises TaskNotFoundError
    └── raises InvalidTaskStateError
    │
    ▼
Global Exception Handler
    │
    ▼
Consistent JSON Response
```

For example:

```json
{
  "error": {
    "code": "EMPLOYEE_NOT_FOUND",
    "message": "Employee does not exist.",
    "request_id": "req-123"
  }
}
```

## 1. Day 10 folder structure

I recommend adding a `core/exceptions.py` and `core/exception_handlers.py`:

```text
Day_9/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── exceptions.py              ← NEW
│   │   └── exception_handlers.py      ← NEW
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

---

# 2. First: define application exceptions

Create:

```text
app/core/exceptions.py
```

Use a common base exception so all application errors have the same structure.

```python
class AppException(Exception):
    """
    Base exception for application-level errors.
    """

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code

        super().__init__(message)


class EmployeeNotFoundError(AppException):
    def __init__(self, employee_id: int):
        super().__init__(
            code="EMPLOYEE_NOT_FOUND",
            message="Employee does not exist.",
            status_code=404,
        )
        self.employee_id = employee_id


class TaskNotFoundError(AppException):
    def __init__(self, task_id: int):
        super().__init__(
            code="TASK_NOT_FOUND",
            message="Task does not exist.",
            status_code=404,
        )
        self.task_id = task_id


class DuplicateEmailError(AppException):
    def __init__(self, email: str | None = None):
        super().__init__(
            code="DUPLICATE_EMAIL",
            message="An employee with this email already exists.",
            status_code=409,
        )
        self.email = email


class InvalidTaskStateError(AppException):
    def __init__(self, state: str):
        super().__init__(
            code="INVALID_TASK_STATE",
            message="The provided task state is not valid.",
            status_code=422,
        )
        self.state = state


class DepartmentNotFoundError(AppException):
    def __init__(self, department_id: int):
        super().__init__(
            code="DEPARTMENT_NOT_FOUND",
            message="Department does not exist.",
            status_code=404,
        )
        self.department_id = department_id


class DuplicateDepartmentCodeError(AppException):
    def __init__(self):
        super().__init__(
            code="DUPLICATE_DEPARTMENT_CODE",
            message="A department with this code already exists.",
            status_code=409,
        )


class DepartmentDeleteConflictError(AppException):
    def __init__(self):
        super().__init__(
            code="DEPARTMENT_DELETE_CONFLICT",
            message="Department cannot be deleted because employees are assigned to it.",
            status_code=409,
        )


class EmployeeDeleteConflictError(AppException):
    def __init__(self):
        super().__init__(
            code="EMPLOYEE_DELETE_CONFLICT",
            message="Employee cannot be deleted because related tasks exist.",
            status_code=409,
        )


class EmployeeNotFoundForTaskError(AppException):
    def __init__(self, employee_id: int):
        super().__init__(
            code="EMPLOYEE_NOT_FOUND",
            message="Employee does not exist.",
            status_code=404,
        )
        self.employee_id = employee_id
```

### Why have `AppException`?

Instead of:

```python
raise ValueError("Employee not found")
```

we now have:

```python
raise EmployeeNotFoundError(employee_id)
```

The exception itself carries:

```text
code
message
HTTP status
```

So the route doesn't need to understand business-error strings.

---

# 3. Global exception handlers

Create:

```text
app/core/exception_handlers.py
```

This is where we convert application exceptions into HTTP responses.

```python
import uuid

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import AppException


def get_request_id(request: Request) -> str:
    """
    Return the request ID assigned to the request.

    If middleware already assigned one, reuse it.
    Otherwise generate one.
    """

    request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    if request_id is None:
        request_id = f"req-{uuid.uuid4().hex[:12]}"
        request.state.request_id = request_id

    return request_id


async def app_exception_handler(
    request: Request,
    exc: AppException,
):
    request_id = get_request_id(request)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": request_id,
            }
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    request_id = get_request_id(request)

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed.",
                "request_id": request_id,
                "details": exc.errors(),
            }
        },
    )


async def integrity_error_handler(
    request: Request,
    exc: IntegrityError,
):
    request_id = get_request_id(request)

    return JSONResponse(
        status_code=409,
        content={
            "error": {
                "code": "DATABASE_INTEGRITY_ERROR",
                "message": "The request violates a database constraint.",
                "request_id": request_id,
            }
        },
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
):
    request_id = get_request_id(request)

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
                "request_id": request_id,
            }
        },
    )
```

---

# 4. Why the request ID matters

You specifically want:

```json
"request_id": "req-123"
```

This becomes extremely useful when you have:

```text
Client
   │
   │ request_id=req-a1b2c3
   ▼
FastAPI
   │
   ├── logs
   ├── database
   ├── service
   └── monitoring
```

If the user receives:

```json
{
  "error": {
    "code": "EMPLOYEE_NOT_FOUND",
    "message": "Employee does not exist.",
    "request_id": "req-a1b2c3"
  }
}
```

you can search your logs for:

```text
req-a1b2c3
```

and investigate that particular request.

This becomes particularly valuable later when you add your observability stack.

---

# 5. Add request ID middleware

Now modify:

```text
app/main.py
```

Add middleware that creates a request ID for every request.

A clean Day 10 implementation:

```python
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

from app.api.router import api_router
from app.core.exceptions import AppException
from app.core.exception_handlers import (
    app_exception_handler,
    generic_exception_handler,
    integrity_error_handler,
    validation_exception_handler,
)


app = FastAPI(
    title="Employee Task Management API",
    description="FastAPI + SQLAlchemy + PostgreSQL CRUD API",
    version="1.0.0",
)


# ============================================================
# REQUEST ID MIDDLEWARE
# ============================================================

@app.middleware("http")
async def request_id_middleware(
    request: Request,
    call_next,
):
    request_id = request.headers.get(
        "X-Request-ID"
    )

    if not request_id:
        request_id = f"req-{uuid.uuid4().hex[:12]}"

    request.state.request_id = request_id

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    return response


# ============================================================
# GLOBAL EXCEPTION HANDLERS
# ============================================================

app.add_exception_handler(
    AppException,
    app_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    IntegrityError,
    integrity_error_handler,
)

app.add_exception_handler(
    Exception,
    generic_exception_handler,
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(
    api_router,
    prefix="/api/v1",
)


# ============================================================
# SYSTEM ENDPOINTS
# ============================================================

@app.get(
    "/",
    tags=["System"],
)
def root():
    return {
        "message": "Employee Task Management API",
        "version": "1.0.0",
    }


@app.get(
    "/health",
    tags=["System"],
)
def health():
    return {
        "status": "healthy",
    }
```

---

# 6. Now change EmployeeService

This is where Day 10 becomes important.

Instead of:

```python
raise ValueError("Employee not found")
```

we use:

```python
raise EmployeeNotFoundError(employee_id)
```

Your `app/services/employee_service.py` should become:

```python
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    DepartmentNotFoundError,
    DuplicateEmailError,
    EmployeeDeleteConflictError,
    EmployeeNotFoundError,
)
from app.db.models import Employee
from app.repositories.department_repository import DepartmentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
)


class EmployeeService:

    def __init__(self, db: Session):
        self.db = db

        self.employee_repository = EmployeeRepository(
            db
        )

        self.department_repository = DepartmentRepository(
            db
        )

    # ========================================================
    # CREATE EMPLOYEE
    # ========================================================

    def create_employee(
        self,
        employee_data: EmployeeCreate,
    ) -> Employee:

        department = (
            self.department_repository.get_by_id(
                employee_data.department_id
            )
        )

        if department is None:
            raise DepartmentNotFoundError(
                employee_data.department_id
            )

        existing_employee = (
            self.employee_repository.get_by_email(
                str(employee_data.email)
            )
        )

        if existing_employee is not None:
            raise DuplicateEmailError(
                str(employee_data.email)
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

            # Database remains the final authority
            raise DuplicateEmailError(
                str(employee_data.email)
            )

        return employee

    # ========================================================
    # GET EMPLOYEE
    # ========================================================

    def get_employee(
        self,
        employee_id: int,
    ) -> Employee:

        employee = (
            self.employee_repository.get_by_id(
                employee_id
            )
        )

        if employee is None:
            raise EmployeeNotFoundError(
                employee_id
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

        employee = (
            self.employee_repository.get_by_id(
                employee_id
            )
        )

        if employee is None:
            raise EmployeeNotFoundError(
                employee_id
            )

        department = (
            self.department_repository.get_by_id(
                employee_data.department_id
            )
        )

        if department is None:
            raise DepartmentNotFoundError(
                employee_data.department_id
            )

        existing_employee = (
            self.employee_repository.get_by_email(
                str(employee_data.email)
            )
        )

        if (
            existing_employee is not None
            and existing_employee.id != employee_id
        ):
            raise DuplicateEmailError(
                str(employee_data.email)
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

            raise DuplicateEmailError(
                str(employee_data.email)
            )

        return employee

    # ========================================================
    # DELETE EMPLOYEE
    # ========================================================

    def delete_employee(
        self,
        employee_id: int,
    ) -> None:

        employee = (
            self.employee_repository.get_by_id(
                employee_id
            )
        )

        if employee is None:
            raise EmployeeNotFoundError(
                employee_id
            )

        try:
            self.employee_repository.delete(
                employee
            )

            self.db.commit()

        except IntegrityError:
            self.db.rollback()

            raise EmployeeDeleteConflictError()
```

Now the service doesn't know anything about HTTP.

It simply says:

```python
raise EmployeeNotFoundError(employee_id)
```

The global handler decides that this means:

```text
HTTP 404
EMPLOYEE_NOT_FOUND
```

That's the separation we want.

---

# Department Service:
`app\services\department_service.py`:
```python
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    DepartmentDeleteConflictError,
    DepartmentNotFoundError,
    DuplicateDepartmentCodeError,
)
from app.db.models import Department
from app.repositories.department_repository import DepartmentRepository
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
)


class DepartmentService:

    def __init__(self, db: Session):
        self.db = db

        self.department_repository = DepartmentRepository(
            db
        )

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
                raise DuplicateDepartmentCodeError()

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

            # Database is the final authority
            # for uniqueness constraints.
            raise DuplicateDepartmentCodeError()

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
            raise DepartmentNotFoundError(
                department_id
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
            raise DepartmentNotFoundError(
                department_id
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
                raise DuplicateDepartmentCodeError()

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

            raise DuplicateDepartmentCodeError()

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
            raise DepartmentNotFoundError(
                department_id
            )

        try:

            self.department_repository.delete(
                department
            )

            self.db.commit()

        except IntegrityError:

            self.db.rollback()

            raise DepartmentDeleteConflictError()

```


# 7. TaskService

Now implement the task-specific exceptions.

`app/services/task_service.py`:

```python
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    EmployeeNotFoundForTaskError,
    InvalidTaskStateError,
    TaskNotFoundError,
)
from app.db.models import Task
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
)


VALID_TASK_STATES = {
    "pending",
    "in_progress",
    "completed",
}


class TaskService:

    def __init__(self, db: Session):
        self.db = db

        self.task_repository = TaskRepository(
            db
        )

        self.employee_repository = EmployeeRepository(
            db
        )

    # ========================================================
    # VALIDATE TASK STATE
    # ========================================================

    def _validate_task_state(
        self,
        state: str,
    ) -> None:

        if state not in VALID_TASK_STATES:
            raise InvalidTaskStateError(
                state
            )

    # ========================================================
    # CREATE TASK
    # ========================================================

    def create_task(
        self,
        task_data: TaskCreate,
    ) -> Task:

        self._validate_task_state(
            task_data.status
        )

        employee = (
            self.employee_repository.get_by_id(
                task_data.employee_id
            )
        )

        if employee is None:
            raise EmployeeNotFoundForTaskError(
                task_data.employee_id
            )

        task = Task(
            title=task_data.title,
            description=task_data.description,
            employee_id=task_data.employee_id,
            status=task_data.status,
        )

        try:
            self.task_repository.create(task)

            self.db.commit()
            self.db.refresh(task)

        except IntegrityError:
            self.db.rollback()

            raise EmployeeNotFoundForTaskError(
                task_data.employee_id
            )

        return task

    # ========================================================
    # GET TASK
    # ========================================================

    def get_task(
        self,
        task_id: int,
    ) -> Task:

        task = (
            self.task_repository.get_by_id(
                task_id
            )
        )

        if task is None:
            raise TaskNotFoundError(
                task_id
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

        employee = (
            self.employee_repository.get_by_id(
                employee_id
            )
        )

        if employee is None:
            raise EmployeeNotFoundForTaskError(
                employee_id
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

        task = (
            self.task_repository.get_by_id(
                task_id
            )
        )

        if task is None:
            raise TaskNotFoundError(
                task_id
            )

        self._validate_task_state(
            task_data.status
        )

        employee = (
            self.employee_repository.get_by_id(
                task_data.employee_id
            )
        )

        if employee is None:
            raise EmployeeNotFoundForTaskError(
                task_data.employee_id
            )

        task.title = task_data.title
        task.description = task_data.description
        task.employee_id = task_data.employee_id
        task.status = task_data.status

        try:
            self.task_repository.update(task)

            self.db.commit()
            self.db.refresh(task)

        except IntegrityError:
            self.db.rollback()

            raise EmployeeNotFoundForTaskError(
                task_data.employee_id
            )

        return task

    # ========================================================
    # DELETE TASK
    # ========================================================

    def delete_task(
        self,
        task_id: int,
    ) -> None:

        task = (
            self.task_repository.get_by_id(
                task_id
            )
        )

        if task is None:
            raise TaskNotFoundError(
                task_id
            )

        try:
            self.task_repository.delete(task)

            self.db.commit()

        except IntegrityError:
            self.db.rollback()

            raise InvalidTaskStateError(
                "delete"
            )
```

### One thing I would change here

The last part:

```python
raise InvalidTaskStateError("delete")
```

is not semantically correct.

A database error while deleting a task is **not necessarily an invalid task state**.

So let's add one more exception:

```python
class TaskDeleteConflictError(AppException):
    def __init__(self):
        super().__init__(
            code="TASK_DELETE_CONFLICT",
            message="Task could not be deleted because of a database constraint.",
            status_code=409,
        )
```

Then import it:

```python
from app.core.exceptions import (
    EmployeeNotFoundForTaskError,
    InvalidTaskStateError,
    TaskDeleteConflictError,
    TaskNotFoundError,
)
```

and use:

```python
except IntegrityError:
    self.db.rollback()
    raise TaskDeleteConflictError()
```

That's the production-correct semantic.

---

# 8. Important point about `InvalidTaskStateError`

Your Pydantic schema already has:

```python
TaskStatus = Literal[
    "pending",
    "in_progress",
    "completed",
]
```

So invalid input such as:

```json
{
  "title": "Test",
  "employee_id": 1,
  "status": "unknown"
}
```

will normally be rejected by **Pydantic/FastAPI validation before the service is called**.

Therefore, you technically won't normally reach:

```python
InvalidTaskStateError
```

from the HTTP API.

But keeping the service validation is still valuable because the service can potentially be called from:

```text
API
Background Job
CLI
Admin script
Celery worker
Internal service
```

So:

```text
Pydantic
   ↓
API input validation

Service
   ↓
business/domain validation
```

is a good design.

---

# 9. Refactor Employee routes

Now your routes become much cleaner.

There should be **no `try/except ValueError` blocks**.

`app/api/routes/employees.py`:

```python
from fastapi import (
    APIRouter,
    Depends,
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


router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_session),
):
    service = EmployeeService(db)

    return service.create_employee(
        employee_data
    )


@router.get(
    "",
    response_model=list[EmployeeResponse],
)
def get_employees(
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_session),
):
    service = EmployeeService(db)

    return service.get_employees(
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_session),
):
    service = EmployeeService(db)

    return service.get_employee(
        employee_id
    )


@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_session),
):
    service = EmployeeService(db)

    return service.update_employee(
        employee_id=employee_id,
        employee_data=employee_data,
    )


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_session),
):
    service = EmployeeService(db)

    service.delete_employee(
        employee_id
    )

    return None
```

Notice how clean the route became.

No:

```python
except ValueError
```

No:

```python
if "not found" in detail
```

No:

```python
HTTPException(...)
```

for application business errors.

---

# 10. Refactor Task routes

`app/api/routes/tasks.py`:

```python
from fastapi import (
    APIRouter,
    Depends,
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
# CREATE
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

    return service.create_task(
        task_data
    )


# ============================================================
# LIST
# ============================================================

@router.get(
    "",
    response_model=list[TaskResponse],
)
def get_tasks(
    page: int = Query(
        1,
        ge=1,
    ),
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
# EMPLOYEE TASKS
# ============================================================

@router.get(
    "/employee/{employee_id}",
    response_model=list[TaskResponse],
)
def get_employee_tasks(
    employee_id: int,
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_session),
):
    service = TaskService(db)

    return service.get_employee_tasks(
        employee_id=employee_id,
        page=page,
        page_size=page_size,
    )


# ============================================================
# GET BY ID
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

    return service.get_task(
        task_id
    )


# ============================================================
# UPDATE
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

    return service.update_task(
        task_id=task_id,
        task_data=task_data,
    )


# ============================================================
# DELETE
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

    service.delete_task(
        task_id
    )

    return None
```

---

# 11. Department routes

Department routes can also become completely clean.

```python
from fastapi import (
    APIRouter,
    Depends,
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

    return service.create_department(
        department_data
    )


@router.get(
    "",
    response_model=list[DepartmentResponse],
)
def get_departments(
    page: int = Query(
        1,
        ge=1,
    ),
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


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def get_department(
    department_id: int,
    db: Session = Depends(get_session),
):
    service = DepartmentService(db)

    return service.get_department(
        department_id
    )


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

    return service.update_department(
        department_id=department_id,
        department_data=department_data,
    )


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_department(
    department_id: int,
    db: Session = Depends(get_session),
):
    service = DepartmentService(db)

    service.delete_department(
        department_id
    )

    return None
```

---

# 12. Update DepartmentService exceptions

Your DepartmentService should also stop raising `ValueError`.

For example:

```python
from app.core.exceptions import (
    DepartmentDeleteConflictError,
    DepartmentNotFoundError,
    DuplicateDepartmentCodeError,
)
```

Then change:

```python
raise ValueError("Department not found")
```

to:

```python
raise DepartmentNotFoundError(
    department_id
)
```

Change:

```python
raise ValueError(
    "Department code already exists"
)
```

to:

```python
raise DuplicateDepartmentCodeError()
```

And:

```python
raise ValueError(
    "Department cannot be deleted because "
    "employees are assigned to it"
)
```

to:

```python
raise DepartmentDeleteConflictError()
```

The rest of your DepartmentService transaction logic can remain as implemented in Day 9.

---

# 13. What about `HTTPException`?

You specifically listed:

> `HTTPException`

We still support it.

The important distinction is **where** we use it.

### Application/service errors

Use:

```python
raise EmployeeNotFoundError(employee_id)
```

### Route-specific HTTP errors

`HTTPException` can still be used for an HTTP-only condition.

For example:

```python
raise HTTPException(
    status_code=401,
    detail="Authentication required",
)
```

But don't do this inside the service:

```python
# ❌ Don't do this
class EmployeeService:

    def get_employee(...):
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )
```

because now your service is coupled to FastAPI.

Better:

```text
Service
  ↓
EmployeeNotFoundError
  ↓
Global Handler
  ↓
HTTP 404
```

---

# 14. Validation error response

Now suppose you send:

```json
{
  "name": "A",
  "email": "invalid-email",
  "department_id": -1
}
```

FastAPI/Pydantic rejects it.

Instead of the default FastAPI response, you'll get something like:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed.",
    "request_id": "req-a82f92d19abc",
    "details": [
      {
        "type": "string_too_short",
        "loc": [
          "body",
          "name"
        ]
      }
    ]
  }
}
```

That's much more consistent for frontend/mobile/API consumers.

---

# 15. Employee not found

Request:

```text
GET /api/v1/employees/99999
```

Service:

```python
raise EmployeeNotFoundError(99999)
```

Global handler:

```text
EmployeeNotFoundError
       ↓
app_exception_handler
       ↓
404
```

Response:

```json
{
  "error": {
    "code": "EMPLOYEE_NOT_FOUND",
    "message": "Employee does not exist.",
    "request_id": "req-4f82c91a2b11"
  }
}
```

---

# 16. Duplicate email

Request:

```http
POST /api/v1/employees
```

```json
{
  "name": "Rahul",
  "email": "existing@example.com",
  "department_id": 1
}
```

Service detects:

```python
raise DuplicateEmailError(...)
```

Response:

```json
{
  "error": {
    "code": "DUPLICATE_EMAIL",
    "message": "An employee with this email already exists.",
    "request_id": "req-9c13ab72f8e1"
  }
}
```

HTTP status:

```text
409 Conflict
```

---

# 17. Task not found

```text
GET /api/v1/tasks/99999
```

Response:

```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task does not exist.",
    "request_id": "req-61a82b9e4d20"
  }
}
```

HTTP:

```text
404 Not Found
```

---

# 18. Database integrity error

This is an important production concept.

Even if we perform:

```python
existing_employee = repository.get_by_email(...)
```

another request could insert the same email between our `SELECT` and `INSERT`.

Therefore:

```text
Application check
       ↓
Helpful
       ↓
Database UNIQUE constraint
       ↓
Authoritative
```

If PostgreSQL raises:

```python
IntegrityError
```

we rollback:

```python
self.db.rollback()
```

and convert it into an application-level error.

This gives us two protection layers:

```text
Layer 1
Service business check

       +

Layer 2
PostgreSQL constraint
```

That's exactly what you want in a production-oriented backend.

---

# 19. One important improvement to the IntegrityError handler

For Day 10 learning, the generic handler:

```python
IntegrityError
    ↓
DATABASE_INTEGRITY_ERROR
```

is acceptable.

But there is an important production nuance.

Not every `IntegrityError` means duplicate email.

It could be:

```text
UNIQUE violation
FOREIGN KEY violation
CHECK violation
NOT NULL violation
```

So **don't blindly convert every database error to `DUPLICATE_EMAIL`**.

The better long-term architecture is:

```text
IntegrityError
       ↓
inspect PostgreSQL constraint
       ↓
map constraint → domain exception
```

We'll eventually improve this when you reach the database/security/testing phase.

For Day 10, keeping a generic fallback is correct.

---

# 20. Final Day 10 architecture

Your application now becomes:

```text
                    ┌─────────────────────┐
                    │     HTTP Request    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Request Middleware│
                    │    Request ID       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       Route         │
                    │  HTTP responsibility │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Service        │
                    │  Business rules     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┴────────────────┐
              ▼                                 ▼
      ┌───────────────┐                 ┌───────────────┐
      │  Repository   │                 │   Repository  │
      │   Employee    │                 │   Department  │
      └───────┬───────┘                 └───────┬───────┘
              │                                 │
              └────────────────┬────────────────┘
                               ▼
                         PostgreSQL
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
             Success response       Database error
                                          │
                                          ▼
                                  IntegrityError
                                          │
                                          ▼
                                  Global Handler
```

And application exceptions follow:

```text
EmployeeService
      │
      └── EmployeeNotFoundError
                  │
                  ▼
       Global Exception Handler
                  │
                  ▼
             HTTP 404
                  │
                  ▼
        Standard JSON Response
```

---

# 21. Your Day 10 error contract

I recommend making this your application's error contract:

| Situation                   | HTTP | Code                         |
| --------------------------- | ---: | ---------------------------- |
| Employee missing            |  404 | `EMPLOYEE_NOT_FOUND`         |
| Task missing                |  404 | `TASK_NOT_FOUND`             |
| Department missing          |  404 | `DEPARTMENT_NOT_FOUND`       |
| Duplicate email             |  409 | `DUPLICATE_EMAIL`            |
| Duplicate department code   |  409 | `DUPLICATE_DEPARTMENT_CODE`  |
| Employee delete conflict    |  409 | `EMPLOYEE_DELETE_CONFLICT`   |
| Department delete conflict  |  409 | `DEPARTMENT_DELETE_CONFLICT` |
| Task delete conflict        |  409 | `TASK_DELETE_CONFLICT`       |
| Invalid task state          |  422 | `INVALID_TASK_STATE`         |
| Request validation failure  |  422 | `VALIDATION_ERROR`           |
| Unknown database constraint |  409 | `DATABASE_INTEGRITY_ERROR`   |
| Unexpected server error     |  500 | `INTERNAL_SERVER_ERROR`      |

Every error has:

```json
{
  "error": {
    "code": "...",
    "message": "...",
    "request_id": "..."
  }
}
```

Validation errors additionally have:

```json
"details": [...]
```

---

# 22. Day 10 testing checklist

After implementation, test these one by one.

### Test 1 — Employee not found

```text
GET /api/v1/employees/99999
```

Expected:

```text
404
EMPLOYEE_NOT_FOUND
```

### Test 2 — Duplicate email

Create an employee twice using the same email.

Expected:

```text
409
DUPLICATE_EMAIL
```

### Test 3 — Task not found

```text
GET /api/v1/tasks/99999
```

Expected:

```text
404
TASK_NOT_FOUND
```

### Test 4 — Missing employee for task

```json
{
  "title": "Test task",
  "description": "Testing errors",
  "employee_id": 99999,
  "status": "pending"
}
```

Expected:

```text
404
EMPLOYEE_NOT_FOUND
```

### Test 5 — Invalid request body

```json
{
  "name": "A",
  "email": "abc",
  "department_id": -1
}
```

Expected:

```text
422
VALIDATION_ERROR
```

### Test 6 — Invalid task status

From Swagger/API client:

```json
{
  "title": "Testing task",
  "description": "Invalid status",
  "employee_id": 1,
  "status": "cancelled"
}
```

Expected:

```text
422
VALIDATION_ERROR
```

because your `Literal` catches it before the service.

### Test 7 — Request ID

Send:

```http
X-Request-ID: req-test-001
```

Then trigger an error.

Expected:

```json
{
  "error": {
    "code": "EMPLOYEE_NOT_FOUND",
    "message": "Employee does not exist.",
    "request_id": "req-test-001"
  }
}
```

And the response header should contain:

```http
X-Request-ID: req-test-001
```

### Test 8 — Unknown exception

Temporarily create a test endpoint:

```python
@app.get("/test-error")
def test_error():
    raise RuntimeError("Something unexpected happened")
```

Call:

```text
GET /test-error
```

Expected:

```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected error occurred.",
    "request_id": "req-..."
  }
}
```

**Do not expose the actual exception message to the client.** That is an important production security practice.

---

## What you've learned by the end of Day 10

The progression is now:

```text
Day 8
FastAPI CRUD
     ↓
Day 9
Route → Service → Repository
     ↓
Day 10
Custom Exceptions
     ↓
Global Exception Handlers
     ↓
Consistent Error Contract
     ↓
Request Correlation ID
     ↓
Database Error Handling
```

And the key architectural rule to teach your intern is:

> **Services raise business/application exceptions. Routes should not translate those exceptions individually. Global handlers translate them into HTTP responses.**

That is a much stronger foundation for your later **testing, authentication, observability, Redis, load testing, and production deployment** phases.



# --------------------------------------------------------
# Remaining Info
# -------------------------------------------------------

Yes — I found the exact problem. Your **global exception handler is already correct**, and `DepartmentNotFoundError` is already defined correctly. The problem is that `DepartmentService` is **still raising `ValueError`**.

Because `ValueError` is not handled by your `app_exception_handler`, it falls through to:

```python
generic_exception_handler()
```

and you get:

```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected error occurred."
  }
}
```

So the fix is to make `DepartmentService` raise your custom exceptions.

## 1. Replace `department_service.py`

Use this complete version:

```python
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    DepartmentDeleteConflictError,
    DepartmentNotFoundError,
    DuplicateDepartmentCodeError,
)
from app.db.models import Department
from app.repositories.department_repository import DepartmentRepository
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
)


class DepartmentService:

    def __init__(self, db: Session):
        self.db = db

        self.department_repository = DepartmentRepository(
            db
        )

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
                raise DuplicateDepartmentCodeError()

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

            # Database is the final authority
            # for uniqueness constraints.
            raise DuplicateDepartmentCodeError()

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
            raise DepartmentNotFoundError(
                department_id
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
            raise DepartmentNotFoundError(
                department_id
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
                raise DuplicateDepartmentCodeError()

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

            raise DuplicateDepartmentCodeError()

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
            raise DepartmentNotFoundError(
                department_id
            )

        try:

            self.department_repository.delete(
                department
            )

            self.db.commit()

        except IntegrityError:

            self.db.rollback()

            raise DepartmentDeleteConflictError()
```

---

# 2. What changed?

There are three important replacements.

### Before

```python
if department is None:
    raise ValueError(
        "Department not found"
    )
```

### Now

```python
if department is None:
    raise DepartmentNotFoundError(
        department_id
    )
```

Your global handler recognizes `DepartmentNotFoundError` because it inherits from:

```python
AppException
```

Therefore:

```text
DepartmentService
       ↓
DepartmentNotFoundError
       ↓
AppException
       ↓
app_exception_handler
       ↓
HTTP 404
```

---

# 3. Test Department GET

Restart your server:

```powershell
uvicorn app.main:app --reload
```

Then call:

```text
GET /api/v1/departments/99999
```

Assuming department `99999` doesn't exist.

You should now receive:

```json
{
  "error": {
    "code": "DEPARTMENT_NOT_FOUND",
    "message": "Department does not exist.",
    "request_id": "req-a83f72c91b20"
  }
}
```

HTTP status:

```text
404 Not Found
```

This is exactly the behavior you want for Day 10.

---

# 4. Test duplicate department code

Suppose you already have:

```json
{
  "id": 1,
  "name": "Engineering",
  "code": "ENG"
}
```

Then send:

```json
{
  "name": "Engineering 2",
  "code": "ENG"
}
```

Your service now raises:

```python
DuplicateDepartmentCodeError()
```

The global handler produces:

```json
{
  "error": {
    "code": "DUPLICATE_DEPARTMENT_CODE",
    "message": "A department with this code already exists.",
    "request_id": "req-..."
  }
}
```

HTTP:

```text
409 Conflict
```

---

# 5. Test department update with nonexistent ID

Send:

```text
PUT /api/v1/departments/99999
```

with:

```json
{
  "name": "New Department",
  "code": "NEW"
}
```

Expected:

```json
{
  "error": {
    "code": "DEPARTMENT_NOT_FOUND",
    "message": "Department does not exist.",
    "request_id": "req-..."
  }
}
```

Status:

```text
404
```

---

# 6. Test department delete with nonexistent ID

```text
DELETE /api/v1/departments/99999
```

Expected:

```json
{
  "error": {
    "code": "DEPARTMENT_NOT_FOUND",
    "message": "Department does not exist.",
    "request_id": "req-..."
  }
}
```

Status:

```text
404
```

---

# 7. Your `exceptions.py` is already correct for Department

You already have:

```python
class DepartmentNotFoundError(AppException):
    def __init__(self, department_id: int):
        super().__init__(
            code="DEPARTMENT_NOT_FOUND",
            message="Department does not exist.",
            status_code=404,
        )
        self.department_id = department_id
```

And:

```python
class DuplicateDepartmentCodeError(AppException):
    def __init__(self):
        super().__init__(
            code="DUPLICATE_DEPARTMENT_CODE",
            message="A department with this code already exists.",
            status_code=409,
        )
```

And:

```python
class DepartmentDeleteConflictError(AppException):
    def __init__(self):
        super().__init__(
            code="DEPARTMENT_DELETE_CONFLICT",
            message="Department cannot be deleted because employees are assigned to it.",
            status_code=409,
        )
```

So **you don't need to change these for this issue.**

---

# 8. Your `exception_handlers.py` is also handling it correctly

This is the important part:

```python
async def app_exception_handler(
    request: Request,
    exc: AppException,
):
```

Because:

```text
DepartmentNotFoundError
        ↓
AppException
```

FastAPI can route it to:

```python
app_exception_handler
```

which produces:

```python
{
    "error": {
        "code": exc.code,
        "message": exc.message,
        "request_id": request_id,
    }
}
```

So the handler itself wasn't the problem.

---

# 9. The real Day 10 rule

You should now eliminate **application-level `ValueError`** from your services.

Your architecture should be:

```text
                    ROUTE
                      │
                      ▼
                   SERVICE
                      │
          ┌───────────┼────────────┐
          │           │            │
          ▼           ▼            ▼
    EmployeeError  TaskError  DepartmentError
          │           │            │
          └───────────┼────────────┘
                      ▼
                AppException
                      │
                      ▼
          Global Exception Handler
                      │
                      ▼
                JSON Response
```

Instead of the old:

```text
Service
   ↓
ValueError
   ↓
???
   ↓
500 Internal Server Error
```

---

# 10. One more thing I recommend checking

You should now search your three services for:

```python
raise ValueError
```

There should ideally be **none** left for application/business errors.

Check:

```text
app/services/
├── employee_service.py
├── department_service.py
└── task_service.py
```

You should have custom exceptions everywhere:

```text
EmployeeService
├── EmployeeNotFoundError
├── DuplicateEmailError
├── DepartmentNotFoundError
└── EmployeeDeleteConflictError

DepartmentService
├── DepartmentNotFoundError
├── DuplicateDepartmentCodeError
└── DepartmentDeleteConflictError

TaskService
├── TaskNotFoundError
├── EmployeeNotFoundForTaskError
├── InvalidTaskStateError
└── TaskDeleteConflictError
```

That gives you a consistent **Day 10 exception architecture**.

One nuance: your current `IntegrityError` handling in `DepartmentService` assumes every create/update integrity failure means a duplicate department code. That's acceptable for this learning phase, but later we'll improve it by inspecting the actual PostgreSQL constraint so a foreign-key/check/unique failure gets the correct error code rather than being mislabeled.
