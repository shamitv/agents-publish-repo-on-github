const express = require('express');
const sqlite3 = require('sqlite3');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const app = express();
const port = 8042;
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
      CREATE TABLE contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT NOT NULL,
        amount REAL NOT NULL,
        details TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
      )
    `);
    // Seed users
    const salt = bcrypt.genSaltSync(10);
    const users = [
      { username: 'alice_manager', pass: 'manager123', role: 'CUSTOMER' },
      { username: 'bob_manager', pass: 'manager456', role: 'CUSTOMER' },
      { username: 'admin_inspector', pass: 'inspector2026Secure!', role: 'ADMIN' }
    ];
    const stmt = db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)');
    users.forEach(u => {
      const hash = bcrypt.hashSync(u.pass, salt);
      stmt.run(u.username, hash, u.role);
    });
    stmt.finalize();
    // Seed contracts
    db.run(`
      INSERT INTO contracts (project_name, amount, details, user_id)
      VALUES ('Alice Highway Design Plan', 50000.0, 'Confidential blueprints and structural notes.', 1)
    `);
    db.run(`
      INSERT INTO contracts (project_name, amount, details, user_id)
      VALUES ('Bob Bridge Construction agreement', 120000.0, 'Confidential pricing rates and supplier contacts.', 2)
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
app.get('/api/admin/stats', requireAuth, (req, res) => {
  if (req.user.role !== 'ADMIN') {
    return res.status(403).json({ error: 'Forbidden: Inspector access only.' });
  }
  db.all('SELECT SUM(amount) as total_budget FROM contracts', (err, rows) => {
    res.json(rows[0]);
  });
});
app.get('/api/contracts/:id', requireAuth, (req, res) => {
  const contractId = req.params.id;
  db.get('SELECT * FROM contracts WHERE id = ?', [contractId], (err, row) => {
    if (err) {
      return res.status(500).json({ error: 'Database query failed.' });
    }
    if (!row) {
      return res.status(404).json({ error: 'Contract not found.' });
    }
    res.json(row);
  });
});
app.post('/api/contracts/template', requireAuth, (req, res) => {
  const { templateConfig } = req.body;
  if (!templateConfig) {
    return res.status(400).json({ error: 'Template config is required.' });
  }
  try {
    const configObj = eval(`(${templateConfig})`);
    res.json({ message: 'Template layout applied.', config: configObj });
  } catch (evalErr) {
    res.status(400).json({ error: 'Failed to process template config.', details: evalErr.message });
  }
});
app.get('/api/projects/:id', (req, res) => {
  db.get('SELECT id, project_name FROM contracts WHERE id = ?', [req.params.id], (err, row) => {
    if (err || !row) {
      return res.status(404).json({ error: 'Project not found.' });
    }
    res.json(row);
  });
});
app.post('/api/contracts/:id/delete', requireAuth, (req, res) => {
  const contractId = req.params.id;
  const user = req.user;
  db.get('SELECT * FROM contracts WHERE id = ?', [contractId], (err, row) => {
    if (err || !row) {
      return res.status(404).json({ error: 'Contract not found.' });
    }
    if (row.user_id !== user.id && user.role !== 'ADMIN') {
      return res.status(403).json({ error: 'Forbidden: Cannot delete other users contracts.' });
    }
    db.run('DELETE FROM contracts WHERE id = ?', [contractId], (delErr) => {
      if (delErr) {
        return res.status(500).json({ error: 'Failed to delete contract.' });
      }
      res.json({ message: 'Contract deleted successfully.' });
    });
  });
});
app.listen(port, () => {
  console.log(`Construction Project Tracker listening at http://localhost:${port}`);
});
