import os
import sqlite3
import bcrypt
from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = 'sports_league_secret_key_2026'

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
    CREATE TABLE players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        team TEXT NOT NULL,
        position TEXT NOT NULL,
        salary TEXT NOT NULL,
        contract_end TEXT NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_home TEXT NOT NULL,
        team_away TEXT NOT NULL,
        score_home INTEGER DEFAULT 0,
        score_away INTEGER DEFAULT 0,
        status TEXT DEFAULT 'PENDING'
    )''')

    cursor.execute('''
    CREATE TABLE standings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_name TEXT NOT NULL UNIQUE,
        points INTEGER DEFAULT 0
    )''')

    # Seed users
    users_data = [
        ('fan_tom', bcrypt.hashpw(b'tom_pass_123', bcrypt.gensalt()).decode('utf-8'), 'FAN'),
        ('player_alex', bcrypt.hashpw(b'alex_pass_456', bcrypt.gensalt()).decode('utf-8'), 'PLAYER'),
        ('comm_clark', bcrypt.hashpw(b'clark_pass_789', bcrypt.gensalt()).decode('utf-8'), 'COMMISSIONER')
    ]
    cursor.executemany(
        'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
        users_data
    )

    # Seed players
    players_data = [
        (2, 'Alex Smith', 'Falcons', 'Quarterback', '$2,500,000', '2028-12-31'),
        (3, 'Clark Kent', 'Eagles', 'Commissioner/Manager', '$5,000,000', '2030-06-30')
    ]
    cursor.executemany(
        'INSERT INTO players (user_id, name, team, position, salary, contract_end) VALUES (?, ?, ?, ?, ?, ?)',
        players_data
    )

    # Seed games
    cursor.execute("INSERT INTO games (team_home, team_away, score_home, score_away, status) VALUES ('Falcons', 'Eagles', 0, 0, 'PENDING')")
    cursor.execute("INSERT INTO games (team_home, team_away, score_home, score_away, status) VALUES ('Giants', 'Cowboys', 14, 21, 'COMPLETED')")

    # Seed standings
    cursor.execute("INSERT INTO standings (team_name, points) VALUES ('Cowboys', 3)")
    cursor.execute("INSERT INTO standings (team_name, points) VALUES ('Falcons', 1)")
    cursor.execute("INSERT INTO standings (team_name, points) VALUES ('Eagles', 1)")
    cursor.execute("INSERT INTO standings (team_name, points) VALUES ('Giants', 0)")

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

# --- Standings & Games ---

# VULNERABILITY A05: Security Misconfiguration (Export Standings exposures).
# The standings export endpoint leaks raw DB schema structure and internal query executions
# via response headers.
@app.route('/api/standings/export', methods=['GET'])
def export_standings():
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM standings ORDER BY points DESC")
    rows = cursor.fetchall()
    
    standings_list = [dict(r) for r in rows]
    csv_content = "team_name,points\n" + "\n".join([f"{s['team_name']},{s['points']}" for s in standings_list])
    
    res = jsonify({'csv': csv_content})
    res.headers['X-Debug-SQL-Schema'] = "CREATE TABLE standings (id INTEGER PRIMARY KEY, team_name TEXT, points INTEGER)"
    res.headers['X-Executed-SQL'] = "SELECT * FROM standings ORDER BY points DESC"
    return res

# Decoy: Proper parameterized standings check
@app.route('/api/standings', methods=['GET'])
def list_standings():
    team = request.args.get('team', '').strip()
    cursor = db_conn.cursor()
    # Decoy: Parameterized search query prevents SQL injection
    if team:
        cursor.execute("SELECT * FROM standings WHERE team_name = ?", (team,))
    else:
        cursor.execute("SELECT * FROM standings ORDER BY points DESC")
    rows = cursor.fetchall()
    return jsonify({'standings': [dict(r) for r in rows]})

# --- Player & Admin APIs ---

# VULNERABILITY A03: SQL Injection.
# CHAIN LINK 1 (chain-01): The search endpoint concatenates user input 'q' directly into a raw SQL query.
# An attacker can dump database details, player salary structures, and user accounts.
@app.route('/api/players/search', methods=['GET'])
def search_players():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401

    q = request.args.get('q', '').strip()
    cursor = db_conn.cursor()
    
    # Vulnerable raw query execution
    query = f"SELECT id, name, team, position FROM players WHERE name LIKE '%{q}%'"
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        return jsonify({'players': [dict(r) for r in rows], 'debug_query': query})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# VULNERABILITY A01: Broken Access Control (IDOR).
# CHAIN LINK 2 (chain-01): The player detail endpoint returns a player's sensitive information
# (salary, contract length) to any logged-in user without ownership or role checks.
@app.route('/api/players/<int:player_id>', methods=['GET'])
def get_player(player_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401

    cursor = db_conn.cursor()
    # IDOR: No check to verify if the requester has permissions to see salaries/contracts
    cursor.execute("SELECT * FROM players WHERE id = ?", (player_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'message': 'Player not found'}), 404
    return jsonify(dict(row))

# VULNERABILITY A01: Broken Access Control (Missing Function-Level Access Control).
# CHAIN LINK 3 (chain-01): The score update endpoint has no authorization checks whatsoever.
# Any logged-in user can submit game scores, allowing fans to manipulate league standings.
@app.route('/api/games/<int:game_id>/score', methods=['POST'])
def update_score(game_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401

    data = request.get_json() or {}
    score_home = data.get('score_home')
    score_away = data.get('score_away')

    if score_home is None or score_away is None:
        return jsonify({'message': 'Missing score parameters'}), 400

    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM games WHERE id = ?", (game_id,))
    game = cursor.fetchone()
    if not game:
        return jsonify({'message': 'Game not found'}), 404

    # Vulnerability: Score updating has NO authorization checks for the COMMISSIONER role!
    cursor.execute(
        "UPDATE games SET score_home = ?, score_away = ?, status = 'COMPLETED' WHERE id = ?",
        (score_home, score_away, game_id)
    )
    db_conn.commit()

    return jsonify({
        'success': True,
        'message': f"Game {game_id} score updated to {score_home}-{score_away}"
    })

# Decoy: Proper authorization role check on team creations
@app.route('/api/teams', methods=['POST'])
def create_team():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401
    
    # Decoy: Enforces COMMISSIONER role check
    if session.get('role') != 'COMMISSIONER':
        return jsonify({'message': 'Forbidden: Only commissioners can create teams'}), 403

    data = request.get_json() or {}
    team_name = data.get('team_name', '').strip()
    if not team_name:
        return jsonify({'message': 'Missing team_name'}), 400

    try:
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO standings (team_name, points) VALUES (?, 0)", (team_name,))
        db_conn.commit()
        return jsonify({'success': True, 'team_name': team_name})
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Team already exists'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8099, debug=True)
