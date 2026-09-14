from typing import Literal

from fastapi import Header, HTTPException, Query, Request


def pagination(
    page: int = Query(
        default=1,
        ge=1,
        description="Page number",
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of records per page",
    ),
) -> dict:
    offset = (page - 1) * page_size

    return {
        "page": page,
        "page_size": page_size,
        "offset": offset,
    }


def request_metadata(
    request: Request,
    user_agent: str | None = Header(default=None),
    x_request_id: str | None = Header(default=None),
) -> dict:
    return {
        "method": request.method,
        "path": request.url.path,
        "user_agent": user_agent,
        "request_id": x_request_id,
    }


TicketStatus = Literal[
    "open",
    "in_progress",
    "resolved",
    "closed",
]


def ticket_filters(
    status: TicketStatus | None = Query(default=None),
    department: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
) -> dict:
    return {
        "status": status,
        "department": department,
        "is_active": is_active,
    }


EXPECTED_API_KEY = "development-secret-key"


def api_key_verification(
    x_api_key: str | None = Header(
        default=None,
        alias="X-API-Key",
    ),
) -> str:
    if x_api_key != EXPECTED_API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API key",
        )

    return x_api_key