'''                                                  Section A 
Question 1

Path parameter URL ka specific resource identify karta hai, jaise /employees/5.
Query parameter filtering/search ke liye use hota hai, jaise /employees?department=Engineering.

Question 2

New leave request create karne ke liye POST method use hota hai.

Question 3

Full update ke liye PUT method use hota hai.

Question 4

Partial update ke liye PATCH method use hota hai.

Question 5

Successfully leave create hone par 201 Created status code return hona chahiye.

Question 6

Employee ya leave request nahi milne par 404 Not Found return hota hai.

Question 7

Pydantic model request data ko validate karta hai aur required fields/data types check karta hai.

Question 8

response_model decide karta hai ki API response mein kaunsa data return/expose hoga.

Question 9

Internal fields ko directly return nahi karna chahiye kyunki unmein sensitive/internal information ho sakti hai.

Question 10

Pydantic validation fail hone par FastAPI normally 422 Unprocessable Entity return karta hai.

                                            SECTION = B
                                          Question=1 

LeaveCreate mein ye fields honi chahiye:

employee_id
leave_type
start_date
end_date
reason

employee_id > 0, leave_type allowed values mein ho, dates valid honi chahiye, aur reason 5–300 characters ka hona chahiye.

                                            Question=2 

LeaveUpdate PUT ke liye use hoga. Ismein saare editable fields required hone chahiye.

                                            Question=3 

LeavePartialUpdate PATCH ke liye use hoga. Ismein saare fields optional honge, isliye ek hi field update kar sakte hain.

                                           Question= 4

LeaveResponse mein ye fields return hongi:

id, employee_id, employee_name, leave_type, start_date, end_date, reason, status

internal_note aur approved_by_internal_id jaise internal fields client ko return nahi karne hain.  

                                        SECTION =D
                                         Question 1

data: dict use karne se proper validation nahi milegi.
data: LeaveCreate use karne se Pydantic validation automatically milegi.

                                           Question 2

Nahi, internal_note client ko return nahi karna chahiye, kyunki ye internal information hai.

                                         Question 3

Agar GET /leaves/999 mein leave exist nahi karti, to 404 Not Found return karna chahiye.

                                          Question 4

FastAPI default mein 200 OK return karega.
Successful creation ke liye better status code 201 Created hai.

                                          section =d                                                                                                                            '''
from fastapi import FastAPI, HTTPException, Query, Path, status
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


app = FastAPI(
    title="Employee Leave Management API",
    description="API for managing employee leave requests",
    version="1.0.0"
)


EMPLOYEES = [
    {
        "id": 101,
        "name": "Rahul Sharma"
    },
    {
        "id": 102,
        "name": "Priya Patel"
    }
]


LEAVES = [
    {
        "id": 1,
        "employee_id": 101,
        "employee_name": "Rahul Sharma",
        "leave_type": "casual",
        "start_date": "2026-09-10",
        "end_date": "2026-09-11",
        "reason": "Personal work",
        "status": "pending",
        "internal_note": "Waiting for manager approval"
    },
    {
        "id": 2,
        "employee_id": 102,
        "employee_name": "Priya Patel",
        "leave_type": "sick",
        "start_date": "2026-09-05",
        "end_date": "2026-09-06",
        "reason": "Not feeling well",
        "status": "approved",
        "internal_note": "Medical leave"
    }
]


class LeaveCreate(BaseModel):
    employee_id: int = Field(gt=0)
    leave_type: str
    start_date: date
    end_date: date
    reason: str = Field(min_length=5, max_length=300)


class LeaveUpdate(BaseModel):
    employee_id: int = Field(gt=0)
    leave_type: str
    start_date: date
    end_date: date
    reason: str = Field(min_length=5, max_length=300)


class LeavePartialUpdate(BaseModel):
    employee_id: Optional[int] = Field(default=None, gt=0)
    leave_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = Field(default=None, min_length=5, max_length=300)


class LeaveResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    leave_type: str
    start_date: date
    end_date: date
    reason: str
    status: str


@app.get(
    "/leaves",
    response_model=list[LeaveResponse],
    tags=["Leaves"],
    summary="List employee leave requests"
)
def get_leaves(
    employee_id: Optional[int] = Query(default=None),
    status: Optional[str] = Query(default=None),
    leave_type: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None)
):
    results = LEAVES

    if employee_id is not None:
        results = [
            leave for leave in results
            if leave["employee_id"] == employee_id
        ]

    if status is not None:
        results = [
            leave for leave in results
            if leave["status"] == status
        ]

    if leave_type is not None:
        results = [
            leave for leave in results
            if leave["leave_type"] == leave_type
        ]

    if search is not None:
        search_text = search.lower()
        results = [
            leave for leave in results
            if search_text in leave["reason"].lower()
            or search_text in leave["employee_name"].lower()
        ]

    return results


@app.get(
    "/leaves/{leave_id}",
    response_model=LeaveResponse,
    tags=["Leaves"],
    summary="Get leave by ID"
)
def get_leave(
    leave_id: int = Path(gt=0)
):
    for leave in LEAVES:
        if leave["id"] == leave_id:
            return leave

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Leave request not found"
    )


@app.post(
    "/leaves",
    response_model=LeaveResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Leaves"],
    summary="Create leave request"
)
def create_leave(leave: LeaveCreate):
    employee = None

    for item in EMPLOYEES:
        if item["id"] == leave.employee_id:
            employee = item
            break

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    if leave.end_date < leave.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_date must be greater than or equal to start_date"
        )

    allowed_leave_types = ["casual", "sick", "earned", "unpaid"]

    if leave.leave_type not in allowed_leave_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid leave type"
        )

    new_id = max([item["id"] for item in LEAVES], default=0) + 1

    new_leave = {
        "id": new_id,
        "employee_id": leave.employee_id,
        "employee_name": employee["name"],
        "leave_type": leave.leave_type,
        "start_date": leave.start_date.isoformat(),
        "end_date": leave.end_date.isoformat(),
        "reason": leave.reason,
        "status": "pending",
        "internal_note": "Waiting for manager approval"
    }

    LEAVES.append(new_leave)

    return new_leave


@app.put(
    "/leaves/{leave_id}",
    response_model=LeaveResponse,
    tags=["Leaves"],
    summary="Fully update leave request"
)
def update_leave(
    leave_id: int = Path(gt=0),
    leave: LeaveUpdate = None
):
    for item in LEAVES:
        if item["id"] == leave_id:

            employee = None

            for emp in EMPLOYEES:
                if emp["id"] == leave.employee_id:
                    employee = emp
                    break

            if employee is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Employee not found"
                )

            if leave.end_date < leave.start_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="end_date must be greater than or equal to start_date"
                )

            if leave.leave_type not in ["casual", "sick", "earned", "unpaid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid leave type"
                )

            item["employee_id"] = leave.employee_id
            item["employee_name"] = employee["name"]
            item["leave_type"] = leave.leave_type
            item["start_date"] = leave.start_date.isoformat()
            item["end_date"] = leave.end_date.isoformat()
            item["reason"] = leave.reason

            return item

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Leave request not found"
    )


@app.patch(
    "/leaves/{leave_id}",
    response_model=LeaveResponse,
    tags=["Leaves"],
    summary="Partially update leave request"
)
def partial_update_leave(
    leave_id: int = Path(gt=0),
    leave: LeavePartialUpdate = None
):
    for item in LEAVES:
        if item["id"] == leave_id:

            update_data = leave.model_dump(exclude_unset=True)

            if "employee_id" in update_data:
                employee = None

                for emp in EMPLOYEES:
                    if emp["id"] == update_data["employee_id"]:
                        employee = emp
                        break

                if employee is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Employee not found"
                    )

                item["employee_id"] = update_data["employee_id"]
                item["employee_name"] = employee["name"]

            if "leave_type" in update_data:
                if update_data["leave_type"] not in [
                    "casual",
                    "sick",
                    "earned",
                    "unpaid"
                ]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid leave type"
                    )

                item["leave_type"] = update_data["leave_type"]

            if "start_date" in update_data:
                item["start_date"] = update_data["start_date"].isoformat()

            if "end_date" in update_data:
                item["end_date"] = update_data["end_date"].isoformat()

            if "start_date" in update_data or "end_date" in update_data:
                start = date.fromisoformat(item["start_date"])
                end = date.fromisoformat(item["end_date"])

                if end < start:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="end_date must be greater than or equal to start_date"
                    )

            if "reason" in update_data:
                item["reason"] = update_data["reason"]

            return item

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Leave request not found"
    )


@app.patch(
    "/leaves/{leave_id}/status",
    response_model=LeaveResponse,
    tags=["Leaves"],
    summary="Approve or reject leave"
)
def update_leave_status(
    leave_id: int = Path(gt=0),
    status_value: str = Query(alias="status")
):
    if status_value not in ["pending", "approved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status"
        )

    for leave in LEAVES:
        if leave["id"] == leave_id:
            leave["status"] = status_value
            return leave

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Leave request not found"
    )


@app.delete(
    "/leaves/{leave_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Leaves"],
    summary="Delete leave request"
)
def delete_leave(
    leave_id: int = Path(gt=0)
):
    for index, leave in enumerate(LEAVES):
        if leave["id"] == leave_id:
            LEAVES.pop(index)
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Leave request not found"
    )


@app.get(
    "/",
    tags=["General"],
    summary="API welcome"
)
def home():
    return {
        "message": "Employee Leave Management API is working"
    }

