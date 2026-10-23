
import json
from typing import Annotated
from pathlib import Path as FilePath

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel

app = FastAPI()

FILE = "products.json"


class Product(BaseModel):
    id: int
    name: str
    price: int
    category: str
    address: str


class ProductUpdate(BaseModel):
    name: str
    price: int
    category: str
    address: str


def load():
    if not FilePath(FILE).exists():
        return []

    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save(products):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=4)


@app.get("/")
def home():
    return {"message": "Product API is running"}


@app.get("/products")
def get_products(
    category: Annotated[
        str | None,
        Query(min_length=3, max_length=20)
    ] = None
):
    products = load()

    if category:
        products = [
            product for product in products
            if product["category"].lower() == category.lower()
        ]

    return products


@app.get("/products/{product_id}")
def get_product(product_id: int):
    products = load()

    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )


@app.post("/products")
def create_product(product: Product):
    products = load()

    if any(p["id"] == product.id for p in products):
        raise HTTPException(
            status_code=400,
            detail="Product ID already exists"
        )

    products.append(product.model_dump())
    save(products)

    return {
        "message": "Product added successfully",
        "product": product
    }


@app.put("/products/{product_id}")
def update_product(product_id: int, updated_product: ProductUpdate):
    products = load()

    for index, product in enumerate(products):
        if product["id"] == product_id:
            products[index].update(updated_product.model_dump())
            save(products)

            return {
                "message": "Product updated successfully",
                "product": products[index]
            }

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    products = load()

    for index, product in enumerate(products):
        if product["id"] == product_id:
            deleted_product = products.pop(index)
            save(products)

            return {
                "message": "Product deleted successfully",
                "product": deleted_product
            }

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )
