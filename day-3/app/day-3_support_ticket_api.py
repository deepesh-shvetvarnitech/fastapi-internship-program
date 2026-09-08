from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Customer Support Ticket API",
    description="API for managing customer support tickets",
    version="1.0.0"
)

TICKETS = [
    {
        "id": 1,
        "customer_name": "Rahul Sharma",
        "subject": "Unable to login",
        "description": "I cannot login to my account.",
        "priority": "high",
        "status": "open"
    },
    {
        "id": 2,
        "customer_name": "Priya Patel",
        "subject": "Payment failed",
        "description": "My payment failed but money was deducted.",
        "priority": "high",
        "status": "in_progress"
    },
    {
        "id": 3,
        "customer_name": "Amit Kumar",
        "subject": "Change email address",
        "description": "I want to change my registered email.",
        "priority": "low",
        "status": "closed"
    }
]


class TicketCreate(BaseModel):
    customer_name: str = Field(..., min_length=1)
    subject: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    priority: str


class TicketUpdate(BaseModel):
    subject: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    priority: str


@app.get("/")
def home():
    return {
        "message": "Customer Support Ticket API is running"
    }


@app.get("/tickets")
def list_tickets(
    search: str | None = Query(None, min_length=2),
    status: str | None = Query(None),
    priority: str | None = Query(None)
):
    results = TICKETS

    if search:
        search_text = search.lower()

        results = [
            ticket for ticket in results
            if search_text in ticket["customer_name"].lower()
            or search_text in ticket["subject"].lower()
        ]

    if status:
        results = [
            ticket for ticket in results
            if ticket["status"] == status
        ]

    if priority:
        results = [
            ticket for ticket in results
            if ticket["priority"] == priority
        ]

    return results


@app.get("/tickets/{ticket_id}")
def get_ticket(
    ticket_id: int = Path(..., gt=0)
):
    for ticket in TICKETS:
        if ticket["id"] == ticket_id:
            return ticket

    raise HTTPException(
        status_code=404,
        detail="Ticket not found"
    )


@app.post("/tickets", status_code=201)
def create_ticket(ticket: TicketCreate):

    if ticket.priority not in ["low", "medium", "high"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid priority"
        )

    new_id = max(
        [ticket["id"] for ticket in TICKETS],
        default=0
    ) + 1

    new_ticket = {
        "id": new_id,
        "customer_name": ticket.customer_name,
        "subject": ticket.subject,
        "description": ticket.description,
        "priority": ticket.priority,
        "status": "open"
    }

    TICKETS.append(new_ticket)

    return new_ticket


@app.put("/tickets/{ticket_id}")
def update_ticket(
    ticket_id: int = Path(..., gt=0),
    ticket: TicketUpdate = ...
):
    for existing_ticket in TICKETS:

        if existing_ticket["id"] == ticket_id:

            existing_ticket["subject"] = ticket.subject
            existing_ticket["description"] = ticket.description
            existing_ticket["priority"] = ticket.priority

            return existing_ticket

    raise HTTPException(
        status_code=404,
        detail="Ticket not found"
    )


@app.patch("/tickets/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int = Path(..., gt=0),
    status: str = Query(...)
):
    if status not in ["open", "in_progress", "closed"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )

    for ticket in TICKETS:

        if ticket["id"] == ticket_id:
            ticket["status"] = status
            return ticket

    raise HTTPException(
        status_code=404,
        detail="Ticket not found"
    )


@app.delete("/tickets/{ticket_id}", status_code=204)
def delete_ticket(
    ticket_id: int = Path(..., gt=0)
):
    for ticket in TICKETS:

        if ticket["id"] == ticket_id:
            TICKETS.remove(ticket)
            return

    raise HTTPException(
        status_code=404,
        detail="Ticket not found"
    )


@app.get("/tickets/stats")
def ticket_statistics():
    total_tickets = len(TICKETS)

    open_tickets = sum(
        1 for ticket in TICKETS
        if ticket["status"] == "open"
    )

    return {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets
    }

'''
Question 1

Pydantic model request body ke data ko validate karta hai aur required fields aur data rules check karta hai.

Question 2

PUT existing resource ko update karne ke liye use hota hai, jabki PATCH resource ke specific part ko update karne ke liye use hota hai.

Question 3

201 ka matlab hai ki request ke through new resource successfully create hua hai.

Question 4

204 ka matlab hai request successful hai aur DELETE ke baad return karne ke liye koi response body nahi hai.

Question 5

400 invalid input/business rule ke liye, 404 resource na milne ke liye, aur 422 request validation fail hone par use hota hai.

Question 6

Search me result na milna error nahi hai, isliye API [] return karti hai, jiska matlab hai koi matching ticket nahi mila.

Question 7

Agar priority="urgent" bheja jaye, to API usse invalid priority maan kar 400 error return karegi.

Question 8

10 million tickets ke liye in-memory list ki jagah database use karenge aur indexing, pagination aur efficient search/filtering add karenge.'''