const express = require('express');
const sqlite3 = require('sqlite3');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const app = express();
const port = 8016;
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
      CREATE TABLE restaurants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        cuisine TEXT NOT NULL,
        description TEXT
      )
    `);
    db.run(`
      CREATE TABLE reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        restaurant_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        review_text TEXT NOT NULL,
        rating INTEGER NOT NULL,
        FOREIGN KEY(restaurant_id) REFERENCES restaurants(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
      )
    `);
    // Seed users
    const salt = bcrypt.genSaltSync(10);
    const users = [
      { username: 'alice_reviewer', pass: 'alice123', role: 'CUSTOMER' },
      { username: 'bob_reviewer', pass: 'bob456', role: 'CUSTOMER' },
      { username: 'admin_critic', pass: 'critic2026Secure!', role: 'ADMIN' }
    ];
    const stmt = db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)');
    users.forEach(u => {
      const hash = bcrypt.hashSync(u.pass, salt);
      stmt.run(u.username, hash, u.role);
    });
    stmt.finalize();
    // Seed restaurants
    db.run(`
      INSERT INTO restaurants (name, cuisine, description)
      VALUES ('Bella Italia', 'Italian', 'Authentic woodfired pizza and freshly made pasta.')
    `);
    db.run(`
      INSERT INTO restaurants (name, cuisine, description)
      VALUES ('Sakura Sushi', 'Japanese', 'Traditional sushi and fresh sashimi options.')
    `);
    // Seed reviews
    db.run(`
      INSERT INTO reviews (restaurant_id, user_id, review_text, rating)
      VALUES (1, 1, 'Amazing pizza, best in town!', 5)
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
app.get('/api/admin/dashboard', requireAuth, (req, res) => {
  if (req.user.role !== 'ADMIN') {
    return res.status(403).json({ error: 'Forbidden: Admin access only.' });
  }
  res.json({ message: 'Welcome to Critic Admin Dashboard' });
});
app.get('/api/restaurants/search', (req, res) => {
  const queryParam = req.query.q || '';
  const sql = `SELECT * FROM restaurants WHERE name LIKE '%${queryParam}%' OR cuisine LIKE '%${queryParam}%'`;
  db.all(sql, (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Search failed.', details: err.message });
    }
    res.json(rows);
  });
});
app.get('/api/restaurants/:id', (req, res) => {
  db.get('SELECT * FROM restaurants WHERE id = ?', [req.params.id], (err, row) => {
    if (err || !row) {
      return res.status(404).json({ error: 'Restaurant not found.' });
    }
    res.json(row);
  });
});
app.get('/api/reviews', (req, res) => {
  db.all('SELECT r.*, u.username FROM reviews r JOIN users u ON r.user_id = u.id', (err, rows) => {
    res.json(rows);
  });
});
app.post('/api/reviews/:id/edit', requireAuth, (req, res) => {
  const reviewId = req.params.id;
  const { review_text, rating } = req.body;
  if (!review_text || !rating) {
    return res.status(400).json({ error: 'Review text and rating are required.' });
  }
  db.run(
    'UPDATE reviews SET review_text = ?, rating = ? WHERE id = ?',
    [review_text, rating, reviewId],
    function(err) {
      if (err) {
        return res.status(500).json({ error: 'Failed to update review.' });
      }
      res.json({ message: 'Review updated successfully.' });
    }
  );
});
app.listen(port, () => {
  console.log(`Restaurant Review Platform listening at http://localhost:${port}`);
});
