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


# async def validation_exception_handler(
#     request: Request,
#     exc: RequestValidationError,
# ):
#     request_id = get_request_id(request)

#     return JSONResponse(
#         status_code=422,
#         content={
#             "error": {
#                 "code": "VALIDATION_ERROR",
#                 "message": "Request validation failed.",
#                 "request_id": request_id,
#                 "details": exc.errors(),
#             }
#         },
#     )



async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    request_id = get_request_id(request)

    details = []

    for error in exc.errors():
        location = error.get("loc", ())

        error_detail = {
            "type": error.get("type"),
            "loc": location,
            "msg": error.get("msg"),
        }

        # Convert non-JSON-serializable objects such as
        # ValueError(...) into strings.
        if "ctx" in error:
            ctx = error["ctx"].copy()

            if "error" in ctx:
                ctx["error"] = str(ctx["error"])

            error_detail["ctx"] = ctx

        details.append(error_detail)

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed.",
                "request_id": request_id,
                "details": details,
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