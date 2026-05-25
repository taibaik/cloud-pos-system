"""Pydantic schemas — request validation and response shaping."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

# ---------- Categories ----------

class Category(BaseModel):
    id: str = Field(validation_alias="ID")
    name: str = Field(validation_alias="NAME")
    parentid: Optional[str] = Field(default=None, validation_alias="PARENTID")
    branch_id: str
    sync_status: str
    last_sync_timestamp: Optional[datetime] = None
    cloud_record_id: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


# ---------- Locations ----------

class Location(BaseModel):
    id: str = Field(validation_alias="ID")
    name: str = Field(validation_alias="NAME")
    address: Optional[str] = Field(default=None, validation_alias="ADDRESS")

    class Config:
        from_attributes = True
        populate_by_name = True


# ---------- Products ----------

class ProductBase(BaseModel):
    name: str = Field(validation_alias="NAME")
    pricesell: float = Field(validation_alias="PRICESELL")
    category: Optional[str] = Field(default=None, validation_alias="CATEGORY")
    taxcat: Optional[str] = Field(default=None, validation_alias="TAXCAT")
    barcode: Optional[str] = Field(default=None, validation_alias="BARCODE")
    stockcurrent: float = Field(default=0.0, validation_alias="STOCKCURRENT")
    branch_id: str = Field(default="branch_1")
    sync_status: str = Field(default="PENDING")
    last_sync_timestamp: Optional[datetime] = None
    cloud_record_id: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class ProductCreate(ProductBase):
    id: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, validation_alias="NAME")
    pricesell: Optional[float] = Field(default=None, validation_alias="PRICESELL")
    category: Optional[str] = Field(default=None, validation_alias="CATEGORY")
    taxcat: Optional[str] = Field(default=None, validation_alias="TAXCAT")
    barcode: Optional[str] = Field(default=None, validation_alias="BARCODE")
    stockcurrent: Optional[float] = Field(default=None, validation_alias="STOCKCURRENT")
    branch_id: Optional[str] = None
    sync_status: Optional[str] = None
    last_sync_timestamp: Optional[datetime] = None
    cloud_record_id: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class Product(ProductBase):
    id: str = Field(validation_alias="ID")


# ---------- Customers ----------

class CustomerBase(BaseModel):
    searchkey: Optional[str] = Field(default=None, validation_alias="SEARCHKEY")
    name: str = Field(validation_alias="NAME")
    email: Optional[EmailStr] = Field(default=None, validation_alias="EMAIL")
    phone: Optional[str] = Field(default=None, validation_alias="PHONE")
    loyaltypoints: int = Field(default=0, validation_alias="LOYALTYPOINTS")
    branch_id: str = Field(default="branch_1")
    sync_status: str = Field(default="PENDING")
    last_sync_timestamp: Optional[datetime] = None
    cloud_record_id: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class CustomerCreate(CustomerBase):
    id: Optional[str] = None


class CustomerUpdate(BaseModel):
    searchkey: Optional[str] = Field(default=None, validation_alias="SEARCHKEY")
    name: Optional[str] = Field(default=None, validation_alias="NAME")
    email: Optional[EmailStr] = Field(default=None, validation_alias="EMAIL")
    phone: Optional[str] = Field(default=None, validation_alias="PHONE")
    loyaltypoints: Optional[int] = Field(default=None, validation_alias="LOYALTYPOINTS")
    branch_id: Optional[str] = None
    sync_status: Optional[str] = None
    last_sync_timestamp: Optional[datetime] = None
    cloud_record_id: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class Customer(CustomerBase):
    id: str = Field(validation_alias="ID")


# ---------- Tickets & Ticket Lines ----------

class TicketLine(BaseModel):
    ticket: str = Field(validation_alias="TICKET")
    line: int = Field(validation_alias="LINE")
    product: Optional[str] = Field(default=None, validation_alias="PRODUCT")
    units: float = Field(validation_alias="UNITS")
    price: float = Field(validation_alias="PRICE")
    taxid: Optional[str] = Field(default=None, validation_alias="TAXID")
    branch_id: str = Field(default="branch_1")
    sync_status: str = Field(default="SYNCED")
    last_sync_timestamp: Optional[datetime] = None
    cloud_record_id: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class Ticket(BaseModel):
    id: str = Field(validation_alias="ID")
    tickettype: int = Field(validation_alias="TICKETTYPE")
    datenew: datetime = Field(validation_alias="DATENEW")
    customer: Optional[str] = Field(default=None, validation_alias="CUSTOMER")
    person: Optional[str] = Field(default=None, validation_alias="PERSON")
    total: float = Field(validation_alias="TOTAL")
    branch_id: str = Field(default="branch_1")
    sync_status: str = Field(default="SYNCED")
    last_sync_timestamp: Optional[datetime] = None
    cloud_record_id: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class TicketWithLines(Ticket):
    lines: list[TicketLine] = []
