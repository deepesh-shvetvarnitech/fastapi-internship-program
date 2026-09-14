from fastapi import APIRouter, Depends

from app.dependencies import (
    api_key_verification,
    pagination,
    request_metadata,
    ticket_filters,
)


router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)


tickets = [
    {
        "id": 1,
        "title": "Login issue",
        "status": "open",
        "department": "IT",
        "is_active": True,
    },
    {
        "id": 2,
        "title": "Payment failed",
        "status": "in_progress",
        "department": "Finance",
        "is_active": True,
    },
    {
        "id": 3,
        "title": "Account locked",
        "status": "resolved",
        "department": "IT",
        "is_active": True,
    },
    {
        "id": 4,
        "title": "Old ticket",
        "status": "closed",
        "department": "Support",
        "is_active": False,
    },
    {
        "id": 5,
        "title": "Password reset",
        "status": "open",
        "department": "IT",
        "is_active": True,
    },
    {
        "id": 6,
        "title": "Refund request",
        "status": "in_progress",
        "department": "Finance",
        "is_active": True,
    },
]


@router.get("")
def get_tickets(
    pagination_data: dict = Depends(pagination),
    filters: dict = Depends(ticket_filters),
):
    filtered_tickets = tickets

    if filters["status"] is not None:
        filtered_tickets = [
            ticket
            for ticket in filtered_tickets
            if ticket["status"] == filters["status"]
        ]

    if filters["department"] is not None:
        filtered_tickets = [
            ticket
            for ticket in filtered_tickets
            if ticket["department"] == filters["department"]
        ]

    if filters["is_active"] is not None:
        filtered_tickets = [
            ticket
            for ticket in filtered_tickets
            if ticket["is_active"] == filters["is_active"]
        ]

    offset = pagination_data["offset"]
    page_size = pagination_data["page_size"]

    paginated_tickets = filtered_tickets[
        offset:offset + page_size
    ]

    return {
        "page": pagination_data["page"],
        "page_size": page_size,
        "total": len(filtered_tickets),
        "tickets": paginated_tickets,
    }


@router.get("/metadata")
def get_metadata(
    metadata: dict = Depends(request_metadata),
):
    return {
        "message": "Request metadata",
        "metadata": metadata,
    }


@router.get("/secure-data")
def get_secure_data(
    key: str = Depends(api_key_verification),
):
    return {
        "message": "Access granted",
        "data": "This is secure data",
    }