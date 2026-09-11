from typing import Literal

from fastapi import APIRouter, HTTPException, Path, Query, status
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/tickets",
    tags=["TICKETS"]
)


class TicketCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    priority: Literal["low", "medium", "high", "critical"]
    category: Literal["hardware", "software", "network", "access", "other"]
    assigned_to: str | None = None


class TicketUpdate(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    priority: Literal["low", "medium", "high", "critical"]
    category: Literal["hardware", "software", "network", "access", "other"]
    assigned_to: str | None = None
    is_active: bool


class TicketPatch(BaseModel):
    title: str | None = Field(None, min_length=5, max_length=100)
    description: str | None = Field(None, min_length=10, max_length=500)
    priority: Literal["low", "medium", "high", "critical"] | None = None
    category: Literal["hardware", "software", "network", "access", "other"] | None = None
    assigned_to: str | None = None
    is_active: bool | None = None


tickets = [
    {
        "id": 101,
        "title": "Laptop not starting",
        "description": "Employee laptop is not powering on",
        "priority": "high",
        "category": "hardware",
        "assigned_to": "Rahul",
        "is_active": True
    },
    {
        "id": 102,
        "title": "VPN connection issue",
        "description": "Unable to connect to company VPN",
        "priority": "critical",
        "category": "network",
        "assigned_to": "Amit",
        "is_active": True
    },
    {
        "id": 103,
        "title": "Software installation",
        "description": "Need installation of required software",
        "priority": "medium",
        "category": "software",
        "assigned_to": None,
        "is_active": True
    }
]


def find_ticket(ticket_id: int):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket
    return None


@router.get("/")
def get_tickets(
    priority: Literal["low", "medium", "high", "critical"] | None = None,
    category: Literal["hardware", "software", "network", "access", "other"] | None = None,
    is_active: bool | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    filtered_tickets = tickets

    if priority:
        filtered_tickets = [
            ticket for ticket in filtered_tickets
            if ticket["priority"] == priority
        ]

    if category:
        filtered_tickets = [
            ticket for ticket in filtered_tickets
            if ticket["category"] == category
        ]

    if is_active is not None:
        filtered_tickets = [
            ticket for ticket in filtered_tickets
            if ticket["is_active"] == is_active
        ]

    if search:
        filtered_tickets = [
            ticket for ticket in filtered_tickets
            if search.lower() in ticket["title"].lower()
            or search.lower() in ticket["description"].lower()
        ]

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total": len(filtered_tickets),
        "tickets": filtered_tickets[start:end]
    }


@router.get("/stats")
def get_ticket_stats():
    total = len(tickets)

    active = sum(
        1 for ticket in tickets
        if ticket["is_active"] is True
    )

    inactive = sum(
        1 for ticket in tickets
        if ticket["is_active"] is False
    )

    critical = sum(
        1 for ticket in tickets
        if ticket["priority"] == "critical"
    )

    unassigned = sum(
        1 for ticket in tickets
        if ticket["assigned_to"] is None
    )

    return {
        "total": total,
        "active": active,
        "inactive": inactive,
        "critical": critical,
        "unassigned": unassigned
    }


@router.get("/summary")
def get_ticket_summary():
    total_tickets = len(tickets)

    active_tickets = sum(
        1 for ticket in tickets
        if ticket["is_active"] is True
    )

    critical_tickets = sum(
        1 for ticket in tickets
        if ticket["priority"] == "critical"
    )

    unassigned_tickets = sum(
        1 for ticket in tickets
        if ticket["assigned_to"] is None
    )

    return {
        "total_tickets": total_tickets,
        "active_tickets": active_tickets,
        "critical_tickets": critical_tickets,
        "unassigned_tickets": unassigned_tickets
    }


@router.get("/{ticket_id}")
def get_ticket(
    ticket_id: int = Path(..., gt=0)
):
    ticket = find_ticket(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    return ticket


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED
)
def create_ticket(ticket_data: TicketCreate):
    new_id = max(ticket["id"] for ticket in tickets) + 1

    new_ticket = {
        "id": new_id,
        **ticket_data.model_dump(),
        "is_active": True
    }

    tickets.append(new_ticket)

    return new_ticket


@router.put("/{ticket_id}")
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate
):
    ticket = find_ticket(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    ticket.update(ticket_data.model_dump())

    return ticket


@router.patch("/{ticket_id}")
def patch_ticket(
    ticket_id: int,
    ticket_data: TicketPatch
):
    ticket = find_ticket(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    update_data = ticket_data.model_dump(exclude_unset=True)

    ticket.update(update_data)

    return ticket


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_ticket(ticket_id: int):
    ticket = find_ticket(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    tickets.remove(ticket)