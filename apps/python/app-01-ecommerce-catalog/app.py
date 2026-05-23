import os
import sqlite3
from flask import Flask, request, jsonify, session, send_from_directory

app = Flask(__name__, static_folder='static')
app.secret_key = 'cyberpunk_secret_key_glow_neon_quantum_core'

# Initialize in-memory SQLite database
def get_db_connection():
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    return conn

# Global database connection for in-memory persistence during execution
db_conn = get_db_connection()

def init_db():
    cursor = db_conn.cursor()
    # Create tables
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    )''')
    
    cursor.execute('''
    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL
    )''')
    
    cursor.execute('''
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        order_number TEXT NOT NULL UNIQUE,
        total_amount REAL NOT NULL,
        status TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    cursor.execute('''
    CREATE TABLE order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL
    )''')
    
    # Seed Users (In a real system, passwords would be hashed; standard plaintext check for decoy simplicity or simple validation)
    users_data = [
        ('alice', 'alice123', 'CUSTOMER'),
        ('bob', 'bob123', 'CUSTOMER'),
        ('admin', 'admin123', 'ADMIN')
    ]
    cursor.executemany('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', users_data)
    
    # Seed Cyberpunk products
    products_data = [
        ('SKU-CB-001', 'Neural Uplink Core v4', 'Direct cortical connection unit. Enables high-speed quantum cyberspace navigation.', 'Hardware', 850.00, 25),
        ('SKU-CB-002', 'Holographic Cyber-Visor', 'Augmented reality HUD with thermal signatures, netrunner trace filters, and neon tint.', 'Wearables', 320.00, 40),
        ('SKU-CB-003', 'Subdermal Armor Plating', 'Military-grade synthetic alloy shields that fit neatly under organic skin layers.', 'Cyberware', 1250.00, 15),
        ('SKU-CB-004', 'Monofilament Laser-Whip', 'High-energy micro-filament line that slices through standard security gates.', 'Tactical', 450.00, 10),
        ('SKU-CB-005', 'Neon Mesh Trenchcoat', 'Stunning waterproof active-mesh outerwear with custom LED color wave modulators.', 'Apparel', 190.00, 50),
        ('SKU-CB-006', 'Decrypted Netrunner Deck', 'Pre-configured mainframe access terminal featuring custom payload exploit macros.', 'Hardware', 950.00, 8),
        ('SKU-CB-007', 'Glitch-Art Decal Sticker Pack', 'High-quality reflective vinyl sticker prints featuring corrupted hardware errors.', 'Apparel', 15.00, 100),
        ('SKU-CB-008', 'Portable Ice-Pick Exploit', 'Hardware-based decrypter capable of shattering sub-level commercial firewalls.', 'Tactical', 680.00, 12)
    ]
    cursor.executemany('INSERT INTO products (sku, name, description, category, price, quantity) VALUES (?, ?, ?, ?, ?, ?)', products_data)
    
    # Seed Orders for Alice and Bob
    cursor.execute("INSERT INTO orders (user_id, order_number, total_amount, status) VALUES (1, 'ORD-2026-001', 1170.00, 'DELIVERED')")
    cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (1, 1, 1, 850.00)")
    cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (1, 2, 1, 320.00)")

    cursor.execute("INSERT INTO orders (user_id, order_number, total_amount, status) VALUES (2, 'ORD-2026-002', 380.00, 'SHIPPED')")
    cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (2, 5, 2, 190.00)")

    cursor.execute("INSERT INTO orders (user_id, order_number, total_amount, status) VALUES (1, 'ORD-2026-003', 1250.00, 'PROCESSING')")
    cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (3, 3, 1, 1250.00)")

    db_conn.commit()

# Init db on start
init_db()

# --- HELPER ROUTE TO SERVE SPA ---
@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# --- AUTH PORTAL APIs ---
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    # Decoy: Secure, parameterized SQL query for login verification
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, password))
    user = cursor.fetchone()
    
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        return jsonify({
            'success': True,
            'user': {
                'username': user['username'],
                'role': user['role']
            }
        })
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

# CHAIN LINK 1 (chain-01): User enumeration endpoint.
# Returns 200 if a username exists, 404 if not — individually a low-severity
# information-disclosure issue, but enables the first step of the session-forge chain.
@app.route('/api/users/exists', methods=['GET'])
def user_exists():
    username = request.args.get('username', '').strip()
    cursor = db_conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    if row:
        return jsonify({'exists': True})
    return jsonify({'exists': False}), 404

@app.route('/api/auth/me', methods=['GET'])
def get_me():
    if 'user_id' in session:
        return jsonify({
            'username': session['username'],
            'role': session['role']
        })
    return jsonify({'message': 'Unauthenticated'}), 401

# --- PRODUCTS CATALOG APIs ---
@app.route('/api/products', methods=['GET'])
def list_products():
    q = request.args.get('q', '').strip()
    cursor = db_conn.cursor()
    
    if q:
        # VULNERABILITY A03: Raw SQL string concatenation mapping user-input parameters (SQL Injection target)
        query = f"SELECT id, sku, name, description, category, price, quantity FROM products WHERE name LIKE '%{q}%' OR description LIKE '%{q}%'"
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
        except Exception as e:
            # Verbose SQL error response helps tool benchmarking and validates A03 trigger success
            return jsonify({'success': False, 'error': str(e), 'query_executed': query}), 400
    else:
        cursor.execute("SELECT id, sku, name, description, category, price, quantity FROM products")
        rows = cursor.fetchall()
        query = "SELECT * FROM products"
        
    products = []
    for r in rows:
        products.append({
            'id': r['id'],
            'sku': r['sku'],
            'name': r['name'],
            'description': r['description'],
            'category': r['category'],
            'price': r['price'],
            'quantity': r['quantity']
        })
    return jsonify({'products': products, 'debug_query': query})

@app.route('/api/products', methods=['POST'])
def create_product():
    if 'user_id' not in session or session.get('role') != 'ADMIN':
        return jsonify({'message': 'Forbidden: Administrator role required'}), 403
        
    data = request.get_json() or {}
    sku = data.get('sku')
    name = data.get('name')
    description = data.get('description', '')
    category = data.get('category', 'General')
    price = float(data.get('price', 0.0))
    quantity = int(data.get('quantity', 0))
    
    cursor = db_conn.cursor()
    try:
        cursor.execute("INSERT INTO products (sku, name, description, category, price, quantity) VALUES (?, ?, ?, ?, ?, ?)",
                       (sku, name, description, category, price, quantity))
        db_conn.commit()
        return jsonify({'success': True, 'id': cursor.lastrowid})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# --- ORDERS APIs ---
@app.route('/api/orders', methods=['GET'])
def list_orders():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401
        
    cursor = db_conn.cursor()
    
    # Admin can view all orders, customers only see theirs
    if session.get('role') == 'ADMIN':
        cursor.execute("SELECT o.id, o.order_number, o.total_amount, o.status, o.created_at, u.username FROM orders o JOIN users u ON o.user_id = u.id")
    else:
        cursor.execute("SELECT id, order_number, total_amount, status, created_at, ? as username FROM orders WHERE user_id = ?", 
                       (session['username'], session['user_id']))
        
    rows = cursor.fetchall()
    orders = []
    for r in rows:
        orders.append({
            'id': r['id'],
            'order_number': r['order_number'],
            'total_amount': r['total_amount'],
            'status': r['status'],
            'created_at': r['created_at'],
            'username': r['username']
        })
    return jsonify(orders)

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order_details(order_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401
        
    cursor = db_conn.cursor()
    
    # VULNERABILITY A01: IDOR. Checks order details by ID directly without verifying owner user_id matches session['user_id']!
    cursor.execute("SELECT o.id, o.order_number, o.total_amount, o.status, o.created_at, u.username FROM orders o JOIN users u ON o.user_id = u.id WHERE o.id = ?", (order_id,))
    order = cursor.fetchone()
    
    if not order:
        return jsonify({'message': 'Order not found'}), 404
        
    cursor.execute("SELECT oi.quantity, oi.price, p.name, p.sku FROM order_items oi JOIN products p ON oi.product_id = p.id WHERE oi.order_id = ?", (order_id,))
    items_rows = cursor.fetchall()
    items = []
    for ir in items_rows:
        items.append({
            'name': ir['name'],
            'sku': ir['sku'],
            'quantity': ir['quantity'],
            'price': ir['price']
        })
        
    return jsonify({
        'id': order['id'],
        'order_number': order['order_number'],
        'total_amount': order['total_amount'],
        'status': order['status'],
        'created_at': order['created_at'],
        'username': order['username'],
        'items': items
    })

@app.route('/api/orders', methods=['POST'])
def create_order():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401
        
    data = request.get_json() or {}
    items = data.get('items', []) # expect list of dicts: {'product_id': X, 'quantity': Y}
    
    if not items:
        return jsonify({'message': 'Empty checkout cart'}), 400
        
    cursor = db_conn.cursor()
    
    try:
        # Calculate total
        total = 0.0
        validated_items = []
        for it in items:
            prod_id = it.get('product_id')
            qty = int(it.get('quantity', 1))
            
            cursor.execute("SELECT id, price, quantity, name FROM products WHERE id = ?", (prod_id,))
            prod = cursor.fetchone()
            if not prod:
                return jsonify({'message': f"Product ID {prod_id} not found"}), 400
            if prod['quantity'] < qty:
                return jsonify({'message': f"Insufficient stock for {prod['name']}"}), 400
                
            total += prod['price'] * qty
            validated_items.append((prod['id'], qty, prod['price']))
            
        # Create order record
        order_number = f"ORD-2026-{os.urandom(2).hex().upper()}"
        cursor.execute("INSERT INTO orders (user_id, order_number, total_amount, status) VALUES (?, ?, ?, 'PROCESSING')",
                       (session['user_id'], order_number, total))
        order_id = cursor.lastrowid
        
        # Save order items and reduce stock
        for pid, qty, price in validated_items:
            cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                           (order_id, pid, qty, price))
            cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (qty, pid))
            
        db_conn.commit()
        
        # VULNERABILITY A09: Severe Logging Failure.
        # Critical financial checkout and catalog stock deduction complete, but no auditable logs are written!
        # (Generic decoy prints might occur on connection setups, but nothing logs this action).
        
        return jsonify({'success': True, 'order_id': order_id, 'order_number': order_number})
    except Exception as e:
        db_conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Run server on port 8081
    app.run(host='0.0.0.0', port=8081, debug=True)
