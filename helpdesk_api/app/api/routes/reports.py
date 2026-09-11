from fastapi import APIRouter

from app.api.routes.tickets import tickets


router = APIRouter(
    prefix="/reports",
    tags=["REPORTS"]
)


@router.get("/tickets")
def get_ticket_report():
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