"""
Data access layer.

Uses SQLAlchemy Core with bound parameters (no string formatting) so the
queries are safe against SQL injection. Kept close to the team's original
raw-SQL style so it stays easy to explain in a presentation.
"""

from sqlalchemy import text
from sqlalchemy.orm import Session


# ---------------- Products ----------------

def list_products(db: Session):
    rows = db.execute(text("SELECT * FROM products ORDER BY id")).mappings().all()
    return [dict(r) for r in rows]


def get_product(db: Session, product_id: int):
    row = db.execute(
        text("SELECT * FROM products WHERE id = :id"),
        {"id": product_id},
    ).mappings().first()
    return dict(row) if row else None


def create_product(db: Session, p):
    result = db.execute(
        text(
            "INSERT INTO products (name, price, stock, branch_id, sync_status) "
            "VALUES (:name, :price, :stock, :branch_id, :sync_status)"
        ),
        p.dict(),
    )
    db.commit()
    return get_product(db, result.lastrowid)


def update_product(db: Session, product_id: int, p):
    fields = {k: v for k, v in p.dict().items() if v is not None}
    if not fields:
        return get_product(db, product_id)
    assignments = ", ".join(f"{k} = :{k}" for k in fields)
    fields["id"] = product_id
    db.execute(
        text(f"UPDATE products SET {assignments} WHERE id = :id"),
        fields,
    )
    db.commit()
    return get_product(db, product_id)


def delete_product(db: Session, product_id: int) -> bool:
    result = db.execute(
        text("DELETE FROM products WHERE id = :id"),
        {"id": product_id},
    )
    db.commit()
    return result.rowcount > 0


# ---------------- Customers ----------------

def list_customers(db: Session):
    rows = db.execute(text("SELECT * FROM customers ORDER BY id")).mappings().all()
    return [dict(r) for r in rows]


def get_customer(db: Session, customer_id: int):
    row = db.execute(
        text("SELECT * FROM customers WHERE id = :id"),
        {"id": customer_id},
    ).mappings().first()
    return dict(row) if row else None


def create_customer(db: Session, c):
    result = db.execute(
        text("INSERT INTO customers (name, email) VALUES (:name, :email)"),
        c.dict(),
    )
    db.commit()
    return get_customer(db, result.lastrowid)


def update_customer(db: Session, customer_id: int, c):
    fields = {k: v for k, v in c.dict().items() if v is not None}
    if not fields:
        return get_customer(db, customer_id)
    assignments = ", ".join(f"{k} = :{k}" for k in fields)
    fields["id"] = customer_id
    db.execute(
        text(f"UPDATE customers SET {assignments} WHERE id = :id"),
        fields,
    )
    db.commit()
    return get_customer(db, customer_id)


def delete_customer(db: Session, customer_id: int) -> bool:
    result = db.execute(
        text("DELETE FROM customers WHERE id = :id"),
        {"id": customer_id},
    )
    db.commit()
    return result.rowcount > 0
