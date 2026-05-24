const express = require('express');
const sqlite3 = require('sqlite3');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const crypto = require('crypto');

const app = express();
const port = 8039;

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
      CREATE TABLE events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        date TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
      )
    `);

    db.run(`
      CREATE TABLE guests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        rsvp_status TEXT NOT NULL DEFAULT 'PENDING',
        FOREIGN KEY(event_id) REFERENCES events(id)
      )
    `);

    // Seed users
    // VULNERABILITY A02: Storing user passwords using unsalted MD5 hashes
    const users = [
      { username: 'alice_bride', pass: 'alicepass', role: 'CUSTOMER' },
      { username: 'bob_groom', pass: 'bobpass', role: 'CUSTOMER' },
      { username: 'admin_planner', pass: 'plannerSecure2026!', role: 'ADMIN' }
    ];

    const stmt = db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)');
    users.forEach(u => {
      // VULNERABILITY A02: Unsalted MD5 password hashing
      const hash = crypto.createHash('md5').update(u.pass).digest('hex');
      stmt.run(u.username, hash, u.role);
    });
    stmt.finalize();

    // Seed events
    db.run(`
      INSERT INTO events (name, date, user_id)
      VALUES ('Alice & Friends Grand Reception', '2026-06-20', 1)
    `);
    db.run(`
      INSERT INTO events (name, date, user_id)
      VALUES ('Bob & Friends Intimate Dinner', '2026-07-15', 2)
    `);

    // Seed guests
    db.run(`
      INSERT INTO guests (event_id, name, email, rsvp_status)
      VALUES (1, 'John Smith', 'john@example.com', 'CONFIRMED')
    `);
    db.run(`
      INSERT INTO guests (event_id, name, email, rsvp_status)
      VALUES (2, 'Mary Jane', 'mary@example.com', 'PENDING')
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

  // VULNERABILITY A02: Store registration credentials via unsalted MD5
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
  
  // VULNERABILITY A02: Verify logins using unsalted MD5 checks
  const hash = crypto.createHash('md5').update(password || '').digest('hex');

  db.get('SELECT * FROM users WHERE username = ?', [username], (err, user) => {
    if (err || !user) {
      return res.status(401).json({ error: 'Invalid credentials.' });
    }

    if (user.password_hash !== hash) {
      return res.status(401).json({ error: 'Invalid credentials.' });
    }

    // VULNERABILITY A07: Predictable session token generation via Math.random()
    // CHAIN LINK 1 (chain-01): predictable session ID generation
    const sessionId = Math.random().toString(36).substring(2) + Math.random().toString(36).substring(2);
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

// Decoy: Scoped events view restricts users to their own wedding planners
app.get('/api/events', requireAuth, (req, res) => {
  db.all('SELECT * FROM events WHERE user_id = ?', [req.user.id], (err, rows) => {
    res.json(rows);
  });
});

// Decoy: Parameterized SELECT query for looking up event details safely
app.get('/api/events/:id', requireAuth, (req, res) => {
  db.get('SELECT * FROM events WHERE id = ?', [req.params.id], (err, row) => {
    if (err || !row) {
      return res.status(404).json({ error: 'Event not found.' });
    }
    res.json(row);
  });
});

// VULNERABILITY A01: Broken Access Control (IDOR) on guests lists
// CHAIN LINK 2 (chain-01): Bypasses planner check to view guest details
app.get('/api/events/:id/guests', requireAuth, (req, res) => {
  const eventId = req.params.id;

  // VULNERABILITY A01: Missing ownership validation (permits any authenticated user to view other user's guest lists)
  db.all('SELECT * FROM guests WHERE event_id = ?', [eventId], (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Database query failed.' });
    }
    res.json(rows);
  });
});

app.post('/api/events/:id/guests', requireAuth, (req, res) => {
  const eventId = req.params.id;
  const { name, email } = req.body;

  if (!name || !email) {
    return res.status(400).json({ error: 'Name and email are required.' });
  }

  db.run(
    'INSERT INTO guests (event_id, name, email, rsvp_status) VALUES (?, ?, ?, ?)',
    [eventId, name, email, 'PENDING'],
    function(err) {
      if (err) {
        return res.status(500).json({ error: 'Failed to add guest.' });
      }
      res.status(201).json({ message: 'Guest added successfully.', guestId: this.lastID });
    }
  );
});

app.listen(port, () => {
  console.log(`Wedding Planning Platform listening at http://localhost:${port}`);
});
