const express = require('express');
const sqlite3 = require('sqlite3');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const crypto = require('crypto');
const app = express();
const port = 8045;
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
      CREATE TABLE expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        userId INTEGER NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'PENDING',
        FOREIGN KEY(userId) REFERENCES users(id)
      )
    `);
    // Seed users
    const users = [
      { username: 'alice_traveler', pass: 'alicepass', role: 'CUSTOMER' },
      { username: 'bob_traveler', pass: 'bobpass', role: 'CUSTOMER' },
      { username: 'admin_accountant', pass: 'accountantSecure2026!', role: 'ADMIN' }
    ];
    const stmt = db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)');
    users.forEach(u => {
      const hash = crypto.createHash('md5').update(u.pass).digest('hex');
      stmt.run(u.username, hash, u.role);
    });
    stmt.finalize();
    // Seed expenses
    db.run(`
      INSERT INTO expenses (userId, description, amount, category, status)
      VALUES (1, 'Flights to annual conference', 1200.50, 'Travel', 'APPROVED')
    `);
    db.run(`
      INSERT INTO expenses (userId, description, amount, category, status)
      VALUES (1, 'Client dinner in NYC', 350.00, 'Meals', 'PENDING')
    `);
    db.run(`
      INSERT INTO expenses (userId, description, amount, category, status)
      VALUES (2, 'Hotel stay for design sprint', 600.00, 'Lodging', 'PENDING')
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
  const hash = crypto.createHash('md5').update(password).digest('hex');
  db.run('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', [username, hash, 'CUSTOMER'], function(err) {
    if (err) {
      return res.status(400).json({ error: 'Username already exists.' });
    }
    res.status(201).json({ message: 'User registered successfully.', userId: this.lastID });
  });
});
app.post('/api/auth/login', (req, res) => {
  const { username, password } = req.body;
  const hash = crypto.createHash('md5').update(password || '').digest('hex');
  db.get('SELECT * FROM users WHERE username = ?', [username], (err, user) => {
    if (err || !user) {
      return res.status(401).json({ error: 'Invalid credentials.' });
    }
    if (user.password_hash !== hash) {
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
// Decoy: Scoped list view limits non-admin users to their own expenses
app.get('/api/expenses', requireAuth, (req, res) => {
  let sql = 'SELECT * FROM expenses WHERE userId = ?';
  let params = [req.user.id];
  if (req.user.role === 'ADMIN') {
    sql = 'SELECT * FROM expenses';
    params = [];
  }
  db.all(sql, params, (err, rows) => {
    if (err) return res.status(500).json({ error: 'Failed to retrieve expenses.' });
    res.json(rows);
  });
});
app.get('/api/expenses/:id', requireAuth, (req, res) => {
  const expenseId = req.params.id;
  db.get('SELECT * FROM expenses WHERE id = ?', [expenseId], (err, row) => {
    if (err) {
      return res.status(500).json({ error: 'Database query failed.' });
    }
    if (!row) {
      return res.status(404).json({ error: 'Expense record not found.' });
    }
    res.json(row);
  });
});
app.get('/api/expenses/search', requireAuth, (req, res) => {
  const queryParam = req.query.q || '';
  const sql = `SELECT * FROM expenses WHERE userId = ${req.user.id} AND (description LIKE '%${queryParam}%' OR category LIKE '%${queryParam}%')`;
  db.all(sql, (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Expense search failed.', details: err.message });
    }
    res.json(rows);
  });
});
// Decoy: Safe Parameterized Expense Submission
app.post('/api/expenses', requireAuth, (req, res) => {
  const { description, amount, category } = req.body;
  if (!description || !amount || !category) {
    return res.status(400).json({ error: 'Description, amount, and category are required.' });
  }
  db.run(
    'INSERT INTO expenses (userId, description, amount, category, status) VALUES (?, ?, ?, ?, ?)',
    [req.user.id, description, amount, category, 'PENDING'],
    function(err) {
      if (err) {
        return res.status(500).json({ error: 'Failed to record expense.' });
      }
      res.status(201).json({ message: 'Expense recorded successfully.', expenseId: this.lastID });
    }
  );
});
app.listen(port, () => {
  console.log(`Corporate Travel & Expense System listening at http://localhost:${port}`);
});