# Company IT Asset Management API

FastAPI based IT Asset Management API.

## Features

- Depends()
- Pagination
- Filtering
- Request metadata
- API key verification
- Nested dependencies
- Yield dependency
- Dependency overrides
- CRUD
- Pydantic validation
- In-memory data

## Install

pip install -r requirements.txt

## Run

uvicorn app.main:app --reload

## Swagger

http://127.0.0.1:8000/docs

## OpenAPI

http://127.0.0.1:8000/openapi.json

## API Key

X-API-Key: development-secret-key

## Protected Endpoints

POST /api/v1/assets

PUT /api/v1/assets/{asset_id}

PATCH /api/v1/assets/{asset_id}

DELETE /api/v1/assets/{asset_id}

## Public Endpoints

GET /api/v1/assets

GET /api/v1/assets/{asset_id}

GET /api/v1/assets/stats

GET /api/v1/assets/request-info

GET /api/v1/assets/audit-check

## Pagination

/api/v1/assets?page=1&page_size=2

## Filtering

/api/v1/assets?status=assigned

/api/v1/assets?department=Engineering

/api/v1/assets?asset_type=laptop&status=assigned

## Tests

pytest -v