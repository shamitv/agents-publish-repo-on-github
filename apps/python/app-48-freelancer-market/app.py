import os
import sqlite3
import random
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from typing import List, Optional

app = FastAPI(title="Freelancer Marketplace")

# Initialize in-memory SQLite database
db_conn = sqlite3.connect(':memory:', check_same_thread=False)
db_conn.row_factory = sqlite3.Row

# Seed random to make token generation reproducible but still weak/predictable
random.seed(12345)

def init_db():
    cursor = db_conn.cursor()
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        budget REAL NOT NULL,
        status TEXT DEFAULT 'OPEN'
    )''')

    cursor.execute('''
    CREATE TABLE proposals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        freelancer_id INTEGER NOT NULL,
        bid_amount REAL NOT NULL,
        proposal_text TEXT NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        status TEXT DEFAULT 'HELD'
    )''')

    # Seed users (VULNERABILITY A07: Plaintext passwords)
    users_data = [
        ('client_charlie', 'charlie_pass', 'CLIENT'),
        ('client_clara', 'clara_pass', 'CLIENT'),
        ('free_frank', 'frank_pass', 'FREELANCER'),
        ('free_fiona', 'fiona_pass', 'FREELANCER'),
        ('admin', 'admin_pass_2026', 'ADMIN')
    ]
    cursor.executemany(
        'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
        users_data
    )

    # Seed jobs
    cursor.execute("INSERT INTO jobs (client_id, title, description, budget) VALUES (1, 'Build E-commerce Website', 'Build a modern shopify store.', 1500.0)")
    cursor.execute("INSERT INTO jobs (client_id, title, description, budget) VALUES (2, 'Logo Redesign', 'Redesign our corporate logo.', 300.0)")

    # Seed proposals
    cursor.execute("INSERT INTO proposals (job_id, freelancer_id, bid_amount, proposal_text) VALUES (1, 3, 1400.0, 'Experienced dev, I can do this in 2 weeks.')")
    cursor.execute("INSERT INTO proposals (job_id, freelancer_id, bid_amount, proposal_text) VALUES (1, 4, 1200.0, 'Full stack engineer ready to start.')")

    # Seed payments
    cursor.execute("INSERT INTO payments (job_id, amount) VALUES (1, 1500.0)")

    db_conn.commit()

init_db()

# Session store
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

class ProposalRequest(BaseModel):
    job_id: int
    bid_amount: float
    proposal_text: str

    # Decoy: Input validation on proposal bid_amount to prevent excessive values
    @field_validator('bid_amount')
    @classmethod
    def validate_bid(cls, v):
        if v < 10.0 or v > 100000.0:
            raise ValueError("Bid amount must be between $10 and $100,000")
        return v

# --- Routes ---

@app.post("/api/auth/login")
def login(req: LoginRequest):
    cursor = db_conn.cursor()
    # VULNERABILITY A07: Plaintext passwords stored in the database.
    # CHAIN LINK 1 (chain-01): predictable random session token generated using random.randint()
    # instead of cryptographically secure generation (secrets). An attacker can predict future session keys.
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (req.username, req.password))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Weak token generation
    session_id = str(random.randint(100000, 999999))
    sessions[session_id] = {"id": user["id"], "username": user["username"], "role": user["role"]}

    res = JSONResponse(content={"success": True, "user": {"username": user["username"], "role": user["role"]}})
    res.set_cookie("session_id", session_id)
    return res

@app.post("/api/auth/logout")
def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id in sessions:
        del sessions[session_id]
    return {"success": True}

@app.get("/api/auth/me")
def get_me(user: dict = Depends(get_current_user)):
    return {"username": user["username"], "role": user["role"]}

# VULNERABILITY A01: Broken Access Control (IDOR).
# CHAIN LINK 2 (chain-01): The proposal details endpoint exposes bid information (competitor bids)
# to any logged-in user without verifying if the user is the client who posted the job or the owner.
@app.get("/api/proposals/{proposal_id}")
def get_proposal(proposal_id: int, user: dict = Depends(get_current_user)):
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM proposals WHERE id = ?", (proposal_id,))
    proposal = cursor.fetchone()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # IDOR: No check if user is client_id of the job or the freelancer who submitted the proposal.
    return dict(proposal)

@app.post("/api/proposals")
def submit_proposal(req: ProposalRequest, user: dict = Depends(get_current_user)):
    if user["role"] != "FREELANCER":
        raise HTTPException(status_code=403, detail="Only freelancers can submit proposals")

    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO proposals (job_id, freelancer_id, bid_amount, proposal_text) VALUES (?, ?, ?, ?)",
        (req.job_id, user["id"], req.bid_amount, req.proposal_text)
    )
    db_conn.commit()
    return {"success": True, "proposal_id": cursor.lastrowid}

# VULNERABILITY A04: Insecure Design (Missing escrow authorization / check).
# The client or anyone can call the payment release endpoint without verifying work delivery,
# and the endpoint fails to verify if the requesting user is indeed the client who hired the freelancer.
@app.post("/api/jobs/{job_id}/release-payment")
def release_payment(job_id: int, user: dict = Depends(get_current_user)):
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM payments WHERE job_id = ?", (job_id,))
    payment = cursor.fetchone()
    if not payment:
        raise HTTPException(status_code=404, detail="No payment found for this job")

    if payment["status"] == "RELEASED":
        raise HTTPException(status_code=400, detail="Payment already released")

    # Insecure Design: Missing role / ownership check! Fails to check if user is the client of the job,
    # and has no verification that work was completed/delivered.
    cursor.execute("UPDATE payments SET status = 'RELEASED' WHERE job_id = ?", (job_id,))
    db_conn.commit()
    
    return {"success": True, "message": "Funds released successfully"}

# Decoy: Proper authorization check on admin user listing
@app.get("/api/admin/users")
def admin_list_users(user: dict = Depends(get_current_user)):
    # Decoy: Proper check for ADMIN role
    if user.get("role") != "ADMIN":
        raise HTTPException(status_code=403, detail="Forbidden: Admin access required")

    cursor = db_conn.cursor()
    cursor.execute("SELECT id, username, role FROM users")
    rows = cursor.fetchall()
    return {"users": [dict(r) for r in rows]}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8098)
