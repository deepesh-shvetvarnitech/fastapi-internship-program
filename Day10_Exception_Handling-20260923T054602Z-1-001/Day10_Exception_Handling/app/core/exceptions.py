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


class TaskDeleteConflictError(AppException):
    def __init__(self):
        super().__init__(
            code="TASK_DELETE_CONFLICT",
            message="Task could not be deleted because of a database constraint.",
            status_code=409,
        )