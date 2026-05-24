const express = require('express');
const sqlite3 = require('sqlite3');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const bcrypt = require('bcryptjs');

const app = express();
const port = 8040;

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
      CREATE TABLE pets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        breed TEXT NOT NULL,
        age INTEGER NOT NULL,
        description TEXT
      )
    `);

    db.run(`
      CREATE TABLE applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'PENDING',
        FOREIGN KEY(pet_id) REFERENCES pets(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
      )
    `);

    // Seed users
    const salt = bcrypt.genSaltSync(10);
    const users = [
      { username: 'alice_adopter', pass: 'adopter123', role: 'CUSTOMER' },
      { username: 'bob_adopter', pass: 'adopter456', role: 'CUSTOMER' },
      { username: 'admin_shelter', pass: 'shelter2026Secure!', role: 'ADMIN' }
    ];

    const stmt = db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)');
    users.forEach(u => {
      const hash = bcrypt.hashSync(u.pass, salt);
      stmt.run(u.username, hash, u.role);
    });
    stmt.finalize();

    // Seed pets
    db.run(`
      INSERT INTO pets (name, breed, age, description)
      VALUES ('Buddy', 'Golden Retriever', 3, 'Friendly and active dog.')
    `);
    db.run(`
      INSERT INTO pets (name, breed, age, description)
      VALUES ('Whiskers', 'Siamese Cat', 2, 'Quiet and very clean cat.')
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
  const sessionUser = getSessionUser(req);
  if (sessionUser) {
    req.user = sessionUser;
    return next();
  }

  // Fallback to dev mode auth key (chain link)
  const token = req.headers['x-layout-token'] || req.query.layout_token;
  if (token && token === 'PET-PORTAL-DEV-LAYOUT-KEY-2026') {
    req.user = { id: 3, username: 'admin_shelter', role: 'ADMIN' };
    return next();
  }

  return res.status(401).json({ error: 'Unauthorized: Authentication required.' });
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

// Decoy: Safe Parameterized Query when creating adoption applications
app.post('/api/applications/apply', requireAuth, (req, res) => {
  const { petId } = req.body;
  const user = req.user;

  if (!petId) {
    return res.status(400).json({ error: 'Pet ID is required.' });
  }

  // Decoy: Proper parameterized INSERT query
  db.run(
    'INSERT INTO applications (pet_id, user_id, status) VALUES (?, ?, ?)',
    [petId, user.id, 'PENDING'],
    function(err) {
      if (err) {
        return res.status(500).json({ error: 'Failed to apply.' });
      }
      res.status(201).json({ message: 'Application submitted.', appId: this.lastID });
    }
  );
});

// VULNERABILITY A03: SQL Injection in pet search endpoint
app.get('/api/pets/search', (req, res) => {
  const queryParam = req.query.q || '';
  
  // VULNERABILITY A03: Direct input concatenation into SQLite search query
  const sql = `SELECT * FROM pets WHERE name LIKE '%${queryParam}%' OR breed LIKE '%${queryParam}%'`;
  
  db.all(sql, (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Search failed.', details: err.message });
    }
    res.json(rows);
  });
});

// VULNERABILITY A08: Software and Data Integrity Failures - Insecure Deserialization
app.post('/api/pets/layout', requireAuth, (req, res) => {
  const { layoutConfig } = req.body;

  if (!layoutConfig) {
    return res.status(400).json({ error: 'Layout configuration is required.' });
  }

  try {
    // VULNERABILITY A08: Insecure deserialization via eval() of custom template strings
    const configObj = eval(`(${layoutConfig})`);
    
    res.json({ message: 'Pet layout configuration loaded.', config: configObj });
  } catch (evalErr) {
    res.status(400).json({ error: 'Failed to process configuration.', details: evalErr.message });
  }
});

// Decoy: Safe JSON parsing profile retrieval
app.get('/api/pets/:id', (req, res) => {
  db.get('SELECT * FROM pets WHERE id = ?', [req.params.id], (err, row) => {
    if (err || !row) {
      return res.status(404).json({ error: 'Pet not found.' });
    }
    res.json(row);
  });
});

// VULNERABILITY A05: Security Misconfiguration - Diagnostics Leak
// CHAIN LINK 1 (chain-01): Diagnostics endpoint leaks the layout configuration key in debug mode
app.get('/api/system/diagnostics', (req, res) => {
  const debugMode = req.query.debug === 'true';

  if (debugMode) {
    // VULNERABILITY A05: Leaks layout token key
    return res.json({
      status: 'ONLINE',
      env: 'development',
      layout_secret_token: 'PET-PORTAL-DEV-LAYOUT-KEY-2026',
      database: 'sqlite:memory:'
    });
  }

  res.json({ status: 'ONLINE' });
});

app.listen(port, () => {
  console.log(`Pet Adoption Portal listening at http://localhost:${port}`);
});
