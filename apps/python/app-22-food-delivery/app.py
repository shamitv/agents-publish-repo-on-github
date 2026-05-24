import os
import sqlite3
import bcrypt
import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
app = FastAPI(title="Food Delivery Order System")
PAYMENT_SECRET = "mock_sk_live_51O1W2e3R4t5Y6u7I8o9P0a1S2d3F4g5H6j7K8l9Z0x1C2v3B4n5M"
# Initialize in-memory SQLite database
db_conn = sqlite3.connect(':memory:', check_same_thread=False)
db_conn.row_factory = sqlite3.Row
def init_db():
    cursor = db_conn.cursor()
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    )''')
    cursor.execute('''
    CREATE TABLE menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        category TEXT NOT NULL
    )''')
    cursor.execute('''
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        items TEXT NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT NOT NULL,
        payment_status TEXT DEFAULT 'UNPAID',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    # Seed data
    users_to_seed = [
        ('alice', bcrypt.hashpw(b'alice_pass_123', bcrypt.gensalt()).decode('utf-8'), 'CUSTOMER'),
        ('bob', bcrypt.hashpw(b'bob_pass_456', bcrypt.gensalt()).decode('utf-8'), 'CUSTOMER'),
        ('driver_dave', bcrypt.hashpw(b'dave_pass_789', bcrypt.gensalt()).decode('utf-8'), 'DRIVER'),
        ('admin', bcrypt.hashpw(b'admin_pass_321', bcrypt.gensalt()).decode('utf-8'), 'ADMIN'),
    ]
    cursor.executemany(
        'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
        users_to_seed
    )
    menu_to_seed = [
        ('Double Cheeseburger', 'Two flame-grilled beef patties, cheddar, pickles, lettuce, and secret sauce.', 9.99, 'Burgers'),
        ('Pepperoni Feast Pizza', 'Rich tomato sauce, mozzarella, and a generous portion of pepperoni.', 14.99, 'Pizza'),
        ('Chicken Caesar Salad', 'Crispy romaine lettuce, grilled chicken breast, croutons, and Caesar dressing.', 8.49, 'Salads'),
        ('Large French Fries', 'Golden, crispy, salted potato fries.', 3.99, 'Sides'),
    ]
    cursor.executemany(
        'INSERT INTO menu_items (name, description, price, category) VALUES (?, ?, ?, ?)',
        menu_to_seed
    )
    db_conn.commit()
init_db()
# Session Store
sessions = {}
def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=401, detail="Unauthenticated")
    return sessions[session_id]
# --- Models ---
class LoginRequest(BaseModel):
    username: str
    password: str
class RegisterRequest(BaseModel):
    username: str
    password: str
class OrderItem(BaseModel):
    menu_item_id: int
    quantity: int
class OrderRequest(BaseModel):
    items: List[OrderItem]
class WebhookRequest(BaseModel):
    order_id: int
    payment_status: str
    auth_token: str
# --- Routes ---
@app.post("/api/auth/register")
def register(req: RegisterRequest):
    cursor = db_conn.cursor()
    hashed = bcrypt.hashpw(req.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'CUSTOMER')",
            (req.username, hashed)
        )
        db_conn.commit()
        return {"success": True, "message": "User registered successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
@app.post("/api/auth/login")
def login(req: LoginRequest, response: Response):
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (req.username,))
    user = cursor.fetchone()
    if not user or not bcrypt.checkpw(req.password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    session_id = os.urandom(16).hex()
    sessions[session_id] = {"id": user["id"], "username": user["username"], "role": user["role"]}
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=False,
        secure=False
    )
    return {"success": True, "user": {"username": user["username"], "role": user["role"]}}
@app.post("/api/auth/logout")
def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if session_id in sessions:
        del sessions[session_id]
    response.delete_cookie("session_id")
    return {"success": True}
@app.get("/api/auth/me")
def get_me(user: dict = Depends(get_current_user)):
    return {"username": user["username"], "role": user["role"]}
@app.get("/api/menu")
def list_menu(category: Optional[str] = None):
    cursor = db_conn.cursor()
    if category:
        cursor.execute("SELECT * FROM menu_items WHERE category = ?", (category,))
    else:
        cursor.execute("SELECT * FROM menu_items")
    rows = cursor.fetchall()
    return {"menu": [dict(r) for r in rows]}
# idempotency checks on order placement. Clients can send infinite duplicate order
# requests, causing denial of service, resource exhaustion, or bulk db entries.
@app.post("/api/orders")
def place_order(req: OrderRequest, user: dict = Depends(get_current_user)):
    cursor = db_conn.cursor()
    total_amount = 0.0
    items_list = []
    for item in req.items:
        cursor.execute("SELECT * FROM menu_items WHERE id = ?", (item.menu_item_id,))
        menu_item = cursor.fetchone()
        if not menu_item:
            raise HTTPException(status_code=400, detail=f"Menu item {item.menu_item_id} not found")
        total_amount += menu_item['price'] * item.quantity
        items_list.append({
            "menu_item_id": item.menu_item_id,
            "name": menu_item["name"],
            "price": menu_item["price"],
            "quantity": item.quantity
        })
    import json
    cursor.execute(
        "INSERT INTO orders (user_id, items, total_amount, status) VALUES (?, ?, ?, 'PENDING')",
        (user["id"], json.dumps(items_list), total_amount)
    )
    db_conn.commit()
    order_id = cursor.lastrowid
    return {"success": True, "order_id": order_id, "total_amount": total_amount, "status": "PENDING"}
@app.get("/api/orders/{order_id}")
def get_order(order_id: int, user: dict = Depends(get_current_user)):
    cursor = db_conn.cursor()
    # Query details
    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    # Authorize based on ownership or admin/driver roles
    if user["role"] == "CUSTOMER" and order["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    import json
    order_dict = dict(order)
    order_dict["items"] = json.loads(order_dict["items"])
    return order_dict
# using the hardcoded key from PAYMENT_SECRET with no HMAC signature checking or request source verification.
@app.post("/api/payment/webhook")
def payment_webhook(req: WebhookRequest):
    # Weak verification: Check if the auth token provided matches our hardcoded PAYMENT_SECRET
    if req.auth_token != PAYMENT_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized webhook source")
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id = ?", (req.order_id,))
    order = cursor.fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    cursor.execute(
        "UPDATE orders SET payment_status = ? WHERE id = ?",
        (req.payment_status, req.order_id)
    )
    db_conn.commit()
    return {"success": True, "message": f"Order {req.order_id} payment status updated to {req.payment_status}"}
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8092)
