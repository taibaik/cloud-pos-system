"""
Data access layer.

Uses SQLAlchemy Core with bound parameters (no string formatting) so the
queries are safe against SQL injection. Kept close to the team's original
raw-SQL style so it stays easy to explain in a presentation.
"""

import uuid
from sqlalchemy import text
from sqlalchemy.orm import Session


# ---------------- Products ----------------

def list_products(db: Session):
    rows = db.execute(text("SELECT * FROM PRODUCTS ORDER BY ID")).mappings().all()
    return [dict(r) for r in rows]


def get_product(db: Session, product_id: str):
    row = db.execute(
        text("SELECT * FROM PRODUCTS WHERE ID = :id"),
        {"id": product_id},
    ).mappings().first()
    return dict(row) if row else None


def create_product(db: Session, p):
    p_dict = p.dict()
    if not p_dict.get("id"):
        p_dict["id"] = f"prod_{uuid.uuid4().hex[:8]}"
    db.execute(
        text(
            "INSERT INTO PRODUCTS (ID, NAME, PRICESELL, CATEGORY, TAXCAT, BARCODE, STOCKCURRENT, branch_id, sync_status, last_sync_timestamp, cloud_record_id) "
            "VALUES (:id, :name, :pricesell, :category, :taxcat, :barcode, :stockcurrent, :branch_id, :sync_status, :last_sync_timestamp, :cloud_record_id)"
        ),
        p_dict,
    )
    db.commit()
    return get_product(db, p_dict["id"])


def update_product(db: Session, product_id: str, p):
    p_dict = p.dict(exclude_unset=True)
    fields = {k: v for k, v in p_dict.items() if v is not None}
    if not fields:
        return get_product(db, product_id)
    
    mapping = {
        "name": "NAME",
        "pricesell": "PRICESELL",
        "category": "CATEGORY",
        "taxcat": "TAXCAT",
        "barcode": "BARCODE",
        "stockcurrent": "STOCKCURRENT",
        "branch_id": "branch_id",
        "sync_status": "sync_status",
        "last_sync_timestamp": "last_sync_timestamp",
        "cloud_record_id": "cloud_record_id"
    }
    
    assignments = ", ".join(f"{mapping.get(k, k)} = :{k}" for k in fields)
    fields["id"] = product_id
    db.execute(
        text(f"UPDATE PRODUCTS SET {assignments} WHERE ID = :id"),
        fields,
    )
    db.commit()
    return get_product(db, product_id)


def delete_product(db: Session, product_id: str) -> bool:
    result = db.execute(
        text("DELETE FROM PRODUCTS WHERE ID = :id"),
        {"id": product_id},
    )
    db.commit()
    return result.rowcount > 0


# ---------------- Customers ----------------

def list_customers(db: Session):
    rows = db.execute(text("SELECT * FROM CUSTOMERS ORDER BY ID")).mappings().all()
    return [dict(r) for r in rows]


def get_customer(db: Session, customer_id: str):
    row = db.execute(
        text("SELECT * FROM CUSTOMERS WHERE ID = :id"),
        {"id": customer_id},
    ).mappings().first()
    return dict(row) if row else None


def create_customer(db: Session, c):
    c_dict = c.dict()
    if not c_dict.get("id"):
        c_dict["id"] = f"cust_{uuid.uuid4().hex[:8]}"
    db.execute(
        text(
            "INSERT INTO CUSTOMERS (ID, SEARCHKEY, NAME, EMAIL, PHONE, LOYALTYPOINTS, branch_id, sync_status, last_sync_timestamp, cloud_record_id) "
            "VALUES (:id, :searchkey, :name, :email, :phone, :loyaltypoints, :branch_id, :sync_status, :last_sync_timestamp, :cloud_record_id)"
        ),
        c_dict,
    )
    db.commit()
    return get_customer(db, c_dict["id"])


def update_customer(db: Session, customer_id: str, c):
    c_dict = c.dict(exclude_unset=True)
    fields = {k: v for k, v in c_dict.items() if v is not None}
    if not fields:
        return get_customer(db, customer_id)
    
    mapping = {
        "searchkey": "SEARCHKEY",
        "name": "NAME",
        "email": "EMAIL",
        "phone": "PHONE",
        "loyaltypoints": "LOYALTYPOINTS",
        "branch_id": "branch_id",
        "sync_status": "sync_status",
        "last_sync_timestamp": "last_sync_timestamp",
        "cloud_record_id": "cloud_record_id"
    }
    
    assignments = ", ".join(f"{mapping.get(k, k)} = :{k}" for k in fields)
    fields["id"] = customer_id
    db.execute(
        text(f"UPDATE CUSTOMERS SET {assignments} WHERE ID = :id"),
        fields,
    )
    db.commit()
    return get_customer(db, customer_id)


def delete_customer(db: Session, customer_id: str) -> bool:
    result = db.execute(
        text("DELETE FROM CUSTOMERS WHERE ID = :id"),
        {"id": customer_id},
    )
    db.commit()
    return result.rowcount > 0


# ---------------- Categories ----------------

def list_categories(db: Session):
    rows = db.execute(text("SELECT * FROM CATEGORIES ORDER BY ID")).mappings().all()
    return [dict(r) for r in rows]


# ---------------- Locations ----------------

def list_locations(db: Session):
    rows = db.execute(text("SELECT * FROM LOCATIONS ORDER BY ID")).mappings().all()
    return [dict(r) for r in rows]


# ---------------- Tickets ----------------

def list_tickets(db: Session):
    rows = db.execute(text("SELECT * FROM TICKETS ORDER BY DATENEW DESC")).mappings().all()
    return [dict(r) for r in rows]


def get_ticket_with_lines(db: Session, ticket_id: str):
    ticket_row = db.execute(
        text("SELECT * FROM TICKETS WHERE ID = :id"),
        {"id": ticket_id},
    ).mappings().first()
    if not ticket_row:
        return None
    ticket_dict = dict(ticket_row)
    
    lines_rows = db.execute(
        text("SELECT * FROM TICKETLINES WHERE TICKET = :ticket_id ORDER BY LINE"),
        {"ticket_id": ticket_id},
    ).mappings().all()
    
    ticket_dict["lines"] = [dict(r) for r in lines_rows]
    return ticket_dict
