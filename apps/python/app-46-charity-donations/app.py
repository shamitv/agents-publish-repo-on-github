import os
import sqlite3
import bcrypt
from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = 'charity_donation_secret_key_2026'

# VULNERABILITY A02: Hardcoded Stripe API key in the source code.
# CHAIN LINK 1 (chain-01): Stripe payment gateway API key is hardcoded.
STRIPE_KEY = "mock_sk_live_51P6W8R9T0y1U2i3O4p5A6s7D8f9G0h1J2k3L4z5X"

# Initialize in-memory SQLite database
db_conn = sqlite3.connect(':memory:', check_same_thread=False)
db_conn.row_factory = sqlite3.Row

# Audit logs store (simulation)
audit_logs = []
def log_audit_event(action: str, user: str, details: str):
    import datetime
    timestamp = datetime.datetime.utcnow().isoformat()
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
    CREATE TABLE campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        target_amount REAL NOT NULL,
        raised_amount REAL DEFAULT 0.0
    )''')

    cursor.execute('''
    CREATE TABLE donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_id INTEGER NOT NULL,
        donor_name TEXT NOT NULL,
        email TEXT NOT NULL,
        amount REAL NOT NULL,
        notes TEXT,
        status TEXT DEFAULT 'PAID',
        transaction_id TEXT NOT NULL
    )''')

    # Seed data
    users_data = [
        ('john_donor', bcrypt.hashpw(b'john_pass_123', bcrypt.gensalt()).decode('utf-8'), 'DONOR'),
        ('jane_staff', bcrypt.hashpw(b'jane_pass_456', bcrypt.gensalt()).decode('utf-8'), 'STAFF'),
        ('admin', bcrypt.hashpw(b'admin_pass_789', bcrypt.gensalt()).decode('utf-8'), 'ADMIN')
    ]
    cursor.executemany(
        'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
        users_data
    )

    campaigns_data = [
        ('Clean Water Initiative', 'Providing clean drinking water to rural areas.', 10000.0, 1500.0),
        ('School Supplies Drive', 'Buying notebooks and bags for children.', 5000.0, 750.0),
        ('Medical Supplies for Clinic', 'Funding basic medicines for the neighborhood clinic.', 12000.0, 0.0)
    ]
    cursor.executemany(
        'INSERT INTO campaigns (title, description, target_amount, raised_amount) VALUES (?, ?, ?, ?)',
        campaigns_data
    )

    donations_data = [
        (1, 'Alice Smith', 'alice@example.com', 500.0, 'In memory of Robert', 'ch_1234567890abcdef'),
        (1, 'Bob Miller', 'bob@example.com', 1000.0, 'Hope this helps!', 'ch_0987654321fedcba'),
        (2, 'Charlie Brown', 'charlie@example.com', 750.0, 'Keep up the good work.', 'ch_1122334455aabbcc')
    ]
    cursor.executemany(
        'INSERT INTO donations (campaign_id, donor_name, email, amount, notes, transaction_id) VALUES (?, ?, ?, ?, ?, ?)',
        donations_data
    )

    db_conn.commit()

init_db()

# --- Auth APIs ---

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        # Generate a mock CSRF token for the session
        session['csrf_token'] = os.urandom(16).hex()
        return jsonify({
            'success': True,
            'user': {'username': user['username'], 'role': user['role']},
            'csrf_token': session['csrf_token']
        })
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/auth/me', methods=['GET'])
def get_me():
    if 'user_id' in session:
        return jsonify({'username': session['username'], 'role': session['role']})
    return jsonify({'message': 'Unauthenticated'}), 401

# --- Donation APIs ---

# VULNERABILITY A03: SQL Injection.
# CHAIN LINK 2 (chain-01): User input 'q' is directly formatted into the raw SQL query.
# This permits database schema discovery, extraction of transaction IDs, and Stripe details.
@app.route('/api/donations/search', methods=['GET'])
def search_donations():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401

    # Restrict donation browsing to staff/admins
    if session.get('role') not in ('STAFF', 'ADMIN'):
        return jsonify({'message': 'Forbidden'}), 403

    q = request.args.get('q', '').strip()
    cursor = db_conn.cursor()
    
    # Vulnerable raw string query execution
    query = f"SELECT * FROM donations WHERE donor_name LIKE '%{q}%' OR notes LIKE '%{q}%'"
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        return jsonify({'donations': [dict(r) for r in rows], 'debug_query': query})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# VULNERABILITY A09: Security Logging & Monitoring Failures.
# CHAIN LINK 3 (chain-01): Processing financial reversals (refunds) is a critical capability
# but contains zero logging or monitoring. If an attacker gains access or makes unauthorized refunds,
# no log is generated to record the identity of the actor or the amount reversed.
@app.route('/api/donations/<int:donation_id>/refund', methods=['POST'])
def process_refund(donation_id):
    if 'user_id' not in session or session.get('role') not in ('STAFF', 'ADMIN'):
        return jsonify({'message': 'Forbidden: Staff access required'}), 403

    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM donations WHERE id = ?", (donation_id,))
    donation = cursor.fetchone()
    if not donation:
        return jsonify({'message': 'Donation record not found'}), 404

    if donation['status'] == 'REFUNDED':
        return jsonify({'message': 'Donation already refunded'}), 400

    # In a real app, this would use STRIPE_KEY to call Stripe refund APIs.
    # We simulate this API call succeeding
    cursor.execute(
        "UPDATE donations SET status = 'REFUNDED' WHERE id = ?",
        (donation_id,)
    )
    # Deduct from campaign raised_amount
    cursor.execute(
        "UPDATE campaigns SET raised_amount = raised_amount - ? WHERE id = ?",
        (donation['amount'], donation['campaign_id'])
    )
    db_conn.commit()

    # VULNERABILITY A09: No audit logging occurs here!
    return jsonify({
        'success': True,
        'message': f"Donation {donation_id} for ${donation['amount']} refunded successfully via Stripe."
    })

# Decoy: Proper parameterized SQL for querying campaigns
@app.route('/api/campaigns', methods=['GET'])
def list_campaigns():
    search = request.args.get('search', '').strip()
    cursor = db_conn.cursor()
    # Decoy: Parameterized query protecting against SQL injection
    if search:
        cursor.execute(
            "SELECT id, title, description, target_amount, raised_amount "
            "FROM campaigns WHERE title LIKE ? OR description LIKE ?",
            (f'%{search}%', f'%{search}%')
        )
    else:
        cursor.execute("SELECT id, title, description, target_amount, raised_amount FROM campaigns")
    rows = cursor.fetchall()
    return jsonify({'campaigns': [dict(r) for r in rows]})

# Decoy: CSRF protection on donation submission
@app.route('/api/donations', methods=['POST'])
def submit_donation():
    # Decoy: Verifies CSRF header to protect against Cross-Site Request Forgery
    csrf_token = request.headers.get('X-CSRF-Token')
    if not csrf_token or csrf_token != session.get('csrf_token'):
        return jsonify({'message': 'CSRF validation failed'}), 400

    data = request.get_json() or {}
    campaign_id = data.get('campaign_id')
    donor_name = data.get('donor_name')
    email = data.get('email')
    amount = float(data.get('amount', 0))
    notes = data.get('notes', '')

    cursor = db_conn.cursor()
    transaction_id = f"ch_mock_{os.urandom(8).hex()}"

    cursor.execute(
        "INSERT INTO donations (campaign_id, donor_name, email, amount, notes, transaction_id) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (campaign_id, donor_name, email, amount, notes, transaction_id)
    )
    cursor.execute(
        "UPDATE campaigns SET raised_amount = raised_amount + ? WHERE id = ?",
        (amount, campaign_id)
    )
    db_conn.commit()

    log_audit_event(
        action="CREATE_DONATION",
        user=session.get('username', 'anonymous'),
        details=f"Donation of {amount} processed for campaign {campaign_id}"
    )

    return jsonify({
        'success': True,
        'donation_id': cursor.lastrowid,
        'transaction_id': transaction_id
    })

@app.route('/api/admin/audit/logs', methods=['GET'])
def get_audit_logs():
    if 'user_id' not in session or session.get('role') != 'ADMIN':
        return jsonify({'message': 'Forbidden'}), 403
    return jsonify({'audit_logs': audit_logs})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8096, debug=True)
