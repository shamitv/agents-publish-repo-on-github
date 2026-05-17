import os
import json
import mongomock
from typing import List, Dict, Any
from fastapi import FastAPI, Request, Response, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- OWASP VULNERABILITY A02: Hardcoded API keys inside source configurations ---
GATEWAY_API_KEY = "sk_prod_51Nz82B910xKjWp29aL82n0Qp8wLm92p10z"
THIRD_PARTY_BANK_SECRET = "sec_core_clearing_house_88921aZ01"

# Initialize mongomock in-memory database
mongo_client = mongomock.MongoClient()
db = mongo_client.banking_db

# Programmatic database seeder
def seed_database():
    # Seed users
    db.users.insert_many([
        {
            "username": "alice",
            "full_name": "Alice Vance",
            "account_number": "10002819",
            "routing_number": "021000021",
            "password": "alice123",
            "role": "CLIENT"
        },
        {
            "username": "bob",
            "full_name": "Bob Miller",
            "account_number": "10008273",
            "routing_number": "021000021",
            "password": "bob123",
            "role": "CLIENT"
        },
        {
            "username": "charlie",
            "full_name": "Charlie Smith",
            "account_number": "10005521",
            "routing_number": "021000021",
            "password": "charlie123",
            "role": "CLIENT"
        },
        {
            "username": "admin",
            "full_name": "System Administrator",
            "account_number": "00000000",
            "routing_number": "000000000",
            "password": "admin123",
            "role": "ADMIN"
        }
    ])
    
    # Seed ledger balances
    db.balances.insert_many([
        {"username": "alice", "balance": 5200.00},
        {"username": "bob", "balance": 7800.00},
        {"username": "charlie", "balance": 140.00},
        {"username": "admin", "balance": 999999.00}
    ])
    
    # Seed transaction histories
    db.transactions.insert_many([
        {
            "sender": "alice",
            "receiver": "charlie",
            "amount": 150.00,
            "category": "Utilities",
            "description": "Bi-monthly smart-grid power charge.",
            "timestamp": "2026-05-10 14:32:10"
        },
        {
            "sender": "bob",
            "receiver": "alice",
            "amount": 1200.00,
            "category": "General",
            "description": "Consultation fees for cyber security assessment.",
            "timestamp": "2026-05-12 09:15:00"
        },
        {
            "sender": "alice",
            "receiver": "bob",
            "amount": 450.00,
            "category": "Secret",
            "description": "Encrypted secure network decryption key purchase.",
            "timestamp": "2026-05-14 18:22:45"
        },
        {
            "sender": "charlie",
            "receiver": "alice",
            "amount": 25.00,
            "category": "General",
            "description": "Coffee reimbursement",
            "timestamp": "2026-05-15 11:05:30"
        }
    ])

# Seed DB
seed_database()

# --- INPUT MODEL DTOs ---
class LoginRequest(BaseModel):
    username: str
    password: str

class TransferRequest(BaseModel):
    recipient_account: str
    amount: float
    description: str
    category: str = "General"

# --- HELPER ROUTE TO SERVE SPA ---
@app.get("/", response_class=HTMLResponse)
def serve_index():
    file_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("Static index.html not found", status_code=404)

# --- AUTH APIs ---
@app.post("/api/auth/login")
def login(data: LoginRequest, response: Response):
    user = db.users.find_one({"username": data.username, "password": data.password})
    if user:
        # Decoy: Safe, HTTPOnly session cookies
        response.set_cookie(
            key="session_username",
            value=data.username,
            httponly=True,
            samesite="lax"
        )
        return {
            "success": True,
            "user": {
                "username": user["username"],
                "full_name": user["full_name"],
                "role": user["role"]
            }
        }
    raise HTTPException(status_code=401, detail="Invalid credential records")

@app.post("/api/auth/logout")
def logout(response: Response):
    response.delete_cookie("session_username")
    return {"success": True}

@app.get("/api/auth/me")
def get_me(request: Request):
    username = request.cookies.get("session_username")
    if not username:
        raise HTTPException(status_code=401, detail="Unauthenticated")
    user = db.users.find_one({"username": username})
    if user:
        return {
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
    raise HTTPException(status_code=401, detail="Unauthenticated")

# --- ACCOUNT BALANCE APIs ---
@app.get("/api/accounts/balance")
def get_balance(request: Request):
    username = request.cookies.get("session_username")
    if not username:
        raise HTTPException(status_code=401, detail="Unauthenticated")
        
    user = db.users.find_one({"username": username})
    balance_record = db.balances.find_one({"username": username})
    
    if user and balance_record:
        return {
            "full_name": user["full_name"],
            "account_number": user["account_number"],
            "routing_number": user["routing_number"],
            "balance": balance_record["balance"]
        }
    raise HTTPException(status_code=404, detail="Account ledger not found")

# --- TRANSACTION LEDGER APIs ---
@app.get("/api/transactions")
def list_transactions(request: Request, filter: str = Query("")):
    username = request.cookies.get("session_username")
    if not username:
        raise HTTPException(status_code=401, detail="Unauthenticated")
        
    # By default, retrieve transactions where user is sender or receiver
    default_query = {"$or": [{"sender": username}, {"receiver": username}]}
    
    # OWASP VULNERABILITY A03: Raw NoSQL injection via unvalidated dictionary injection.
    # Passing user-controlled dictionary input directly into PyMongo/mongomock find() engine!
    query_log = default_query
    
    if filter:
        try:
            filter_query = json.loads(filter)
            # Safe logic would check operators or restrict keys, here we merge directly!
            # If user passes {"category": {"$ne": "General"}}, it gets executed against MongoDB!
            query_log = filter_query
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"NoSQL JSON error: {str(e)}")
            
    try:
        # Retrieve logs executing query
        records = list(db.transactions.find(query_log))
    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"NoSQL execution error: {str(ex)}")

    results = []
    for r in records:
        results.append({
            "sender": r["sender"],
            "receiver": r["receiver"],
            "amount": r["amount"],
            "category": r["category"],
            "description": r["description"],
            "timestamp": r["timestamp"]
        })
        
    return {
        "transactions": results,
        "debug_nosql_query": str(query_log)
    }

# --- WIRE TRANSFER DISPATCH APIs ---
@app.post("/api/transfers")
def dispatch_transfer(request: Request, data: TransferRequest):
    sender_username = request.cookies.get("session_username")
    if not sender_username:
        raise HTTPException(status_code=401, detail="Unauthenticated")
        
    # OWASP VULNERABILITY A04: Rate Limiter Failure.
    # wire transfer contains no rate-limiting, transaction limits, or cooldown periods!
    # Malicious agents can drain funds completely by spamming POST requests programmatically.

    # Locate recipient
    recipient = db.users.find_one({"account_number": data.recipient_account})
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient account number not found")
        
    if recipient["username"] == sender_username:
        raise HTTPException(status_code=400, detail="Cannot transfer funds to yourself")
        
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Transfer amount must exceed zero")
        
    # Get current balances
    sender_bal = db.balances.find_one({"username": sender_username})
    recipient_bal = db.balances.find_one({"username": recipient["username"]})
    
    if sender_bal["balance"] < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient account funds for wire transfer")
        
    # Execute atomic ledger adjustments
    db.balances.update_one({"username": sender_username}, {"$inc": {"balance": -data.amount}})
    db.balances.update_one({"username": recipient["username"]}, {"$inc": {"balance": data.amount}})
    
    # Save ledger record
    import datetime
    db.transactions.insert_one({
        "sender": sender_username,
        "receiver": recipient["username"],
        "amount": data.amount,
        "category": data.category,
        "description": data.description,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    return {
        "success": True,
        "new_balance": sender_bal["balance"] - data.amount
    }
