'''
                                                Section A 

1)	APIRouter related routes ko group/organize karta hai.
2) prefix	Prefix sabhi routes ke starting mein add hota hai.
3)	Tags Swagger UI mein endpoints ko group karte hain.
4) main.py	Usually main.py main FastAPI application rakhta hai.
5)	Har route ke aage /api/v1 automatically lag jayega.
6)	Feature-based folders/files modular project ke liye better hain.
7	None of the given options	Correct syntax hai app.include_router(router).
8)	Route URL mein prefix automatically include hota hai.
9)	Code maintain karna aur responsibilities separate karna easy hota hai.
10)	api/router.py commonly different feature routers ko aggregate karta hai.
11) POST	POST generally new resource create karta hai.
12) 201	201 Created successful resource creation ke liye typical response hai.
13)	Future API changes ko existing clients se separate rakhne mein help karta hai.
14) app/main.py	Main FastAPI() instance generally yahin hota hai.
15)	Related code ko feature/domain ke according group karta hai.
16) employees	Employee endpoints ke liye descriptive tag hai.
17)	Router ke routes ko main FastAPI app mein register karta hai.
18)	employees.py, auth.py jaise descriptive names better hain.
19)	Swagger UI mein routes "Employees" group ke andar dikhenge.
20)	Large project mein scalability, maintenance aur teamwork improve hota hai.

                                             Section B 
                                             Question = 1

APIRouter FastAPI ka tool hai jo related API routes ko ek jagah organize karne ke liye use hota hai.

Example: Employee ke saare routes employees.py mein rakh sakte hain:

api/
└── routes/
    └── employees.py

Is file mein employee ke:

GET
POST
PUT
DELETE

routes rakhe ja sakte hain.

Phir main.py mein router ko include karte hain:

app.include_router(employee_router)

Benefit: main.py bahut bada nahi hota aur project maintain karna easy hota hai.

                                                     Question = 2

prefix ka use router ke common starting URL ko define karne ke liye hota hai.

Example:

router = APIRouter(prefix="/api/v1")

Aur route:

@router.get("/employees")

To final URL hoga:

/api/v1/employees

Matlab prefix har route ke aage automatically add ho jayega.

Simple formula:
prefix + route
/api/v1 + /employees

=

/api/v1/employees
                                                   Question=3

Tags Swagger UI mein API endpoints ko groups mein arrange karte hain.

Example:

router = APIRouter(tags=["Employees"])

To employee ke routes Swagger UI mein Employees naam ke group ke andar dikh sakte hain.

Different features ke liye different tags use kar sakte hain:

Employees
Auth
Reports
Benefit

Agar API mein 50–100 endpoints hain, to Swagger UI mein sab routes mixed nahi rahenge.

Instead:

Employees
   ├── GET /employees
   ├── POST /employees
   └── DELETE /employees

Auth
   ├── POST /login
   └── POST /register

Reports
   └── GET /reports

Isse API documentation samajhna easy hota hai.

                                                   Question = 4

Employees, authentication aur reports ke liye ek possible structure:

app/
│
├── main.py
│
└── api/
    │
    ├── router.py
    │
    └── routes/
        ├── employees.py
        ├── auth.py
        └── reports.py
Kaam

main.py
→ Main FastAPI application.

employees.py
→ Employee-related routes.

auth.py
→ Login/register/authentication routes.

reports.py
→ Report-related routes.

router.py
→ Different routers ko combine/include karne mein help karta hai.

                                                 section = c
                                                question = 1
main.py can become very large.
Employee, authentication, and report routes are mixed together.
Finding and maintaining routes becomes difficult.
Multiple developers may face difficulty working on the same file.
Separation of concerns is not properly followed.

                                                question = 2
The route will be available as /employees.
There is no API version such as /api/v1.
Managing future API changes can become difficult.
Different API versions cannot be clearly separated.

                                                question = 3
Different features are mixed together.
The router file can become very large.
Finding specific routes becomes difficult.
Maintenance becomes harder.
Separation of concerns is not followed properly.

                                                question = 4
The employee router is imported, but it is not included in the FastAPI application.

Therefore, FastAPI does not register the employee routes, so they will not be available.                                                
                                                 '''
from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(
    title="Employee API",
    description="Modular Employee Management API",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}