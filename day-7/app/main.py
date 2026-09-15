'''
                                                       SECTION = 1
                                                       1	One session per request + proper cleanup
2 201	Resource successfully create hua
3 404	Resource nahi mila
4 Pending changes database mein save karta hai
5 Current transaction ke changes undo karta hai
6		Har request ke liye session aur baad mein close
7		Commit ke bina changes persist nahi hote
8	 db.add()	Object ko session mein add karta hai
9		db.get() ya appropriate SELECT style
10	 db.delete(obj)	Object delete karne ke liye
11	All succeed or all fail together
12	 422	Request validation failure
13	 rollback()	Failed transaction ko undo karta hai
14	404	Clear not-found response
15	Connection leaks/resource exhaustion
16	Create, Read, Update, Delete
17	Structured HTTP error response
18	Load → modify → commit
19	Database se object state reload
20	Detailed error internally log, generic error user ko

                                                           Section B 
                                                          Question =1


FastAPI mein database session dependency ka purpose API endpoint ko database ke saath safely connect karna hai.

Hum get_session() dependency use karte hain jo har request ke liye ek database session provide karti hai.

Basic flow:

Request
   ↓
get_session()
   ↓
Database Session
   ↓
API operation
   ↓
commit / rollback
   ↓
session close

Example:

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

yield ke through session endpoint ko milta hai aur finally mein session close ho jata hai.


                                                 Question = 2

CRUD ka full form:

CRUD	Meaning	Example
C	Create	POST /api/v1/employees
R	Read	GET /api/v1/employees/{employee_id}
U	Update	PUT /api/v1/employees/{employee_id}
D	Delete	DELETE /api/v1/employees/{employee_id}
Simple flow:
POST   → Create
GET    → Read
PUT    → Update
DELETE → Delete
                                              Question = 3
Transaction kya hai?

Database transaction multiple database operations ka ek logical unit hota hai.

Goal:

Ya to saare operations successful hon, ya failure hone par changes undo ho jayein.

commit()

commit() database mein changes permanently save karta hai.

Example:

db.add(employee)
db.commit()
rollback()

Agar database operation fail ho jaye to rollback() current transaction ke changes ko undo karta hai.

Example:

try:
    db.add(employee)
    db.commit()
except Exception:
    db.rollback()
    raise
Simple yaad rakho:
SUCCESS → commit()
ERROR   → rollback()
                                                     Question = 4
1. Resource Not Found

Agar employee database mein nahi hai:

raise HTTPException(
    status_code=404,
    detail="Employee not found"
)

Response:

{
    "detail": "Employee not found"
}
                                                 Question = 2

Pydantic model invalid input ko validate karta hai.

FastAPI normally invalid request body ke liye:

422 Unprocessable Entity

return karta hai.

Example:

{
    "email": "wrong-email"
}

Agar schema mein valid email required hai, validation fail hogi.

                                                   Question = 3

Agar email unique hai aur same email dobara insert kiya:

try:
    db.add(employee)
    db.commit()
except IntegrityError:
    db.rollback()
    raise HTTPException(
        status_code=400,
        detail="Email already exists"
    )

Important:

Database error ke baad rollback karna zaroori hai.

                                                        Section = C 
                                                      Question = 1

Given:

@app.post("/employees")
def create_employee(employee_data: EmployeeCreate, db: Session = Depends(get_session)):
    employee = Employee(**employee_data.dict())
    db.add(employee)
    # missing commit
    return employee
1. Issue

Employee ko db.add() se session mein add kiya gaya hai, lekin db.commit() nahi kiya.

                                                    Question = 2
db.add() sirf object ko current SQLAlchemy session mein add karta hai.

Database mein permanent save karne ke liye:

db.commit()

required hai.

Agar commit nahi hua, transaction commit nahi hogi aur request ke baad changes persist nahi honge.

                                                   Question = 3

Correct flow:

Create object
     ↓
db.add()
     ↓
db.commit()
     ↓
db.refresh()
     ↓
return object

Example:

db.add(employee)
db.commit()
db.refresh(employee)
return employee
Task 2 — No Rollback on Error

Given:

@app.post("/employees")
def create_employee(employee_data: EmployeeCreate, db: Session = Depends(get_session)):
    employee = Employee(**employee_data.dict())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee
Issue

Is code mein database error handle nahi kiya gaya.

Example:

duplicate email
foreign key error
NOT NULL violation
database error
Problem

Agar commit() ke time exception aa gayi aur rollback nahi kiya, to SQLAlchemy session failed/invalid transaction state mein reh sakta hai.

Usi session mein further database operations problematic ho sakte hain.

Improvement

try-except use karo:

try:
    db.add(employee)
    db.commit()
    db.refresh(employee)
except Exception:
    db.rollback()
    raise
Simple rule:
Database operation successful → commit()
Database operation failed     → rollback()
                                                   Question = 3 
Given:

@app.post("/employees", status_code=200)
def create_employee(...):
    

Correct:
@app.post("/employees", status_code=201)
Why?

201 Created specifically indicate karta hai:

New resource successfully create ho gaya.

Expected response:

POST /employees
        ↓
201 Created
                                                Question = 4 

Given:

@app.get("/employees/{employee_id}")
def get_employee(employee_id: int, db: Session = Depends(get_session)):
    employee = db.get(Employee, employee_id)
    return employee
Issue

Agar employee exist nahi karta, db.get():

None

return karega.

Endpoint potentially:

null

return kar sakta hai.

Ye proper API error handling nahi hai.

Improvement:
employee = db.get(Employee, employee_id)

if employee is None:
    raise HTTPException(
        status_code=404,
        detail="Employee not found"
    )

return employee
Correct flow:
ID database mein hai?
       ↓
    YES → 200 + employee
       ↓
     NO → 404 + error'''





from fastapi import FastAPI

from .api.routes.employees import router as employee_router
from .api.routes.task import router as task_router


app = FastAPI(
    title="Employee Task API"
)


app.include_router(
    employee_router,
    prefix="/api/v1"
)

app.include_router(
    task_router,
    prefix="/api/v1"
)


@app.get("/")
def root():
    return {
        "message": "Employee Task API is running"
    }