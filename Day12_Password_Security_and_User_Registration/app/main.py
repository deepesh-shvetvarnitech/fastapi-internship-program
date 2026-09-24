'''
                                                      SECTION A
Q1

Answer: a) Authentication verifies who a user is; authorization verifies what they are allowed to do.

Q2

Answer: b) Hashed with a strong algorithm like bcrypt.

Q3
Answer: b) passlib with bcrypt.

Q4

Answer: b) One-way transformation to protect passwords.

Q5

Answer: c) Unique constraint.

Q6
Answer: b) IntegrityError.

Q7

Answer: c) Password hash.

Q8

Answer: b) POST.

Q9

Answer: b) 201.

Q10

Answer: d) 409.

Q11

Answer: a) To make passwords harder to guess and brute-force.

Q12

Answer: c) 8+ characters.

Q13

Answer: b) Return a generic “invalid credentials” error.

Q14
Answer: b) Use a constant-time comparison function provided by the hashing library.

Q15
Answer: b) To store user accounts and credentials.

Q16
Answer: b) Email or username.

Q17
Answer: b) Clear but safe messages, e.g. “Email already registered”.

Q18
Answer: b) Credential theft if the database is compromised.

Q19
Answer: b) email.

Q20
Answer: a) Hash once during registration and store the hash.

                                                   SECTION = B
Q1
Authentication means verifying the identity of a user.

Example:

A user sends an email and password during login. The application verifies that the credentials belong to that user.

Authorization means checking what an authenticated user is allowed to do.

Example:

An authenticated employee may access their own employee data, while an admin may be allowed to create, update, or delete employee records.


Q2

Password hashing converts a password into a one-way hashed value.

Example:

Original password:
MyPassword123

Hashed password:
$2b$12$................................

The original password should not be stored in the database.

During registration:

Password
   ↓
Hash
   ↓
Database

During verification:

Entered password
       ↓
Hashing library verifies it
       ↓
Stored hash
       ↓
Match / No Match

A Python library that can be used is Passlib.

A commonly used algorithm is bcrypt.

Q3
A unique constraint prevents two users from having the same email address.

For example:

user 1 → abc@gmail.com
user 2 → abc@gmail.com

The second registration should not be allowed.

In SQLAlchemy:

email = Column(String, unique=True, nullable=False)

If the database unique constraint is violated, SQLAlchemy commonly raises:

IntegrityError

The application can catch this error and return:

409 Conflict
Q4. User Registration Flow

A secure registration flow works like this:

Client
  ↓
POST /api/v1/auth/register
  ↓
Validate email/password
  ↓
Check whether email already exists
  ↓
Hash password
  ↓
Create User object
  ↓
Save user in database
  ↓
Commit transaction
  ↓
Return safe UserResponse

The password should never be returned in the response.

Example response:

{
    "id": 1,
    "email": "user@example.com"
} 

                                                    SECTION -= C

                                                   QUESTION = 1
Given:
password = Column(String)
Problems:
The password is stored directly in the database.
Anyone who gets database access can see user passwords.
Users may reuse the same password on other websites.
A database leak can therefore expose users' accounts elsewhere.
Passwords should never be stored as plain text.
Improvement:

Use a password hashing algorithm such as bcrypt.

Instead of:

password = "MyPassword123"

store something like:

password_hash = "$2b$12$..."

The application should hash the password during registration.

                                                  QUESTION = 2 
Given:
email = Column(String)
Problems:
Multiple users can register with the same email.
Email cannot reliably identify a unique account.
Login can become ambiguous.
Duplicate accounts can be created accidentally.
Application-level checking alone is not enough because concurrent requests can still create duplicates.
Improvement:

Add a database-level unique constraint:

email = Column(String, unique=True, nullable=False)

Also handle:

IntegrityError

and return:

409 Conflict
                                         QUESTION = 3 
Given:
password_hash: str
Problems:
The password hash is sensitive information.
API clients should not receive it.
Logs or frontend storage could accidentally expose it.
Even though a hash cannot normally be reversed directly, exposing it gives attackers a valuable credential artifact.
Response schemas should contain only information that the client needs.
Improvement:

Use a separate response schema.

Example:

class UserResponse(BaseModel):
    id: int
    email: EmailStr

Do not include:

password_hash

in the response.

                                                     QUESTION = 4

Allowing passwords such as:

a
1
x
""

creates security problems.

Problems:
Very short passwords are easier to guess.
They are more vulnerable to brute-force attacks.
Empty passwords should never be accepted.
Weak passwords reduce account security.
Basic improvement:

Set a minimum password length.

For example:

min_length=8

You can additionally enforce stronger password requirements depending on application needs.

Example:

Minimum 8 characters

The password should then be hashed before storing it.                                                                                                                                                                                                            '''


import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

from app.api.router import api_router
from app.core.exceptions import AppException
from app.core.exception_handlers import (
    app_exception_handler,
    generic_exception_handler,
    integrity_error_handler,
    validation_exception_handler,
)


app = FastAPI(
    title="Employee Task Management API",
    description="FastAPI + SQLAlchemy + PostgreSQL CRUD API",
    version="1.0.0",
)


# ============================================================
# REQUEST ID MIDDLEWARE
# ============================================================

@app.middleware("http")
async def request_id_middleware(
    request: Request,
    call_next,
):
    request_id = request.headers.get(
        "X-Request-ID"
    )

    if not request_id:
        request_id = f"req-{uuid.uuid4().hex[:12]}"

    request.state.request_id = request_id

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    return response


# ============================================================
# GLOBAL EXCEPTION HANDLERS
# ============================================================

app.add_exception_handler(
    AppException,
    app_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    IntegrityError,
    integrity_error_handler,
)

app.add_exception_handler(
    Exception,
    generic_exception_handler,
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(
    api_router,
    prefix="/api/v1",
)


# ============================================================
# SYSTEM ENDPOINTS
# ============================================================

@app.get(
    "/",
    tags=["System"],
)
def root():
    return {
        "message": "Employee Task Management API",
        "version": "1.0.0",
    }


@app.get(
    "/health",
    tags=["System"],
)
def health():
    return {
        "status": "healthy",
    }