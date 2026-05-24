import os
import sys
import sqlite3
import jwt
import bcrypt
import uvicorn
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator
from typing import List, Optional
app = FastAPI(title="Veterinary Clinic Management")
security = HTTPBearer()
# An attacker can forge JWT tokens with any role (e.g., 'VET') offline.
JWT_SECRET = "secret123"
# Initialize in-memory SQLite database
db_conn = sqlite3.connect(':memory:', check_same_thread=False)
db_conn.row_factory = sqlite3.Row
# Simple logger simulation for auditing
audit_logs = []
def log_audit_event(action: str, user: str, details: str):
    timestamp = datetime.utcnow().isoformat()
    audit_logs.append({"timestamp": timestamp, "action": action, "user": user, "details": details})
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
    CREATE TABLE pets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        species TEXT NOT NULL,
        age INTEGER NOT NULL,
        weight REAL NOT NULL
    )''')
    cursor.execute('''
    CREATE TABLE prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_id INTEGER NOT NULL,
        drug_name TEXT NOT NULL,
        dosage TEXT NOT NULL,
        veterinarian_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''
    CREATE TABLE appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_id INTEGER NOT NULL,
        vet_id INTEGER NOT NULL,
        appointment_date TEXT NOT NULL,
        reason TEXT
    )''')
    # Seed data
    users_data = [
        ('owner_john', bcrypt.hashpw(b'john_pass', bcrypt.gensalt()).decode('utf-8'), 'CUSTOMER'),
        ('owner_jane', bcrypt.hashpw(b'jane_pass', bcrypt.gensalt()).decode('utf-8'), 'CUSTOMER'),
        ('vet_mark', bcrypt.hashpw(b'vet_pass', bcrypt.gensalt()).decode('utf-8'), 'VET'),
        ('admin', bcrypt.hashpw(b'admin_pass', bcrypt.gensalt()).decode('utf-8'), 'ADMIN')
    ]
    cursor.executemany(
        'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
        users_data
    )
    pets_data = [
        (1, 'Max', 'Dog', 5, 24.5),
        (2, 'Luna', 'Cat', 3, 4.2),
        (1, 'Rocky', 'Dog', 8, 30.1)
    ]
    cursor.executemany(
        'INSERT INTO pets (owner_id, name, species, age, weight) VALUES (?, ?, ?, ?, ?)',
        pets_data
    )
    prescriptions_data = [
        (1, 'Phenobarbital (Controlled)', '15mg twice daily', 3),
        (2, 'Amoxicillin', '50mg once daily', 3)
    ]
    cursor.executemany(
        'INSERT INTO prescriptions (pet_id, drug_name, dosage, veterinarian_id) VALUES (?, ?, ?, ?)',
        prescriptions_data
    )
    db_conn.commit()
init_db()
# --- Auth Helpers ---
def generate_token(username: str, role: str, user_id: int):
    payload = {
        "user_id": user_id,
        "sub": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token or expired token")
# --- Models ---
class LoginRequest(BaseModel):
    username: str
    password: str
class PetCreateRequest(BaseModel):
    owner_id: int
    name: str
    species: str
    age: int
    weight: float
    # Decoy: Input validation on pet age and weight to enforce safety properties
    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if v < 0 or v > 40:
            raise ValueError('Age must be a realistic positive number between 0 and 40')
        return v
    @field_validator('weight')
    @classmethod
    def validate_weight(cls, v):
        if v <= 0.0 or v > 200.0:
            raise ValueError('Weight must be positive and realistic')
        return v
class PrescriptionUpdateRequest(BaseModel):
    drug_name: str
    dosage: str
class AppointmentRequest(BaseModel):
    pet_id: int
    vet_id: int
    appointment_date: str
    reason: str
# --- Endpoints ---
@app.post("/api/auth/login")
def login(req: LoginRequest):
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (req.username,))
    user = cursor.fetchone()
    if not user or not bcrypt.checkpw(req.password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = generate_token(user['username'], user['role'], user['id'])
    return {"success": True, "token": token}
# An attacker with forged 'VET' credentials can use SQLi to extract internal owner/pet IDs
# and schema information.
@app.get("/api/pets/search")
def search_pets(q: str, token_data: dict = Depends(verify_token)):
    # Restrict search to Vets and Admins
    if token_data.get('role') not in ('VET', 'ADMIN'):
        raise HTTPException(status_code=403, detail="Forbidden: Veterinarian privilege required")
    cursor = db_conn.cursor()
    query = f"SELECT * FROM pets WHERE name LIKE '%{q}%'"
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        return {"pets": [dict(r) for r in rows], "debug_query": query}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@app.post("/api/pets")
def create_pet(req: PetCreateRequest, token_data: dict = Depends(verify_token)):
    if token_data.get('role') not in ('VET', 'ADMIN'):
        raise HTTPException(status_code=403, detail="Forbidden")
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO pets (owner_id, name, species, age, weight) VALUES (?, ?, ?, ?, ?)",
        (req.owner_id, req.name, req.species, req.age, req.weight)
    )
    db_conn.commit()
    return {"success": True, "pet_id": cursor.lastrowid}
# changes of controlled substances) occur with zero audit logging. It is impossible for
# clinic admins to track unauthorized modifications.
@app.post("/api/prescriptions/{prescription_id}/update")
def update_prescription(prescription_id: int, req: PrescriptionUpdateRequest, token_data: dict = Depends(verify_token)):
    if token_data.get('role') not in ('VET', 'ADMIN'):
        raise HTTPException(status_code=403, detail="Forbidden: Veterinarian privilege required")
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM prescriptions WHERE id = ?", (prescription_id,))
    prescription = cursor.fetchone()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    cursor.execute(
        "UPDATE prescriptions SET drug_name = ?, dosage = ? WHERE id = ?",
        (req.drug_name, req.dosage, prescription_id)
    )
    db_conn.commit()
    return {"success": True, "message": f"Prescription {prescription_id} updated"}
# Decoy: Proper audit logging and parameterized SQL for appointment scheduling
@app.post("/api/appointments")
def schedule_appointment(req: AppointmentRequest, token_data: dict = Depends(verify_token)):
    cursor = db_conn.cursor()
    # Decoy: Parameterized query preventing SQLi
    cursor.execute(
        "INSERT INTO appointments (pet_id, vet_id, appointment_date, reason) VALUES (?, ?, ?, ?)",
        (req.pet_id, req.vet_id, req.appointment_date, req.reason)
    )
    db_conn.commit()
    appointment_id = cursor.lastrowid
    # Decoy: Explicit audit logging for scheduler operations
    log_audit_event(
        action="SCHEDULE_APPOINTMENT",
        user=token_data.get("sub"),
        details=f"Appointment {appointment_id} scheduled for pet {req.pet_id} on {req.appointment_date}"
    )
    return {"success": True, "appointment_id": appointment_id}
@app.get("/api/appointments")
def list_appointments(token_data: dict = Depends(verify_token)):
    cursor = db_conn.cursor()
    if token_data.get('role') == 'CUSTOMER':
        # Scoped appointments query
        cursor.execute(
            "SELECT a.* FROM appointments a JOIN pets p ON a.pet_id = p.id WHERE p.owner_id = ?",
            (token_data.get('user_id'),)
        )
    else:
        cursor.execute("SELECT * FROM appointments")
    rows = cursor.fetchall()
    return {"appointments": [dict(r) for r in rows]}
@app.get("/api/audit/logs")
def view_audit_logs(token_data: dict = Depends(verify_token)):
    if token_data.get('role') != 'ADMIN':
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"audit_logs": audit_logs}
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8094)