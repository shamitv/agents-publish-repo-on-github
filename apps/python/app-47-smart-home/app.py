import os
import sqlite3
import requests
import bcrypt
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Smart Home Device Manager")

# Initialize in-memory SQLite database
db_conn = sqlite3.connect(':memory:', check_same_thread=False)
db_conn.row_factory = sqlite3.Row

# Mock rate limiting store for decoy
rate_limit_store = {}

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
    CREATE TABLE devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_name TEXT NOT NULL,
        device_type TEXT NOT NULL,
        api_token TEXT NOT NULL,
        status TEXT DEFAULT 'ONLINE',
        firmware_version TEXT DEFAULT 'v1.0.0'
    )''')

    # Seed users
    users_data = [
        ('owner_alice', bcrypt.hashpw(b'alice_home_2026', bcrypt.gensalt()).decode('utf-8'), 'USER'),
        ('admin', bcrypt.hashpw(b'admin_home_2026', bcrypt.gensalt()).decode('utf-8'), 'ADMIN')
    ]
    cursor.executemany(
        'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
        users_data
    )

    # Seed devices
    devices_data = [
        ('Living Room Thermostat', 'THERMOSTAT', 'tok_thermostat_9982x'),
        ('Smart Lock Front Door', 'LOCK', 'tok_lock_1102z'),
        ('Garage Door Opener', 'GARAGE', 'tok_garage_4431a')
    ]
    cursor.executemany(
        'INSERT INTO devices (device_name, device_type, api_token) VALUES (?, ?, ?)',
        devices_data
    )

    db_conn.commit()

init_db()

# --- Auth Helper ---
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

class FirmwareUpdateRequest(BaseModel):
    firmware_url: str

class CommandRequest(BaseModel):
    command: str

# --- Endpoints ---

@app.post("/api/auth/login")
def login(req: LoginRequest, response: Request):
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (req.username,))
    user = cursor.fetchone()
    if not user or not bcrypt.checkpw(req.password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    session_id = os.urandom(16).hex()
    sessions[session_id] = {"id": user["id"], "username": user["username"], "role": user["role"]}
    
    # Secure session response (we can just return it in JSON)
    from fastapi.responses import JSONResponse
    res = JSONResponse(content={"success": True, "user": {"username": user["username"], "role": user["role"]}})
    res.set_cookie("session_id", session_id, httponly=True)
    return res

@app.post("/api/auth/logout")
def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id in sessions:
        del sessions[session_id]
    return {"success": True}

# VULNERABILITY A05: Security Misconfiguration (Debug endpoint exposure).
# CHAIN LINK 1 (chain-01): The unauthenticated debug endpoint leaks all registered smart devices
# along with their private device API tokens, exposing them to unauthorized device access.
@app.get("/api/debug/devices")
def debug_devices():
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM devices")
    rows = cursor.fetchall()
    return {"devices": [dict(r) for r in rows]}

# VULNERABILITY A10: Server-Side Request Forgery (SSRF).
# CHAIN LINK 2 (chain-01): Sensor data proxy endpoint fetches arbitrary user-supplied URLs from the
# internal network without validation. An attacker can scan internal networks by specifying local IP ranges.
@app.get("/api/devices/sensor-data")
def fetch_sensor_data(url: str, user: dict = Depends(get_current_user)):
    try:
        # SSRF: Fetches any user-provided URL without validation
        resp = requests.get(url, timeout=5)
        return {"success": True, "content": resp.text[:2000]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# VULNERABILITY A08: Software and Data Integrity Failures (Unsigned Firmware Update).
# CHAIN LINK 3 (chain-01): Firmware update accepts arbitrary URLs, downloads the binary payload,
# and executes/updates it without verifying checksums, digital signatures, or origins.
@app.post("/api/devices/{device_id}/firmware/update")
def update_firmware(device_id: int, req: FirmwareUpdateRequest, user: dict = Depends(get_current_user)):
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
    device = cursor.fetchone()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    try:
        # Fetches the remote binary (vulnerable to SSRF as well, but primarily integrity fail)
        resp = requests.get(req.firmware_url, timeout=10)
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch firmware binary")
        
        # Simulates updating the firmware binary without checking integrity (signature, hash)
        binary_size = len(resp.content)
        new_version = f"v1.1.{binary_size % 100}"
        
        cursor.execute(
            "UPDATE devices SET firmware_version = ? WHERE id = ?",
            (new_version, device_id)
        )
        db_conn.commit()
        return {
            "success": True,
            "message": f"Device {device_id} updated to version {new_version} successfully (applied {binary_size} bytes)."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Decoy: Proper device API token validation checking device authority before accepting commands
@app.post("/api/devices/{device_id}/command")
def send_device_command(device_id: int, req: CommandRequest, request: Request, user: dict = Depends(get_current_user)):
    auth_header = request.headers.get("X-Device-Token")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing X-Device-Token header")

    cursor = db_conn.cursor()
    # Decoy: Validates the token matches the registered token of the target device
    cursor.execute("SELECT * FROM devices WHERE id = ? AND api_token = ?", (device_id, auth_header))
    device = cursor.fetchone()
    if not device:
        raise HTTPException(status_code=403, detail="Invalid token for this device")

    return {
        "success": True,
        "message": f"Command '{req.command}' successfully dispatched to device {device['device_name']}"
    }

# Decoy: Rate-limited status polling to prevent denial of service
@app.get("/api/devices/{device_id}/status")
def get_device_status(device_id: int, user: dict = Depends(get_current_user)):
    import time
    username = user['username']
    now = time.time()
    
    # Decoy: Rate limiting check (cooldown timer of 1 second per user)
    if username in rate_limit_store:
        last_request_time = rate_limit_store[username]
        if now - last_request_time < 1.0:
            raise HTTPException(status_code=429, detail="Too many requests. Please wait before polling status.")
            
    rate_limit_store[username] = now

    cursor = db_conn.cursor()
    cursor.execute("SELECT id, device_name, device_type, status, firmware_version FROM devices WHERE id = ?", (device_id,))
    device = cursor.fetchone()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return dict(device)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8097)
