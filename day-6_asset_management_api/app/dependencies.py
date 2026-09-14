from fastapi import Depends, Header, HTTPException, Query, Request
from typing import Literal, Optional

EXPECTED_API_KEY = "development-secret-key"


def pagination(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    offset = (page - 1) * page_size

    return {
        "page": page,
        "page_size": page_size,
        "offset": offset,
    }


def asset_filters(
    asset_type: Optional[
        Literal[
            "laptop",
            "monitor",
            "mobile",
            "keyboard",
            "mouse",
            "headset",
            "other",
        ]
    ] = Query(None),
    status: Optional[
        Literal[
            "available",
            "assigned",
            "maintenance",
            "retired",
            "lost",
        ]
    ] = Query(None),
    department: Optional[
        Literal[
            "Engineering",
            "HR",
            "Sales",
            "Finance",
            "Marketing",
            "Support",
        ]
    ] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    return {
        "asset_type": asset_type,
        "status": status,
        "department": department,
        "is_active": is_active,
    }


def request_metadata(
    request: Request,
    request_id: Optional[str] = Header(None, alias="X-Request-ID"),
):
    return {
        "method": request.method,
        "path": request.url.path,
        "user_agent": request.headers.get("User-Agent"),
        "request_id": request_id,
    }


def verify_api_key(
    api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    if api_key != EXPECTED_API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API key",
        )

    return api_key


def require_it_admin(
    api_key: str = Depends(verify_api_key),
):
    return {
        "role": "it_admin",
        "api_key": api_key,
    }


def get_audit_resource():
    print("Opening audit resource")

    resource = {
        "name": "audit-session"
    }

    try:
        yield resource
    finally:
        print("Closing audit resource")