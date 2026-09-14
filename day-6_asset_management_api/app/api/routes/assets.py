from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.dependencies import (
    asset_filters,
    get_audit_resource,
    pagination,
    request_metadata,
    require_it_admin,
)

router = APIRouter(
    prefix="/assets",
    tags=["Assets"],
)


ASSETS = [
    {
        "id": 101,
        "asset_tag": "LAP-001",
        "asset_type": "laptop",
        "brand": "Dell",
        "model": "Latitude 5440",
        "employee_name": "Rahul Sharma",
        "department": "Engineering",
        "status": "assigned",
        "is_active": True,
    },
    {
        "id": 102,
        "asset_tag": "MON-001",
        "asset_type": "monitor",
        "brand": "LG",
        "model": "27UP850",
        "employee_name": "Priya Patel",
        "department": "HR",
        "status": "assigned",
        "is_active": True,
    },
    {
        "id": 103,
        "asset_tag": "LAP-002",
        "asset_type": "laptop",
        "brand": "Lenovo",
        "model": "ThinkPad E14",
        "employee_name": "Amit Verma",
        "department": "Engineering",
        "status": "available",
        "is_active": True,
    },
    {
        "id": 104,
        "asset_tag": "MOB-001",
        "asset_type": "mobile",
        "brand": "Samsung",
        "model": "Galaxy S24",
        "employee_name": "Neha Singh",
        "department": "Sales",
        "status": "assigned",
        "is_active": True,
    },
    {
        "id": 105,
        "asset_tag": "LAP-003",
        "asset_type": "laptop",
        "brand": "HP",
        "model": "EliteBook 840",
        "employee_name": None,
        "department": None,
        "status": "maintenance",
        "is_active": True,
    },
]


AssetType = Literal[
    "laptop",
    "monitor",
    "mobile",
    "keyboard",
    "mouse",
    "headset",
    "other",
]

AssetStatus = Literal[
    "available",
    "assigned",
    "maintenance",
    "retired",
    "lost",
]

Department = Literal[
    "Engineering",
    "HR",
    "Sales",
    "Finance",
    "Marketing",
    "Support",
]


class AssetCreate(BaseModel):
    asset_tag: str = Field(..., min_length=1)
    asset_type: AssetType
    brand: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    employee_name: Optional[str] = None
    department: Optional[Department] = None


class AssetUpdate(BaseModel):
    asset_tag: str = Field(..., min_length=1)
    asset_type: AssetType
    brand: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    employee_name: Optional[str] = None
    department: Optional[Department] = None
    status: AssetStatus
    is_active: bool


class AssetPatch(BaseModel):
    asset_tag: Optional[str] = Field(None, min_length=1)
    asset_type: Optional[AssetType] = None
    brand: Optional[str] = Field(None, min_length=1)
    model: Optional[str] = Field(None, min_length=1)
    employee_name: Optional[str] = None
    department: Optional[Department] = None
    status: Optional[AssetStatus] = None
    is_active: Optional[bool] = None


@router.get("/request-info")
def get_request_info(
    metadata: dict = Depends(request_metadata),
):
    return metadata


@router.get("/stats")
def get_asset_stats():
    return {
        "total_assets": len(ASSETS),
        "available": sum(asset["status"] == "available" for asset in ASSETS),
        "assigned": sum(asset["status"] == "assigned" for asset in ASSETS),
        "maintenance": sum(asset["status"] == "maintenance" for asset in ASSETS),
        "retired": sum(asset["status"] == "retired" for asset in ASSETS),
        "lost": sum(asset["status"] == "lost" for asset in ASSETS),
    }


@router.get("/audit-check")
def audit_check(
    resource: dict = Depends(get_audit_resource),
):
    return {
        "message": "Audit resource is working",
        "resource": resource,
    }


@router.get("")
def list_assets(
    pagination_data: dict = Depends(pagination),
    filters: dict = Depends(asset_filters),
):
    filtered_assets = ASSETS

    if filters["asset_type"] is not None:
        filtered_assets = [
            asset
            for asset in filtered_assets
            if asset["asset_type"] == filters["asset_type"]
        ]

    if filters["status"] is not None:
        filtered_assets = [
            asset
            for asset in filtered_assets
            if asset["status"] == filters["status"]
        ]

    if filters["department"] is not None:
        filtered_assets = [
            asset
            for asset in filtered_assets
            if asset["department"] == filters["department"]
        ]

    if filters["is_active"] is not None:
        filtered_assets = [
            asset
            for asset in filtered_assets
            if asset["is_active"] == filters["is_active"]
        ]

    total = len(filtered_assets)

    offset = pagination_data["offset"]
    page_size = pagination_data["page_size"]

    paginated_assets = filtered_assets[
        offset:offset + page_size
    ]

    return {
        "page": pagination_data["page"],
        "page_size": page_size,
        "total": total,
        "assets": paginated_assets,
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_it_admin)],
)
def create_asset(asset: AssetCreate):
    max_id = max(
        (item["id"] for item in ASSETS),
        default=100,
    )

    new_asset = {
        "id": max_id + 1,
        "asset_tag": asset.asset_tag,
        "asset_type": asset.asset_type,
        "brand": asset.brand,
        "model": asset.model,
        "employee_name": asset.employee_name,
        "department": asset.department,
        "status": "available",
        "is_active": True,
    }

    ASSETS.append(new_asset)

    return new_asset


@router.get("/{asset_id}")
def get_asset(asset_id: int):
    if asset_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="asset_id must be greater than 0",
        )

    for asset in ASSETS:
        if asset["id"] == asset_id:
            return asset

    raise HTTPException(
        status_code=404,
        detail="Asset not found",
    )


@router.put(
    "/{asset_id}",
    dependencies=[Depends(require_it_admin)],
)
def update_asset(
    asset_id: int,
    asset: AssetUpdate,
):
    if asset_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="asset_id must be greater than 0",
        )

    for existing_asset in ASSETS:
        if existing_asset["id"] == asset_id:
            existing_asset.update(
                asset.model_dump()
            )

            existing_asset["id"] = asset_id

            return existing_asset

    raise HTTPException(
        status_code=404,
        detail="Asset not found",
    )


@router.patch(
    "/{asset_id}",
    dependencies=[Depends(require_it_admin)],
)
def patch_asset(
    asset_id: int,
    asset: AssetPatch,
):
    if asset_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="asset_id must be greater than 0",
        )

    for existing_asset in ASSETS:
        if existing_asset["id"] == asset_id:
            update_data = asset.model_dump(
                exclude_unset=True
            )

            existing_asset.update(update_data)

            return existing_asset

    raise HTTPException(
        status_code=404,
        detail="Asset not found",
    )


@router.delete(
    "/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_it_admin)],
)
def delete_asset(asset_id: int):
    if asset_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="asset_id must be greater than 0",
        )

    for index, asset in enumerate(ASSETS):
        if asset["id"] == asset_id:
            ASSETS.pop(index)

            return Response(
                status_code=status.HTTP_204_NO_CONTENT
            )

    raise HTTPException(
        status_code=404,
        detail="Asset not found",
    )