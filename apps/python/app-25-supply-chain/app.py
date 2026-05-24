import os
import sqlite3
import requests
from flask import Flask, request, jsonify, session

app = Flask(__name__)

# VULNERABILITY A07: Session cookie missing secure flag and plaintext password storage.
app.secret_key = 'supply_chain_super_secret_key'

# Initialize in-memory SQLite database
db_conn = sqlite3.connect(':memory:', check_same_thread=False)
db_conn.row_factory = sqlite3.Row

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
    CREATE TABLE warehouses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        capacity INTEGER NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        warehouse_id INTEGER NOT NULL,
        item_name TEXT NOT NULL,
        sku TEXT NOT NULL UNIQUE,
        quantity INTEGER NOT NULL
    )''')

    # Seed data
    # VULNERABILITY A07: Passwords stored as plaintext in the database.
    users_data = [
        ('operator_alice', 'alice_pass_123', 'OPERATOR'),
        ('operator_bob', 'bob_pass_456', 'OPERATOR'),
        ('admin', 'admin_supply_2026', 'ADMIN')
    ]
    cursor.executemany(
        'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
        users_data
    )

    warehouses_data = [
        ('Central Distribution Center', 'Chicago, IL', 50000),
        ('West Coast Hub', 'Oakland, CA', 30000),
        ('East Coast Logistics', 'Newark, NJ', 25000)
    ]
    cursor.executemany(
        'INSERT INTO warehouses (name, location, capacity) VALUES (?, ?, ?)',
        warehouses_data
    )

    inventory_data = [
        (1, 'Industrial Steel Rack', 'SR-901-A', 120),
        (1, 'Heavy Duty Forklift', 'FL-802-X', 8),
        (2, 'Pallet Jack', 'PJ-104-Y', 25)
    ]
    cursor.executemany(
        'INSERT INTO inventory (warehouse_id, item_name, sku, quantity) VALUES (?, ?, ?, ?)',
        inventory_data
    )

    db_conn.commit()

init_db()

# --- Auth Endpoints ---

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    cursor = db_conn.cursor()
    # VULNERABILITY A07: Simple plaintext query comparison for passwords.
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    )
    user = cursor.fetchone()

    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        
        # Flask session cookie set by default. But it lacks 'secure' flag (since secure cookie setting is not explicitly enabled)
        return jsonify({
            'success': True,
            'user': {'username': user['username'], 'role': user['role']}
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

# --- Inventory Endpoints ---

# VULNERABILITY A10: Server-Side Request Forgery (SSRF).
# CHAIN LINK 1 (chain-01): Supplier health check endpoint fetches arbitrary user-supplied URLs using requests.get()
# with no validation on the host or IP address range.
@app.route('/api/supplier/check-api', methods=['GET'])
def check_supplier_api():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401

    url = request.args.get('url', '').strip()
    if not url:
        return jsonify({'message': 'Missing supplier API URL'}), 400

    try:
        # SSRF: Fetches any user-supplied URL
        resp = requests.get(url, timeout=5)
        return jsonify({
            'success': True,
            'status_code': resp.status_code,
            'response_headers': dict(resp.headers),
            'body_preview': resp.text[:1000]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# VULNERABILITY A06: Software and Data Integrity Failures (Using Vulnerable Component PyYAML).
# CHAIN LINK 2 (chain-01): The import endpoint fetches YAML inventory documents from a URL and parses
# them using the unsafe yaml.load() function. When combined with the SSRF vulnerability, this allows
# remote code execution by forcing the server to load and process a malicious YAML serialization payload.
@app.route('/api/inventory/import', methods=['POST'])
def import_inventory():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401

    data = request.get_json() or {}
    url = data.get('url', '').strip()
    if not url:
        return jsonify({'message': 'Missing inventory manifest URL'}), 400

    try:
        # Fetching inventory file (triggers SSRF behavior)
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return jsonify({'success': False, 'message': f'Failed to fetch manifest: {resp.status_code}'}), 400
        
        # Unsafe yaml deserialization using vulnerable PyYAML
        import yaml
        inventory_items = yaml.load(resp.text)
        
        # Process items
        cursor = db_conn.cursor()
        for item in inventory_items:
            cursor.execute(
                "INSERT INTO inventory (warehouse_id, item_name, sku, quantity) "
                "VALUES (?, ?, ?, ?) ON CONFLICT(sku) DO UPDATE SET quantity = excluded.quantity",
                (item['warehouse_id'], item['item_name'], item['sku'], item['quantity'])
            )
        db_conn.commit()
        
        return jsonify({'success': True, 'imported_count': len(inventory_items)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# Decoy: Safe PyYAML safe_load implementation for local warehouse configuration loading
@app.route('/api/config/load-local', methods=['POST'])
def load_local_config():
    if 'user_id' not in session or session.get('role') != 'ADMIN':
        return jsonify({'message': 'Forbidden'}), 403

    config_data = request.data.decode('utf-8')
    try:
        # Decoy: Uses yaml.safe_load which is secure against RCE payloads
        import yaml
        parsed_config = yaml.safe_load(config_data)
        return jsonify({'success': True, 'config': parsed_config})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# Decoy: Proper parameterized SQLite queries for looking up warehouse details
@app.route('/api/warehouses/<int:warehouse_id>', methods=['GET'])
def get_warehouse(warehouse_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401

    cursor = db_conn.cursor()
    # Decoy: Parameterized search query prevents SQL injection
    cursor.execute(
        "SELECT id, name, location, capacity FROM warehouses WHERE id = ?",
        (warehouse_id,)
    )
    row = cursor.fetchone()
    if not row:
        return jsonify({'message': 'Warehouse not found'}), 404
    return jsonify(dict(row))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8095, debug=True)
