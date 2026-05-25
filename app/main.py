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
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/products", response_model=schemas.Product, status_code=201)
def create_product(payload: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db, payload)


@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: str, payload: schemas.ProductUpdate, db: Session = Depends(get_db)):
    if not crud.get_product(db, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.update_product(db, product_id, payload)


@app.delete("/products/{product_id}")
def delete_product(product_id: str, db: Session = Depends(get_db)):
    if not crud.delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return {"deleted": product_id}


# ---------------- Customers: full CRUD ----------------

@app.get("/customers", response_model=list[schemas.Customer])
def get_customers(db: Session = Depends(get_db)):
    return crud.list_customers(db)


@app.get("/customers/{customer_id}", response_model=schemas.Customer)
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.post("/customers", response_model=schemas.Customer, status_code=201)
def create_customer(payload: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db, payload)


@app.put("/customers/{customer_id}", response_model=schemas.Customer)
def update_customer(customer_id: str, payload: schemas.CustomerUpdate, db: Session = Depends(get_db)):
    if not crud.get_customer(db, customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    return crud.update_customer(db, customer_id, payload)


@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: str, db: Session = Depends(get_db)):
    if not crud.delete_customer(db, customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"deleted": customer_id}


# ---------------- Categories, Locations & Tickets ----------------

@app.get("/categories", response_model=list[schemas.Category])
def get_categories(db: Session = Depends(get_db)):
    return crud.list_categories(db)


@app.get("/locations", response_model=list[schemas.Location])
def get_locations(db: Session = Depends(get_db)):
    return crud.list_locations(db)


@app.get("/tickets", response_model=list[schemas.Ticket])
def get_tickets(db: Session = Depends(get_db)):
    return crud.list_tickets(db)


@app.get("/tickets/{ticket_id}", response_model=schemas.TicketWithLines)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = crud.get_ticket_with_lines(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


# ---------------- Dashboard ----------------

@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>UGM Cloud POS Console</title>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-main: #0b0f19;
                --bg-card: #151b2c;
                --bg-active: #1d253f;
                --border-color: rgba(255, 255, 255, 0.08);
                --text-main: #f3f4f6;
                --text-secondary: #9ca3af;
                --accent-blue: #38bdf8;
                --accent-emerald: #10b981;
                --accent-purple: #a855f7;
            }}
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}
            body {{
                font-family: 'Plus Jakarta Sans', sans-serif;
                background-color: var(--bg-main);
                background-image: 
                    radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.05) 0px, transparent 50%),
                    radial-gradient(at 100% 100%, rgba(168, 85, 247, 0.05) 0px, transparent 50%);
                color: var(--text-main);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                line-height: 1.5;
            }}
            header {{
                background-color: rgba(21, 27, 44, 0.8);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border-bottom: 1px solid var(--border-color);
                padding: 16px 40px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                position: sticky;
                top: 0;
                z-index: 100;
            }}
            .brand {{
                display: flex;
                align-items: center;
                gap: 10px;
                font-weight: 800;
                font-size: 20px;
                letter-spacing: -0.5px;
                background: linear-gradient(135deg, var(--accent-blue), #60a5fa);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .sys-badge {{
                background-color: rgba(16, 185, 129, 0.08);
                border: 1px solid rgba(16, 185, 129, 0.15);
                color: var(--accent-emerald);
                padding: 6px 14px;
                border-radius: 9999px;
                font-size: 12px;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            .pulse-dot {{
                width: 8px;
                height: 8px;
                background-color: var(--accent-emerald);
                border-radius: 50%;
                animation: pulse-animation 2s infinite;
            }}
            @keyframes pulse-animation {{
                0% {{ opacity: 0.4; }}
                50% {{ opacity: 1; }}
                100% {{ opacity: 0.4; }}
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 30px 20px;
                width: 100%;
                display: flex;
                flex-direction: column;
                gap: 25px;
                flex: 1;
            }}
            
            /* Overview Cards */
            .grid-stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
                gap: 20px;
            }}
            .card-stat {{
                background-color: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: 12px;
                padding: 24px;
                display: flex;
                flex-direction: column;
                gap: 6px;
                transition: border-color 0.2s ease;
            }}
            .card-stat:hover {{
                border-color: rgba(56, 189, 248, 0.2);
            }}
            .card-title {{
                font-size: 13px;
                color: var(--text-secondary);
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-weight: 600;
            }}
            .card-value {{
                font-size: 28px;
                font-weight: 700;
                color: var(--text-main);
            }}
            
            /* Hybrid Architecture Map */
            .panel-arch {{
                background-color: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: 12px;
                padding: 24px;
            }}
            .arch-title {{
                font-size: 15px;
                font-weight: 700;
                margin-bottom: 15px;
                color: var(--accent-blue);
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .pipeline {{
                display: flex;
                flex-direction: column;
                gap: 15px;
            }}
            @media (min-width: 768px) {{
                .pipeline {{
                    flex-direction: row;
                    align-items: center;
                    justify-content: space-between;
                }}
            }}
            .pipe-node {{
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 16px;
                flex: 1;
                text-align: center;
                font-size: 14px;
            }}
            .pipe-node h4 {{
                font-weight: 600;
                margin-bottom: 4px;
                color: var(--text-main);
            }}
            .pipe-node p {{
                font-size: 12px;
                color: var(--text-secondary);
            }}
            .pipe-arrow {{
                text-align: center;
                color: var(--accent-blue);
                font-weight: bold;
                font-size: 18px;
            }}
            @media (min-width: 768px) {{
                .pipe-arrow {{
                    transform: rotate(0deg);
                }}
            }}
            
            /* Data Explorer Panel */
            .panel-explorer {{
                background-color: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: 12px;
                padding: 24px;
                display: flex;
                flex-direction: column;
                gap: 20px;
                flex: 1;
            }}
            .explorer-header {{
                display: flex;
                flex-direction: column;
                gap: 15px;
                justify-content: space-between;
                border-bottom: 1px solid var(--border-color);
                padding-bottom: 15px;
            }}
            @media (min-width: 768px) {{
                .explorer-header {{
                    flex-direction: row;
                    align-items: center;
                }}
            }}
            .nav-tabs {{
                display: flex;
                gap: 8px;
                overflow-x: auto;
            }}
            .tab-btn {{
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid var(--border-color);
                color: var(--text-secondary);
                padding: 8px 16px;
                border-radius: 6px;
                font-family: inherit;
                font-weight: 600;
                font-size: 13px;
                cursor: pointer;
                transition: all 0.2s ease;
                white-space: nowrap;
            }}
            .tab-btn:hover, .tab-btn.active-tab {{
                background-color: rgba(56, 189, 248, 0.08);
                border-color: var(--accent-blue);
                color: var(--accent-blue);
            }}
            .view-toggles {{
                display: flex;
                gap: 6px;
                background-color: rgba(0, 0, 0, 0.2);
                padding: 4px;
                border-radius: 8px;
                border: 1px solid var(--border-color);
                align-self: flex-start;
            }}
            .toggle-btn {{
                background: none;
                border: none;
                color: var(--text-secondary);
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
                cursor: pointer;
                font-family: inherit;
                transition: all 0.2s ease;
            }}
            .toggle-btn.active-toggle {{
                background-color: var(--bg-active);
                color: var(--accent-blue);
            }}
            
            .content-display {{
                background-color: rgba(0, 0, 0, 0.15);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                min-height: 350px;
                overflow: auto;
                position: relative;
            }}
            
            /* Styled Tables */
            .data-table {{
                width: 100%;
                border-collapse: collapse;
                text-align: left;
                font-size: 14px;
            }}
            .data-table th {{
                background-color: rgba(255, 255, 255, 0.01);
                color: var(--text-secondary);
                font-weight: 600;
                padding: 12px 18px;
                border-bottom: 1px solid var(--border-color);
            }}
            .data-table td {{
                padding: 14px 18px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.03);
                color: var(--text-main);
            }}
            .data-table tr:hover {{
                background-color: rgba(255, 255, 255, 0.01);
            }}
            .tag {{
                font-size: 11px;
                font-weight: 700;
                padding: 2px 8px;
                border-radius: 4px;
                background-color: rgba(16, 185, 129, 0.1);
                color: var(--accent-emerald);
            }}
            
            /* Pretty JSON Code Block */
            .code-block {{
                font-family: 'JetBrains Mono', monospace;
                font-size: 13px;
                padding: 20px;
                line-height: 1.5;
                white-space: pre;
            }}
            .json-string {{ color: #a7f3d0; }}
            .json-number {{ color: #f59e0b; }}
            .json-boolean {{ color: #60a5fa; }}
            .json-null {{ color: #f87171; }}
            .json-key {{ color: #38bdf8; }}
            
            footer {{
                text-align: center;
                color: var(--text-secondary);
                font-size: 13px;
                padding: 25px 0;
                border-top: 1px solid var(--border-color);
                background-color: rgba(21, 27, 44, 0.4);
                margin-top: auto;
            }}
            
            .loading-spinner {{
                display: flex;
                justify-content: center;
                align-items: center;
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background-color: var(--bg-card);
                color: var(--accent-blue);
                font-weight: 600;
                font-size: 14px;
                gap: 10px;
            }}
        </style>
    </head>
    <body>
        <header>
            <div class="brand">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                    <path d="M2 17L12 22L22 17"/>
                    <path d="M2 12L12 17L22 12"/>
                </svg>
                UGM CLOUD POS
            </div>
            <div class="sys-badge">
                <span class="pulse-dot"></span>
                API ONLINE // {DEPLOY_ENV.upper()}
            </div>
        </header>
        
        <div class="container">
            <!-- Stats Dashboard -->
            <div class="grid-stats">
                <div class="card-stat">
                    <span class="card-title">Environment</span>
                    <span class="card-value" style="color: var(--accent-blue); font-size: 20px; font-weight: 600; margin-top: 8px;">{DEPLOY_ENV}</span>
                </div>
                <div class="card-stat">
                    <span class="card-title">Catalog Size</span>
                    <span class="card-value" id="count-products">5 Products</span>
                </div>
                <div class="card-stat">
                    <span class="card-title">Registered Customers</span>
                    <span class="card-value" id="count-customers">3 Accounts</span>
                </div>
                <div class="card-stat">
                    <span class="card-title">Cloud Integration</span>
                    <span class="card-value" style="color: var(--accent-emerald);">Active</span>
                </div>
            </div>
            
            <!-- CSS Flow Topology Map -->
            <div class="panel-arch">
                <div class="arch-title">Hybrid Architecture Infrastructure</div>
                <div class="pipeline">
                    <div class="pipe-node">
                        <h4>Chromis Desktop POS</h4>
                        <p>On-Premises Store Client</p>
                    </div>
                    <div class="pipe-arrow">➔</div>
                    <div class="pipe-node">
                        <h4>Cloud Sync Agent</h4>
                        <p>Gateway Sync Daemon</p>
                    </div>
                    <div class="pipe-arrow">➔</div>
                    <div class="pipe-node">
                        <h4>FastAPI Backend Node</h4>
                        <p>AWS EC2 Server Subnet</p>
                    </div>
                    <div class="pipe-arrow">➔</div>
                    <div class="pipe-node">
                        <h4>MySQL Database Node</h4>
                        <p>Amazon RDS Cluster</p>
                    </div>
                </div>
            </div>
            
            <!-- Real-Time Data Explorer Panel -->
            <div class="panel-explorer">
                <div class="explorer-header">
                    <div class="nav-tabs">
                        <button class="tab-btn active-tab" onclick="switchTab(this, 'products')">Products</button>
                        <button class="tab-btn" onclick="switchTab(this, 'customers')">Customers</button>
                        <button class="tab-btn" onclick="switchTab(this, 'categories')">Categories</button>
                        <button class="tab-btn" onclick="switchTab(this, 'locations')">Locations</button>
                        <button class="tab-btn" onclick="switchTab(this, 'tickets')">Transactions</button>
                    </div>
                    
                    <div class="view-toggles">
                        <button class="toggle-btn active-toggle" onclick="switchView(this, 'table')">Table View</button>
                        <button class="toggle-btn" onclick="switchView(this, 'json')">Raw JSON</button>
                    </div>
                </div>
                
                <div class="content-display" id="dataContainer">
                    <!-- Dynamic Content populated via JavaScript -->
                    <div class="loading-spinner">Initializing explorer node...</div>
                </div>
            </div>
        </div>
        
        <footer>
            Universitas Gadjah Mada — Cloud Computing Final Project 2026
        </footer>
        
        <script>
            let currentTab = 'products';
            let currentView = 'table';
            let cachedData = {{}};

            function showLoader() {{
                document.getElementById('dataContainer').innerHTML = '<div class="loading-spinner">Querying RDS database instance...</div>';
            }}

            async function fetchData(endpoint) {{
                if (cachedData[endpoint]) {{
                    return cachedData[endpoint];
                }}
                try {{
                    const res = await fetch(endpoint);
                    if (!res.ok) throw new Error('HTTP Query Failed');
                    const data = await res.json();
                    cachedData[endpoint] = data;
                    return data;
                }} catch (err) {{
                    return null;
                }}
            }}

            function highlightJSON(json) {{
                if (typeof json !== 'string') {{
                    json = JSON.stringify(json, null, 2);
                }}
                json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                return json.replace(/("(\\u[a-zA-Z0-9]{{4}}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)/g, function (match) {{
                    let cls = 'json-number';
                    if (/^"/.test(match)) {{
                        if (/:$/.test(match)) {{
                            cls = 'json-key';
                        }} else {{
                            cls = 'json-string';
                        }}
                    }} else if (/true|false/.test(match)) {{
                        cls = 'json-boolean';
                    }} else if (/null/.test(match)) {{
                        cls = 'json-null';
                    }}
                    return '<span class="' + cls + '">' + match + '</span>';
                }});
            }}

            function renderJSONView(data) {{
                const highlighted = highlightJSON(data);
                document.getElementById('dataContainer').innerHTML = `<pre class="code-block">${{highlighted}}</pre>`;
            }}

            function renderTableView(data, tab) {{
                if (!data || data.length === 0) {{
                    document.getElementById('dataContainer').innerHTML = '<div class="loading-spinner" style="color: var(--text-secondary)">No records found in target table.</div>';
                    return;
                }}

                let html = '<table class="data-table"><thead><tr>';
                
                if (tab === 'products') {{
                    html += '<th>Product ID</th><th>Name</th><th>Sell Price</th><th>Stock Level</th><th>Barcode</th><th>Sync Status</th>';
                    html += '</tr></thead><tbody>';
                    data.forEach(item => {{
                        html += `<tr>
                            <td><code>${{item.id}}</code></td>
                            <td style="font-weight: 600;">${{item.name}}</td>
                            <td>Rp ${{Number(item.pricesell).toLocaleString('id-ID')}}</td>
                            <td style="font-weight: 500; color: ${{item.stockcurrent > 0 ? 'var(--text-main)' : '#f87171'}}">${{item.stockcurrent}}</td>
                            <td>${{item.barcode || '—'}}</td>
                            <td><span class="tag">${{item.sync_status}}</span></td>
                        </tr>`;
                    }});
                }} else if (tab === 'customers') {{
                    html += '<th>Customer ID</th><th>Name</th><th>Email Address</th><th>Phone Number</th><th>Loyalty Points</th><th>Sync Status</th>';
                    html += '</tr></thead><tbody>';
                    data.forEach(item => {{
                        html += `<tr>
                            <td><code>${{item.id}}</code></td>
                            <td style="font-weight: 600;">${{item.name}}</td>
                            <td>${{item.email || '—'}}</td>
                            <td>${{item.phone || '—'}}</td>
                            <td>${{item.loyaltypoints}} pts</td>
                            <td><span class="tag">${{item.sync_status}}</span></td>
                        </tr>`;
                    }});
                }} else if (tab === 'categories') {{
                    html += '<th>Category ID</th><th>Category Name</th><th>Parent Node</th><th>Sync Status</th>';
                    html += '</tr></thead><tbody>';
                    data.forEach(item => {{
                        html += `<tr>
                            <td><code>${{item.id}}</code></td>
                            <td style="font-weight: 600;">${{item.name}}</td>
                            <td>${{item.parentid || 'None (Root)'}}</td>
                            <td><span class="tag">${{item.sync_status}}</span></td>
                        </tr>`;
                    }});
                }} else if (tab === 'locations') {{
                    html += '<th>Branch Code</th><th>Branch Name</th><th>Physical Address</th>';
                    html += '</tr></thead><tbody>';
                    data.forEach(item => {{
                        html += `<tr>
                            <td><code>${{item.id}}</code></td>
                            <td style="font-weight: 600;">${{item.name}}</td>
                            <td>${{item.address || '—'}}</td>
                        </tr>`;
                    }});
                }} else if (tab === 'tickets') {{
                    html += '<th>Ticket Reference</th><th>Created Timestamp</th><th>Customer Ref</th><th>Cashier Person</th><th>Total Amount</th><th>Sync Status</th>';
                    html += '</tr></thead><tbody>';
                    data.forEach(item => {{
                        html += `<tr>
                            <td><code>${{item.id}}</code></td>
                            <td>${{new Date(item.datenew).toLocaleString('id-ID')}}</td>
                            <td><code>${{item.customer || 'Guest'}}</code></td>
                            <td>${{item.person}}</td>
                            <td style="font-weight: 600; color: var(--accent-blue)">Rp ${{Number(item.total).toLocaleString('id-ID')}}</td>
                            <td><span class="tag">${{item.sync_status}}</span></td>
                        </tr>`;
                    }});
                }}
                
                html += '</tbody></table>';
                document.getElementById('dataContainer').innerHTML = html;
            }}

            async function updateDisplay() {{
                showLoader();
                const data = await fetchData('/' + currentTab);
                
                if (currentView === 'json') {{
                    renderJSONView(data);
                }} else {{
                    renderTableView(data, currentTab);
                }}

                // Update Overview count badges
                if (currentTab === 'products' && data) {{
                    document.getElementById('count-products').innerText = data.length + ' Products';
                }} else if (currentTab === 'customers' && data) {{
                    document.getElementById('count-customers').innerText = data.length + ' Accounts';
                }}
            }}

            function switchTab(btn, tab) {{
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active-tab'));
                btn.classList.add('active-tab');
                currentTab = tab;
                updateDisplay();
            }}

            function switchView(btn, view) {{
                document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active-toggle'));
                btn.classList.add('active-toggle');
                currentView = view;
                updateDisplay();
            }}

            // Run initial load
            updateDisplay();
        </script>
    </body>
    </html>
    """
