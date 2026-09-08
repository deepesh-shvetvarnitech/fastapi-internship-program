
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field

app = FastAPI(
    title="Product Inventory API",
    description="A simple in-memory inventory management API",
    version="1.0.0"
)

PRODUCTS = [
    {
        "id": 1,
        "name": "Wireless Mouse",
        "category": "Electronics",
        "price": 799.00,
        "stock": 25,
        "is_active": True
    },
    {
        "id": 2,
        "name": "Mechanical Keyboard",
        "category": "Electronics",
        "price": 2499.00,
        "stock": 10,
        "is_active": True
    },
    {
        "id": 3,
        "name": "Office Chair",
        "category": "Furniture",
        "price": 8999.00,
        "stock": 5,
        "is_active": True
    },
    {
        "id": 4,
        "name": "USB-C Cable",
        "category": "Accessories",
        "price": 499.00,
        "stock": 0,
        "is_active": False
    }
]

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)

class ProductUpdate(BaseModel):
    name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)

def find_product(product_id: int):
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    return None

@app.get("/products/{product_id}", status_code=200)
def get_product(
    product_id: int = Path(..., gt=0)
):
    product = find_product(product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product

@app.post("/products", status_code=201)
def create_product(product: ProductCreate):
    if PRODUCTS:
        new_id = max(item["id"] for item in PRODUCTS) + 1
    else:
        new_id = 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "category": product.category,
        "price": product.price,
        "stock": product.stock,
        "is_active": True
    }

    PRODUCTS.append(new_product)

    return new_product

@app.put("/products/{product_id}", status_code=200)
def update_product(
    product: ProductUpdate,
    product_id: int = Path(..., gt=0)
):
    existing_product = find_product(product_id)

    if existing_product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    existing_product["name"] = product.name
    existing_product["category"] = product.category
    existing_product["price"] = product.price
    existing_product["stock"] = product.stock

    return existing_product

@app.patch("/products/{product_id}/status", status_code=200)
def update_product_status(
    product_id: int = Path(..., gt=0),
    is_active: bool = Query(...)
):
    product = find_product(product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    product["is_active"] = is_active

    return product

@app.delete("/products/{product_id}", status_code=204)
def delete_product(
    product_id: int = Path(..., gt=0)
):
    product = find_product(product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    PRODUCTS.remove(product)
    return None

@app.get("/products", status_code=200)
def list_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None, min_length=2),
    category: str | None = Query(default=None),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    is_active: bool | None = Query(default=None)
):
    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):
        raise HTTPException(
            status_code=400,
            detail="min_price cannot be greater than max_price"
        )

    filtered_products = PRODUCTS.copy()

    if search is not None:
        search = search.lower()

        filtered_products = [
            product
            for product in filtered_products
            if search in product["name"].lower()
        ]

    if category is not None:
        filtered_products = [
            product
            for product in filtered_products
            if product["category"].lower() == category.lower()
        ]

    if min_price is not None:
        filtered_products = [
            product
            for product in filtered_products
            if product["price"] >= min_price
        ]

    if max_price is not None:
        filtered_products = [
            product
            for product in filtered_products
            if product["price"] <= max_price
        ]

    if is_active is not None:
        filtered_products = [
            product
            for product in filtered_products
            if product["is_active"] == is_active
        ]

    total = len(filtered_products)

    start = (page - 1) * page_size
    end = start + page_size

    paginated_products = filtered_products[start:end]

    return {
        "items": paginated_products,
        "total": total,
        "page": page,
        "page_size": page_size
    }


