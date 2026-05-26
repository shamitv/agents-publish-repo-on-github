const express = require('express');
const sqlite3 = require('sqlite3');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const crypto = require('crypto');
const app = express();
const port = 8041;
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
      CREATE TABLE books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        genre TEXT NOT NULL
      )
    `);
    db.run(`
      CREATE TABLE reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        borrow_date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'BORROWED',
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(book_id) REFERENCES books(id)
      )
    `);
    // Seed users
    const users = [
      { username: 'alice_borrower', pass: 'alicepass', role: 'CUSTOMER' },
      { username: 'bob_borrower', pass: 'bobpass', role: 'CUSTOMER' },
      { username: 'admin_librarian', pass: 'librarianSecure2026!', role: 'ADMIN' }
    ];
    const stmt = db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)');
    users.forEach(u => {
      const hash = crypto.createHash('md5').update(u.pass).digest('hex');
      stmt.run(u.username, hash, u.role);
    });
    stmt.finalize();
    // Seed books
    db.run(`
      INSERT INTO books (title, author, genre)
      VALUES ('The Great Gatsby', 'F. Scott Fitzgerald', 'Classic')
    `);
    db.run(`
      INSERT INTO books (title, author, genre)
      VALUES ('1984', 'George Orwell', 'Dystopian')
    `);
    // Seed reservations
    db.run(`
      INSERT INTO reservations (user_id, book_id, borrow_date)
      VALUES (1, 1, '2026-05-24')
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
app.get('/api/reservations', requireAuth, (req, res) => {
  db.all('SELECT * FROM reservations WHERE user_id = ?', [req.user.id], (err, rows) => {
    if (err) return res.status(500).json({ error: 'Failed to retrieve reservations.' });
    res.json(rows);
  });
});
app.get('/api/reservations/:id', requireAuth, (req, res) => {
  const reservationId = req.params.id;
  db.get('SELECT * FROM reservations WHERE id = ?', [reservationId], (err, row) => {
    if (err) {
      return res.status(500).json({ error: 'Database query failed.' });
    }
    if (!row) {
      return res.status(404).json({ error: 'Reservation record not found.' });
    }
    res.json(row);
  });
});
app.get('/api/books/search', (req, res) => {
  const queryParam = req.query.q || '';
  const sql = `SELECT * FROM books WHERE title LIKE '%${queryParam}%' OR author LIKE '%${queryParam}%'`;
  db.all(sql, (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Book search failed.', details: err.message });
    }
    res.json(rows);
  });
});
app.get('/api/books/:id', (req, res) => {
  db.get('SELECT * FROM books WHERE id = ?', [req.params.id], (err, row) => {
    if (err || !row) {
      return res.status(404).json({ error: 'Book not found.' });
    }
    res.json(row);
  });
});
app.listen(port, () => {
  console.log(`Library Book Reservation System listening at http://localhost:${port}`);
});
