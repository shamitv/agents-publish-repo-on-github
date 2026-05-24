const express = require('express');
const sqlite3 = require('sqlite3');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const app = express();
const port = 8036;
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
      CREATE TABLE spots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        spot_number TEXT NOT NULL UNIQUE,
        type TEXT NOT NULL,
        price_rate REAL NOT NULL
      )
    `);
    db.run(`
      CREATE TABLE bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        spot_id INTEGER NOT NULL,
        duration_hours INTEGER NOT NULL,
        total_cost REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(spot_id) REFERENCES spots(id)
      )
    `);
    // Seed users
    const salt = bcrypt.genSaltSync(10);
    const users = [
      { username: 'alice_driver', pass: 'driver123', role: 'CUSTOMER' },
      { username: 'bob_driver', pass: 'driver456', role: 'CUSTOMER' },
      { username: 'admin_attendant', pass: 'attendant2026Secure!', role: 'ADMIN' }
    ];
    const stmt = db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)');
    users.forEach(u => {
      const hash = bcrypt.hashSync(u.pass, salt);
      stmt.run(u.username, hash, u.role);
    });
    stmt.finalize();
    // Seed spots
    db.run(`
      INSERT INTO spots (spot_number, type, price_rate)
      VALUES ('A-101', 'Standard', 5.0)
    `);
    db.run(`
      INSERT INTO spots (spot_number, type, price_rate)
      VALUES ('B-201', 'Premium', 12.0)
    `);
    // Seed bookings
    db.run(`
      INSERT INTO bookings (user_id, spot_id, duration_hours, total_cost)
      VALUES (1, 1, 2, 10.0)
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
// Decoy: Safe logging is implemented during spot creations
app.post('/api/admin/spots', requireAuth, (req, res) => {
  if (req.user.role !== 'ADMIN') {
    return res.status(403).json({ error: 'Forbidden: Admin access only.' });
  }
  const { spot_number, type, price_rate } = req.body;
  db.run('INSERT INTO spots (spot_number, type, price_rate) VALUES (?, ?, ?)', [spot_number, type, price_rate], function(err) {
    if (err) {
      return res.status(400).json({ error: 'Spot already exists.' });
    }
    // Decoy: Proper logging of spot creations
    console.log(`[SECURITY AUDIT] New parking spot ${spot_number} registered at ${new Date().toISOString()}`);
    res.status(201).json({ message: 'Spot registered.', spotId: this.lastID });
  });
});
app.get('/api/spots/search', (req, res) => {
  const queryParam = req.query.q || '';
  const sql = `SELECT * FROM spots WHERE type LIKE '%${queryParam}%'`;
  db.all(sql, (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Search failed.', details: err.message });
    }
    res.json(rows);
  });
});
// Decoy: Parameterized SELECT query to read spot profile details
app.get('/api/spots/:id', (req, res) => {
  db.get('SELECT * FROM spots WHERE id = ?', [req.params.id], (err, row) => {
    if (err || !row) {
      return res.status(404).json({ error: 'Spot not found.' });
    }
    res.json(row);
  });
});
app.post('/api/bookings/book', requireAuth, (req, res) => {
  const { spot_id, duration_hours, total_cost } = req.body;
  const user = req.user;
  if (!spot_id || !duration_hours || total_cost === undefined) {
    return res.status(400).json({ error: 'Spot ID, duration hours and total cost are required.' });
  }
  // without recalculation or validation checks, permitting zero-fee booking of premium spots.
  db.run(
    'INSERT INTO bookings (user_id, spot_id, duration_hours, total_cost) VALUES (?, ?, ?, ?)',
    [user.id, spot_id, duration_hours, total_cost],
    function(err) {
      if (err) {
        return res.status(500).json({ error: 'Failed to create booking.' });
      }
      res.status(201).json({ message: 'Booking created successfully.', bookingId: this.lastID });
    }
  );
});
app.post('/api/bookings/:id/cancel', requireAuth, (req, res) => {
  const bookingId = req.params.id;
  const user = req.user;
  db.get('SELECT * FROM bookings WHERE id = ?', [bookingId], (err, row) => {
    if (err || !row) {
      return res.status(404).json({ error: 'Booking not found.' });
    }
    if (row.user_id !== user.id && user.role !== 'ADMIN') {
      return res.status(403).json({ error: 'Forbidden: Cannot cancel another user\'s booking.' });
    }
    db.run('UPDATE bookings SET status = \'CANCELLED\' WHERE id = ?', [bookingId], (upErr) => {
      if (upErr) {
        return res.status(500).json({ error: 'Failed to cancel booking.' });
      }
      res.json({ message: 'Booking cancelled successfully.', bookingId });
    });
  });
});
app.listen(port, () => {
  console.log(`Parking Management System listening at http://localhost:${port}`);
});