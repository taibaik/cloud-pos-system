"""
Cloud POS System — FastAPI backend.

Cloud-ready version: the same code runs locally and on AWS EC2 + RDS.
Only the DATABASE_URL environment variable changes between environments.
"""

import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db, engine, DATABASE_URL
from app import crud, schemas

app = FastAPI(
    title="Cloud POS System",
    version="1.0.0",
    description="On-premise POS transformed into a cloud-based platform (AWS EC2 + RDS).",
)

# "rds" appears in Amazon RDS endpoints; used only to label the dashboard.
DEPLOY_ENV = "AWS Cloud (RDS)" if "rds" in DATABASE_URL else "Local Development"


@app.get("/health")
def health(db: Session = Depends(get_db)):
    """Liveness + DB connectivity probe (used by load balancers / monitoring)."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected", "environment": DEPLOY_ENV}
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=503, detail=f"database unavailable: {exc}")


# ---------------- Products: full CRUD ----------------

@app.get("/products", response_model=list[schemas.Product])
def get_products(db: Session = Depends(get_db)):
    return crud.list_products(db)


@app.get("/products/{product_id}", response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/products", response_model=schemas.Product, status_code=201)
def create_product(payload: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db, payload)


@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, payload: schemas.ProductUpdate, db: Session = Depends(get_db)):
    if not crud.get_product(db, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.update_product(db, product_id, payload)


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    if not crud.delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return {"deleted": product_id}


# ---------------- Customers: full CRUD ----------------

@app.get("/customers", response_model=list[schemas.Customer])
def get_customers(db: Session = Depends(get_db)):
    return crud.list_customers(db)


@app.get("/customers/{customer_id}", response_model=schemas.Customer)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.post("/customers", response_model=schemas.Customer, status_code=201)
def create_customer(payload: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db, payload)


@app.put("/customers/{customer_id}", response_model=schemas.Customer)
def update_customer(customer_id: int, payload: schemas.CustomerUpdate, db: Session = Depends(get_db)):
    if not crud.get_customer(db, customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    return crud.update_customer(db, customer_id, payload)


@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    if not crud.delete_customer(db, customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"deleted": customer_id}


# ---------------- Dashboard ----------------

@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cloud POS Dashboard</title>
        <style>
            body{{margin:0;font-family:Arial,Helvetica,sans-serif;background:#0f172a;color:#fff;}}
            .navbar{{background:#111827;padding:20px 40px;display:flex;justify-content:space-between;
                     align-items:center;border-bottom:1px solid #1f2937;}}
            .navbar h1{{margin:0;font-size:24px;color:#38bdf8;}}
            .status{{background:#16a34a;padding:8px 14px;border-radius:20px;font-size:14px;}}
            .container{{max-width:1200px;margin:auto;padding:40px;}}
            .hero h2{{font-size:42px;margin-bottom:10px;}}
            .hero p{{color:#94a3b8;font-size:18px;}}
            .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:20px;
                   margin-top:30px;}}
            .card{{background:#1e293b;padding:25px;border-radius:16px;
                   box-shadow:0 4px 12px rgba(0,0,0,.3);}}
            .card h3{{margin-top:0;color:#38bdf8;}}
            .endpoint{{margin-top:10px;background:#0f172a;padding:10px;border-radius:10px;
                       font-family:monospace;color:#4ade80;}}
            .footer{{margin-top:50px;text-align:center;color:#64748b;font-size:14px;}}
            a{{color:#38bdf8;text-decoration:none;}}
        </style>
    </head>
    <body>
        <div class="navbar">
            <h1>Cloud POS System</h1>
            <div class="status">API ONLINE</div>
        </div>
        <div class="container">
            <div class="hero">
                <h2>Smart Retail Cloud Dashboard</h2>
                <p>Cloud Computing Project — Universitas Gadjah Mada</p>
            </div>
            <div class="grid">
                <div class="card">
                    <h3>Environment</h3>
                    <p>{DEPLOY_ENV}</p>
                </div>
                <div class="card">
                    <h3>Database</h3>
                    <p>Managed MySQL via Amazon RDS (env-driven connection).</p>
                </div>
                <div class="card">
                    <h3>Implemented Features</h3>
                    <ul>
                        <li>Full CRUD REST API</li>
                        <li>Swagger Docs</li>
                        <li>Products &amp; Customers</li>
                        <li>Health probe</li>
                    </ul>
                </div>
                <div class="card">
                    <h3>Available Endpoints</h3>
                    <div class="endpoint">GET/POST/PUT/DELETE /products</div>
                    <div class="endpoint">GET/POST/PUT/DELETE /customers</div>
                    <div class="endpoint">GET /health</div>
                    <div class="endpoint"><a href="/docs">Swagger Documentation</a></div>
                </div>
            </div>
            <div class="footer">Developed for Cloud Computing Course Project 2026</div>
        </div>
    </body>
    </html>
    """
