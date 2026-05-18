"""Pydantic schemas — request validation and response shaping."""

from typing import Optional
from pydantic import BaseModel, EmailStr


# ---------- Products ----------

class ProductBase(BaseModel):
    name: str
    price: float
    stock: int
    branch_id: str = "branch_1"
    sync_status: str = "PENDING"


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    branch_id: Optional[str] = None
    sync_status: Optional[str] = None


class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Customers ----------

class CustomerBase(BaseModel):
    name: str
    email: EmailStr


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class Customer(CustomerBase):
    id: int

    class Config:
        from_attributes = True
