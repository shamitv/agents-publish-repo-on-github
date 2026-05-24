import os
import sqlite3
from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = 'insurance_claims_secret_2026_xk9'

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
        role TEXT NOT NULL,
        full_name TEXT,
        email TEXT
    )''')

    cursor.execute('''
    CREATE TABLE policies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        policy_number TEXT NOT NULL UNIQUE,
        holder_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        premium REAL NOT NULL,
        coverage_amount REAL NOT NULL,
        status TEXT DEFAULT 'ACTIVE'
    )''')

    cursor.execute('''
    CREATE TABLE claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        claim_number TEXT NOT NULL UNIQUE,
        policy_id INTEGER NOT NULL,
        claimant_id INTEGER NOT NULL,
        description TEXT,
        amount_requested REAL NOT NULL,
        amount_approved REAL,
        status TEXT DEFAULT 'PENDING',
        adjuster_id INTEGER,
        filed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP
    )''')

    cursor.execute('''
    CREATE TABLE payouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        claim_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        method TEXT DEFAULT 'ACH',
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Seed users
    users_data = [
        ('john_doe', 'john_pass_123', 'CUSTOMER', 'John Doe', 'john@example.com'),
        ('jane_smith', 'jane_pass_456', 'CUSTOMER', 'Jane Smith', 'jane@example.com'),
        ('adj_williams', 'adj_pass_789', 'ADJUSTER', 'Mark Williams', 'mark@insurance.com'),
        ('admin', 'admin_claims_2026', 'ADMIN', 'System Admin', 'admin@insurance.com'),
    ]
    cursor.executemany(
        'INSERT INTO users (username, password_hash, role, full_name, email) VALUES (?, ?, ?, ?, ?)',
        users_data,
    )

    # Seed policies
    cursor.execute(
        "INSERT INTO policies (policy_number, holder_id, type, premium, coverage_amount) "
        "VALUES ('POL-2026-001', 1, 'AUTO', 180.00, 50000.00)"
    )
    cursor.execute(
        "INSERT INTO policies (policy_number, holder_id, type, premium, coverage_amount) "
        "VALUES ('POL-2026-002', 2, 'HOME', 320.00, 250000.00)"
    )
    cursor.execute(
        "INSERT INTO policies (policy_number, holder_id, type, premium, coverage_amount) "
        "VALUES ('POL-2026-003', 1, 'HEALTH', 450.00, 100000.00)"
    )

    # Seed claims
    cursor.execute(
        "INSERT INTO claims (claim_number, policy_id, claimant_id, description, amount_requested, status, adjuster_id) "
        "VALUES ('CLM-2026-001', 1, 1, 'Rear-end collision on Highway 101 — bumper and taillight damage', 4500.00, 'UNDER_REVIEW', 3)"
    )
    cursor.execute(
        "INSERT INTO claims (claim_number, policy_id, claimant_id, description, amount_requested, amount_approved, status, adjuster_id) "
        "VALUES ('CLM-2026-002', 2, 2, 'Storm damage to roof shingles and gutters', 12000.00, 9800.00, 'APPROVED', 3)"
    )

    # Seed payouts
    cursor.execute(
        "INSERT INTO payouts (claim_id, amount, method) VALUES (2, 9800.00, 'ACH')"
    )

    db_conn.commit()


init_db()


# --- AUTH APIs ---
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    # Decoy: Secure parameterized query for login
    cursor = db_conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username, password),
    )
    user = cursor.fetchone()

    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        return jsonify({
            'success': True,
            'user': {'username': user['username'], 'role': user['role']},
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


# --- POLICY APIs ---
@app.route('/api/policies', methods=['GET'])
def list_policies():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401

    cursor = db_conn.cursor()
    # Decoy: Properly scoped query — customers only see their own policies
    if session.get('role') == 'CUSTOMER':
        cursor.execute(
            "SELECT id, policy_number, type, premium, coverage_amount, status "
            "FROM policies WHERE holder_id = ?",
            (session['user_id'],),
        )
    else:
        cursor.execute(
            "SELECT p.id, p.policy_number, p.type, p.premium, p.coverage_amount, p.status, "
            "u.full_name as holder_name FROM policies p JOIN users u ON p.holder_id = u.id"
        )

    rows = cursor.fetchall()
    policies = [dict(r) for r in rows]
    return jsonify({'policies': policies})


# --- CLAIMS APIs ---
@app.route('/api/claims/search', methods=['GET'])
def search_claims():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401

    q = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()

    cursor = db_conn.cursor()

    if q:
        # VULNERABILITY A03: SQL Injection — User search input is concatenated directly
        # into a raw SQL WHERE clause without parameterization.
        # CHAIN LINK 1 (chain-01): SQLi reveals internal claim IDs and amounts
        query = (
            f"SELECT c.id, c.claim_number, c.description, c.amount_requested, c.status "
            f"FROM claims c WHERE c.description LIKE '%{q}%'"
        )
        if status_filter:
            query += f" AND c.status = '{status_filter}'"
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
        except Exception as e:
            return jsonify({'success': False, 'error': str(e), 'query_executed': query}), 400
    else:
        if session.get('role') == 'CUSTOMER':
            cursor.execute(
                "SELECT id, claim_number, description, amount_requested, status "
                "FROM claims WHERE claimant_id = ?",
                (session['user_id'],),
            )
        else:
            cursor.execute(
                "SELECT id, claim_number, description, amount_requested, status FROM claims"
            )
        rows = cursor.fetchall()

    claims = [dict(r) for r in rows]
    return jsonify({'claims': claims})


@app.route('/api/claims/<int:claim_id>', methods=['GET'])
def get_claim(claim_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401

    cursor = db_conn.cursor()
    # VULNERABILITY A01: IDOR — Any authenticated user can view any claim by ID,
    # including other customers' PII, payout amounts, and claim details.
    # No ownership check is performed between session user and claim's claimant_id.
    # CHAIN LINK 2 (chain-01): IDOR allows accessing and modifying any claim data
    cursor.execute(
        "SELECT c.id, c.claim_number, c.description, c.amount_requested, c.amount_approved, "
        "c.status, c.filed_at, c.resolved_at, u.full_name as claimant, u.email as claimant_email, "
        "p.policy_number, p.type as policy_type "
        "FROM claims c "
        "JOIN users u ON c.claimant_id = u.id "
        "JOIN policies p ON c.policy_id = p.id "
        "WHERE c.id = ?",
        (claim_id,),
    )
    row = cursor.fetchone()

    if not row:
        return jsonify({'message': 'Claim not found'}), 404

    return jsonify(dict(row))


@app.route('/api/claims', methods=['POST'])
def file_claim():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401

    data = request.get_json() or {}
    policy_id = data.get('policy_id')
    description = data.get('description', '')
    amount = float(data.get('amount_requested', 0))

    cursor = db_conn.cursor()
    claim_number = f"CLM-2026-{os.urandom(2).hex().upper()}"

    try:
        cursor.execute(
            "INSERT INTO claims (claim_number, policy_id, claimant_id, description, amount_requested) "
            "VALUES (?, ?, ?, ?, ?)",
            (claim_number, policy_id, session['user_id'], description, amount),
        )
        db_conn.commit()
        return jsonify({'success': True, 'claim_id': cursor.lastrowid, 'claim_number': claim_number})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/claims/<int:claim_id>/approve', methods=['POST'])
def approve_claim(claim_id):
    if 'user_id' not in session or session.get('role') not in ('ADJUSTER', 'ADMIN'):
        return jsonify({'message': 'Forbidden: Adjuster role required'}), 403

    data = request.get_json() or {}
    approved_amount = float(data.get('amount_approved', 0))

    cursor = db_conn.cursor()

    # VULNERABILITY A09: Security Logging & Monitoring Failures — High-value claim
    # approvals and payout dispatches produce no audit logs whatsoever. There is no
    # record of who approved what amount or when.
    # CHAIN LINK 3 (chain-01): Silent approval enables undetected payout fraud
    cursor.execute(
        "UPDATE claims SET status = 'APPROVED', amount_approved = ?, adjuster_id = ?, "
        "resolved_at = CURRENT_TIMESTAMP WHERE id = ?",
        (approved_amount, session['user_id'], claim_id),
    )

    # Auto-create payout record
    cursor.execute(
        "INSERT INTO payouts (claim_id, amount) VALUES (?, ?)",
        (claim_id, approved_amount),
    )
    db_conn.commit()

    return jsonify({'success': True, 'message': f'Claim {claim_id} approved for ${approved_amount:.2f}'})


# --- ADMIN APIs ---
@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    # Decoy: Proper authorization check — only ADMIN role can access stats
    if 'user_id' not in session or session.get('role') != 'ADMIN':
        return jsonify({'message': 'Forbidden: Admin role required'}), 403

    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*) as total_claims FROM claims")
    total_claims = cursor.fetchone()['total_claims']

    cursor.execute("SELECT SUM(amount) as total_payouts FROM payouts")
    total_payouts = cursor.fetchone()['total_payouts'] or 0

    cursor.execute("SELECT COUNT(*) as pending FROM claims WHERE status = 'PENDING'")
    pending = cursor.fetchone()['pending']

    return jsonify({
        'total_claims': total_claims,
        'total_payouts': total_payouts,
        'pending_claims': pending,
    })


@app.route('/api/admin/users', methods=['GET'])
def admin_list_users():
    if 'user_id' not in session or session.get('role') != 'ADMIN':
        return jsonify({'message': 'Forbidden'}), 403

    cursor = db_conn.cursor()
    cursor.execute("SELECT id, username, role, full_name, email FROM users")
    rows = cursor.fetchall()
    return jsonify({'users': [dict(r) for r in rows]})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8091, debug=True)
