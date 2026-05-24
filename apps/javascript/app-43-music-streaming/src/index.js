const express = require('express');
const sqlite3 = require('sqlite3');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const axios = require('axios');
const app = express();
const port = 8043;
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
      CREATE TABLE playlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        is_private INTEGER NOT NULL DEFAULT 1,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
      )
    `);
    db.run(`
      CREATE TABLE tracks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        playlist_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        artist TEXT NOT NULL,
        FOREIGN KEY(playlist_id) REFERENCES playlists(id)
      )
    `);
    // Seed users
    const salt = bcrypt.genSaltSync(10);
    const users = [
      { username: 'alice_listener', pass: 'listener123', role: 'CUSTOMER' },
      { username: 'bob_listener', pass: 'listener456', role: 'CUSTOMER' },
      { username: 'admin_dj', pass: 'dj2026Secure!', role: 'ADMIN' }
    ];
    const stmt = db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)');
    users.forEach(u => {
      const hash = bcrypt.hashSync(u.pass, salt);
      stmt.run(u.username, hash, u.role);
    });
    stmt.finalize();
    // Seed playlists
    db.run(`
      INSERT INTO playlists (name, is_private, user_id)
      VALUES ('Alices Rock Chill', 1, 1)
    `);
    db.run(`
      INSERT INTO playlists (name, is_private, user_id)
      VALUES ('Bobs Pop Workout', 1, 2)
    `);
    // Seed tracks
    db.run(`
      INSERT INTO tracks (playlist_id, title, artist)
      VALUES (1, 'Bohemian Rhapsody', 'Queen')
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
// Decoy: Scoped playlist listing prevents other users from seeing private names
app.get('/api/playlists', requireAuth, (req, res) => {
  db.all('SELECT * FROM playlists WHERE user_id = ?', [req.user.id], (err, rows) => {
    res.json(rows);
  });
});
app.get('/api/playlists/:id', requireAuth, (req, res) => {
  const playlistId = req.params.id;
  db.get('SELECT * FROM playlists WHERE id = ?', [playlistId], (err, row) => {
    if (err) {
      return res.status(500).json({ error: 'Database query failed.' });
    }
    if (!row) {
      return res.status(404).json({ error: 'Playlist not found.' });
    }
    res.json(row);
  });
});
// Decoy: Safe Parameterized Query when adding tracks
app.post('/api/tracks', requireAuth, (req, res) => {
  const { playlist_id, title, artist } = req.body;
  const user = req.user;
  if (!playlist_id || !title || !artist) {
    return res.status(400).json({ error: 'Playlist ID, title and artist are required.' });
  }
  db.get('SELECT * FROM playlists WHERE id = ?', [playlist_id], (err, row) => {
    if (err || !row || row.user_id !== user.id) {
      return res.status(403).json({ error: 'Forbidden: Cannot edit this playlist.' });
    }
    // Decoy: Proper parameterized INSERT query
    db.run(
      'INSERT INTO tracks (playlist_id, title, artist) VALUES (?, ?, ?)',
      [playlist_id, title, artist],
      function(insErr) {
        if (insErr) {
          return res.status(500).json({ error: 'Failed to add track.' });
        }
        res.status(201).json({ message: 'Track added successfully.', trackId: this.lastID });
      }
    );
  });
});
app.get('/api/cover', requireAuth, (req, res) => {
  const { url } = req.query;
  if (!url || typeof url !== 'string') {
    return res.status(400).json({ error: 'URL query parameter is required.' });
  }
  axios.get(url)
    .then(response => {
      res.json(response.data);
    })
    .catch(err => {
      res.status(500).json({ error: 'Failed to contact art provider.', details: err.message });
    });
});
app.get('/api/system/status', (req, res) => {
  const debugMode = req.query.debug === 'true';
  if (debugMode) {
    return res.json({
      status: 'UP',
      env: 'development',
      metrics_service: {
        host: 'localhost',
        port: port,
        api_token: 'INTERNAL-METRICS-API-SECRET-2026'
      }
    });
  }
  res.json({ status: 'UP' });
});
// Internal telemetry endpoint (SSRF Target)
app.get('/api/internal/analytics', (req, res) => {
  const authHeader = req.headers['x-metrics-token'] || req.query.token;
  if (!authHeader || authHeader !== 'INTERNAL-METRICS-API-SECRET-2026') {
    return res.status(403).json({ error: 'Access Denied: Invalid metrics token.' });
  }
  db.all('SELECT * FROM playlists', (err, rows) => {
    res.json({
      system: 'Internal Analytics Service',
      version: 'v1.0',
      playlists: rows
    });
  });
});
app.listen(port, () => {
  console.log(`Music Streaming Playlist Service listening at http://localhost:${port}`);
});