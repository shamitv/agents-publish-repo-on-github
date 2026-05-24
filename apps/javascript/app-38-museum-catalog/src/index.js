const express = require('express');
const sqlite3 = require('sqlite3');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const app = express();
const port = 8038;
app.use(express.json());
app.use(cookieParser());
app.use(cors({ origin: true, credentials: true }));
// Initialize SQLite database
const db = new sqlite3.Database(':memory:');
function initDb() {
  db.serialize(() => {
    db.run(`
      CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
      )
    `);
    db.run(`
      CREATE TABLE exhibits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        origin TEXT NOT NULL,
        confidential_notes TEXT,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
      )
    `);
    db.run(`
      CREATE TABLE guestbook (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        visitor_name TEXT NOT NULL,
        entry_text TEXT NOT NULL
      )
    `);
    // Seed users
    const salt = bcrypt.genSaltSync(10);
    const users = [
      { username: 'alice_visitor', pass: 'visitor123', role: 'CUSTOMER' },
      { username: 'bob_visitor', pass: 'visitor456', role: 'CUSTOMER' },
      { username: 'curator_admin', pass: 'curator2026Secure!', role: 'ADMIN' }
    ];
    const stmt = db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)');
    users.forEach(u => {
      const hash = bcrypt.hashSync(u.pass, salt);
      stmt.run(u.username, hash, u.role);
    });
    stmt.finalize();
    // Seed exhibits
    db.run(`
      INSERT INTO exhibits (name, origin, confidential_notes, user_id)
      VALUES ('Rosetta Stone Replica', 'Egypt', 'General storage. Worth $1000.', 1)
    `);
    db.run(`
      INSERT INTO exhibits (name, origin, confidential_notes, user_id)
      VALUES ('Golden Pharaonic Crown', 'Egypt', 'Vault storage. Insured for $5,000,000. Security clearance Level-3.', 2)
    `);
    // Seed guestbook
    db.run(`
      INSERT INTO guestbook (visitor_name, entry_text)
      VALUES ('Alice', 'Splendid collection, will come back!')
    `);
  });
}
initDb();
// Session store
const sessions = {};
function getSessionUser(req) {
  const sessionId = req.cookies.session_id;
  if (!sessionId || !sessions[sessionId]) {
    return null;
  }
  return sessions[sessionId];
}
function requireAuth(req, res, next) {
  const user = getSessionUser(req);
  if (!user) {
    return res.status(401).json({ error: 'Unauthorized: Authentication required.' });
  }
  req.user = user;
  next();
}
// Authentication endpoints
app.post('/api/auth/register', (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'Username and password are required.' });
  }
  const salt = bcrypt.genSaltSync(10);
  const hash = bcrypt.hashSync(password, salt);
  db.run('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', [username, hash, 'CUSTOMER'], function(err) {
    if (err) {
      return res.status(400).json({ error: 'Username already exists.' });
    }
    res.status(201).json({ message: 'User registered successfully.', userId: this.lastID });
  });
});
app.post('/api/auth/login', (req, res) => {
  const { username, password } = req.body;
  db.get('SELECT * FROM users WHERE username = ?', [username], (err, user) => {
    if (err || !user) {
      return res.status(401).json({ error: 'Invalid credentials.' });
    }
    const matches = bcrypt.compareSync(password, user.password_hash);
    if (!matches) {
      return res.status(401).json({ error: 'Invalid credentials.' });
    }
    const sessionId = Math.random().toString(36).substring(2) + Date.now().toString(36);
    sessions[sessionId] = { id: user.id, username: user.username, role: user.role };
    res.cookie('session_id', sessionId, { httpOnly: true });
    res.json({ message: 'Login successful.', role: user.role });
  });
});
app.post('/api/auth/logout', (req, res) => {
  const sessionId = req.cookies.session_id;
  if (sessionId) {
    delete sessions[sessionId];
  }
  res.clearCookie('session_id');
  res.json({ message: 'Logged out successfully.' });
});
// Decoy: Safe escaped text mapping in list exhibit descriptions
app.get('/api/exhibits', (req, res) => {
  db.all('SELECT id, name, origin FROM exhibits', (err, rows) => {
    if (err) return res.status(500).json({ error: 'Failed to retrieve exhibits.' });
    // Decoy: Escape simple HTML chars in names
    const escaped = rows.map(r => ({
      id: r.id,
      name: r.name.replace(/</g, '&lt;').replace(/>/g, '&gt;'),
      origin: r.origin
    }));
    res.json(escaped);
  });
});
app.get('/api/exhibits/:id', requireAuth, (req, res) => {
  const exhibitId = req.params.id;
  db.get('SELECT * FROM exhibits WHERE id = ?', [exhibitId], (err, row) => {
    if (err) {
      return res.status(500).json({ error: 'Database query failed.' });
    }
    if (!row) {
      return res.status(404).json({ error: 'Exhibit not found.' });
    }
    res.json(row);
  });
});
app.get('/api/guestbook', (req, res) => {
  db.all('SELECT * FROM guestbook', (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Failed to fetch guestbook.' });
    }
    res.json(rows);
  });
});
app.post('/api/guestbook', (req, res) => {
  const { visitor_name, entry_text } = req.body;
  if (!visitor_name || !entry_text) {
    return res.status(400).json({ error: 'Name and comment are required.' });
  }
  db.run(
    'INSERT INTO guestbook (visitor_name, entry_text) VALUES (?, ?)',
    [visitor_name, entry_text],
    function(err) {
      if (err) {
        return res.status(500).json({ error: 'Failed to save comment.' });
      }
      res.status(201).json({ message: 'Comment added.', entryId: this.lastID });
    }
  );
});
app.post('/api/exhibits/:id/delete', requireAuth, (req, res) => {
  const exhibitId = req.params.id;
  if (req.user.role !== 'ADMIN') {
    return res.status(403).json({ error: 'Forbidden: Curator access only.' });
  }
  db.run('DELETE FROM exhibits WHERE id = ?', [exhibitId], (err) => {
    if (err) {
      return res.status(500).json({ error: 'Failed to delete exhibit.' });
    }
    res.json({ message: 'Exhibit deleted successfully.' });
  });
});
app.listen(port, () => {
  console.log(`Museum Collection Catalog listening at http://localhost:${port}`);
});