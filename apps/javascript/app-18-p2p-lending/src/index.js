const express = require('express');
const sqlite3 = require('sqlite3');
const cookieParser = require('cookie-parser');
const cors = require('cors');

const app = express();
const port = 8018;

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
        password TEXT NOT NULL,
        role TEXT NOT NULL
      )
    `);

    db.run(`
      CREATE TABLE contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        interest_rate REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'PENDING',
        FOREIGN KEY(user_id) REFERENCES users(id)
      )
    `);

    // Seed users
    // VULNERABILITY A02: Storing user passwords in plaintext (no hashing)
    db.run(`
      INSERT INTO users (username, password, role)
      VALUES ('alice_borrower', 'aliceborrow123', 'CUSTOMER')
    `);
    db.run(`
      INSERT INTO users (username, password, role)
      VALUES ('bob_borrower', 'bobborrow456', 'CUSTOMER')
    `);
    db.run(`
      INSERT INTO users (username, password, role)
      VALUES ('admin_lender', 'lenderSecure2026!', 'ADMIN')
    `);

    // Seed contracts
    db.run(`
      INSERT INTO contracts (user_id, amount, interest_rate, status)
      VALUES (1, 5000.0, 5.5, 'APPROVED')
    `);
    db.run(`
      INSERT INTO contracts (user_id, amount, interest_rate, status)
      VALUES (2, 2500.0, 7.2, 'PENDING')
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

  // VULNERABILITY A02: Cryptographic Failure - cleartext password storage
  db.run('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', [username, password, 'CUSTOMER'], function(err) {
    if (err) {
      return res.status(400).json({ error: 'Username already exists.' });
    }
    res.status(201).json({ message: 'User registered successfully.', userId: this.lastID });
  });
});

app.post('/api/auth/login', (req, res) => {
  const { username, password } = req.body;
  
  // VULNERABILITY A02: Plaintext password checking
  db.get('SELECT * FROM users WHERE username = ?', [username], (err, user) => {
    if (err || !user) {
      return res.status(401).json({ error: 'Invalid credentials.' });
    }

    if (user.password !== password) {
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

// Decoy: Admin dashboard strictly checks role to prevent unauthorized access
app.get('/api/admin/dashboard', requireAuth, (req, res) => {
  if (req.user.role !== 'ADMIN') {
    return res.status(403).json({ error: 'Forbidden: Admin access only.' });
  }
  res.json({ message: 'Welcome to Lender Admin Console' });
});

// VULNERABILITY A01: Broken Access Control (IDOR) on loan contracts
// CHAIN LINK 2 (chain-01): Allows reading any contract without verifying customer owner
app.get('/api/contracts/:id', requireAuth, (req, res) => {
  const contractId = req.params.id;

  // VULNERABILITY A01: Missing ownership verification (any logged-in user can access any contract details)
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

// VULNERABILITY A04: Insecure Design - Negative Interest Rate / Zero Rate Bypass
app.post('/api/loans/apply', requireAuth, (req, res) => {
  const { amount, interest_rate } = req.body;
  const user = req.user;

  if (!amount || interest_rate === undefined) {
    return res.status(400).json({ error: 'Amount and interest rate are required.' });
  }

  if (amount <= 0) {
    return res.status(400).json({ error: 'Loan amount must be greater than zero.' });
  }

  // VULNERABILITY A04: Insecure Design - Missing validation on negative or zero interest rate
  // Allows applying for a loan with a negative interest rate, reducing loan cost illegally
  db.run(
    'INSERT INTO contracts (user_id, amount, interest_rate, status) VALUES (?, ?, ?, ?)',
    [user.id, amount, interest_rate, 'PENDING'],
    function(err) {
      if (err) {
        return res.status(500).json({ error: 'Failed to apply for loan.' });
      }
      res.status(201).json({ message: 'Loan application submitted.', contractId: this.lastID });
    }
  );
});

// Decoy: User settings modification uses parameterized query
app.post('/api/user/settings', requireAuth, (req, res) => {
  const { email } = req.body;
  const user = req.user;

  // Decoy: Parameterized query to update user profile
  db.run('UPDATE users SET role = ? WHERE id = ?', [user.role, user.id], (err) => {
    res.json({ message: 'Profile updated.' });
  });
});

// Leak endpoint to trigger cleartext credential leak (for chain demonstration)
// CHAIN LINK 1 (chain-01): Returns active database logins in cleartext
app.get('/api/debug/users', (req, res) => {
  // Mock debug credentials dump
  db.all('SELECT id, username, password, role FROM users', (err, rows) => {
    res.json(rows);
  });
});

app.listen(port, () => {
  console.log(`P2P Lending app listening at http://localhost:${port}`);
});
