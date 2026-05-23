import os
import sqlite3
import subprocess
import requests
from flask import Flask, request, jsonify, session, send_from_directory

app = Flask(__name__, static_folder='static')

# --- OWASP VULNERABILITY A05: Security Misconfiguration ---
# Uses a default insecure widely known secret key, and runs in Debug=True
app.config['SECRET_KEY'] = 'dev'

def get_db_connection():
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    return conn

db_conn = get_db_connection()

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
    CREATE TABLE properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        location TEXT NOT NULL,
        description TEXT,
        image_url TEXT
    )''')
    
    cursor.execute('''
    CREATE TABLE messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_id INTEGER NOT NULL,
        client_name TEXT NOT NULL,
        client_phone TEXT,
        message_content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Seed Accounts
    users_data = [
        ('alice', 'alice123', 'BUYER'),
        ('bob', 'bob123', 'BUYER'),
        ('agent_smith', 'agent123', 'AGENT')
    ]
    cursor.executemany('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', users_data)
    
    # Seed Real Estate listings
    properties_data = [
        ('Sovereign Sunset Penthouse', 'Apartment', 1450000.00, 'Skyline Sector B', 'Exclusive panoramic penthouse featuring active light-emitting structural frames and custom biometric security access locks.', '/static/img/prop1.jpg'),
        ('Neo-Metropolis Warehouse Loft', 'Loft', 890000.00, 'Industrial Sector 9', 'Authentic brick warehouse conversion with high-density fiber connectivity, steel trusses, and modular layout zones.', '/static/img/prop2.jpg'),
        ('Vapor-Wave Lakeside Cabin', 'House', 420000.00, 'Cyber Reserve Forest', 'Secluded sustainable forest cabin featuring integrated solar grids and holographic smart-glass windows.', '/static/img/prop3.jpg'),
        ('Holographic High-Rise Studio', 'Studio', 350000.00, 'Neon Core Central', 'Perfect compact netrunner studio equipped with dynamic active insulation and smart home voice routines.', '/static/img/prop4.jpg')
    ]
    cursor.executemany('INSERT INTO properties (title, category, price, location, description, image_url) VALUES (?, ?, ?, ?, ?, ?)', properties_data)
    
    # Seed Initial Messages
    cursor.execute("INSERT INTO messages (property_id, client_name, client_phone, message_content) VALUES (1, 'Alice Vance', '555-0192', 'Is the dynamic light-grid frame system customizable via standard net API controls?')")
    
    db_conn.commit()

init_db()

# --- HELPER ROUTE TO SERVE SPA ---
@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# --- AUTH APIs ---
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    cursor = db_conn.cursor()
    # Decoy: Secure parameterized query check
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
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

@app.route('/api/auth/me', methods=['GET'])
def get_me():
    if 'user_id' in session:
        return jsonify({
            'username': session['username'],
            'role': session['role']
        })
    return jsonify({'message': 'Unauthenticated'}), 401

# --- PROPERTIES LISTING APIs ---
@app.route('/api/properties', methods=['GET'])
def list_properties():
    cursor = db_conn.cursor()
    # Decoy: parameterized lookup based on price thresholds
    min_price = float(request.args.get('min_price', 0.0))
    cursor.execute("SELECT * FROM properties WHERE price >= ?", (min_price,))
    rows = cursor.fetchall()
    
    props = []
    for r in rows:
        props.append({
            'id': r['id'],
            'title': r['title'],
            'category': r['category'],
            'price': r['price'],
            'location': r['location'],
            'description': r['description'],
            'image_url': r['image_url']
        })
    return jsonify(props)

@app.route('/api/properties', methods=['POST'])
def create_property():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401
        
    data = request.get_json() or {}
    title = data.get('title')
    category = data.get('category')
    price = float(data.get('price', 0.0))
    location = data.get('location')
    description = data.get('description', '')
    image_url = data.get('image_url', '/static/img/default.jpg')
    
    cursor = db_conn.cursor()
    try:
        cursor.execute("INSERT INTO properties (title, category, price, location, description, image_url) VALUES (?, ?, ?, ?, ?, ?)",
                       (title, category, price, location, description, image_url))
        db_conn.commit()
        return jsonify({'success': True, 'id': cursor.lastrowid})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# --- OWASP VULNERABILITY A03: OS Command Injection via Subprocess shell=True ---
@app.route('/api/properties/analyze', methods=['POST'])
def analyze_listing():
    data = request.get_json() or {}
    # User-controlled parameter passed straight to the command line shell execution!
    filename = data.get('filename', 'default_desc.txt')
    
    # Subprocess execution mapping raw parameters inside string formats
    cmd = f"echo 'Metadata inspection for property description filename: {filename}'"
    try:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        output_log = stdout.decode('utf-8', errors='ignore') + stderr.decode('utf-8', errors='ignore')
        return jsonify({
            'success': True,
            'cmd_executed': cmd,
            'output': output_log
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# --- OWASP VULNERABILITY A10: Server-Side Request Forgery (SSRF) ---
@app.route('/api/properties/import-image', methods=['POST'])
def import_external_image():
    data = request.get_json() or {}
    # User provides URL of a layout layout or JPEG photo to load
    target_url = data.get('url', '').strip()
    
    if not target_url:
        return jsonify({'message': 'Remote URL input target required'}), 400
        
    try:
        # SSRF: Fetches remote asset bytes using standard request library without IP restrictions,
        # hostname validation, or DNS sandboxing. Permits probing localhost/private subnet nodes.
        res = requests.get(target_url, timeout=4)
        
        # Save a mock layout thumbnail name or confirm connection status
        return jsonify({
            'success': True,
            'bytes_fetched': len(res.content),
            'content_type': res.headers.get('Content-Type'),
            'status_code': res.status_code
        })
    except Exception as ex:
        # Returns clear exception tracebacks aiding agent SSRF discovery validations
        return jsonify({'success': False, 'error': str(ex)}), 400

# --- AGENT COMMUNICATIONS APIs ---
# CHAIN LINK 1 (chain-01): Debug environment introspection endpoint left active in production.
# Individually this is a low-impact misconfiguration, but it reveals internal file paths,
# service URLs, and environment variables that make the SSRF and command-injection steps
# far more precise and reliable.
@app.route('/api/debug/env', methods=['GET'])
def debug_env():
    env_dump = {k: v for k, v in os.environ.items()}
    return jsonify({'env': env_dump, 'cwd': os.getcwd()})

@app.route('/api/messages', methods=['POST'])
def create_message():
    data = request.get_json() or {}
    property_id = int(data.get('property_id'))
    name = data.get('client_name')
    phone = data.get('client_phone', '')
    content = data.get('message_content')
    
    cursor = db_conn.cursor()
    try:
        cursor.execute("INSERT INTO messages (property_id, client_name, client_phone, message_content) VALUES (?, ?, ?, ?)",
                       (property_id, name, phone, content))
        db_conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/messages', methods=['GET'])
def list_messages():
    if 'user_id' not in session or session.get('role') != 'AGENT':
        return jsonify({'message': 'Forbidden: Agent role signature required'}), 403
        
    cursor = db_conn.cursor()
    cursor.execute("SELECT m.id, m.client_name, m.client_phone, m.message_content, m.created_at, p.title FROM messages m JOIN properties p ON m.property_id = p.id")
    rows = cursor.fetchall()
    
    msgs = []
    for r in rows:
        msgs.append({
            'id': r['id'],
            'client_name': r['client_name'],
            'client_phone': r['client_phone'],
            'message_content': r['message_content'],
            'created_at': r['created_at'],
            'property_title': r['title']
        })
    return jsonify(msgs)

if __name__ == '__main__':
    # Run application on port 8084
    # Flag debug=True enables remote execution debuggers!
    app.run(host='0.0.0.0', port=8084, debug=True)
