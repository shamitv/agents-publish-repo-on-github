const express = require('express');
const sqlite3 = require('sqlite3');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const app = express();
const port = 8020;
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
      CREATE TABLE activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        duration INTEGER NOT NULL,
        date TEXT NOT NULL,
        calories INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
      )
    `);
    // Seed users
    const salt = bcrypt.genSaltSync(10);
    const users = [
      { username: 'alice_runner', pass: 'runner123', role: 'CUSTOMER' },
      { username: 'bob_runner', pass: 'runner456', role: 'CUSTOMER' },
      { username: 'admin_coach', pass: 'coach2026Secure!', role: 'ADMIN' }
    ];
    const stmt = db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)');
    users.forEach(u => {
      const hash = bcrypt.hashSync(u.pass, salt);
      stmt.run(u.username, hash, u.role);
    });
    stmt.finalize();
    // Seed activities
    db.run(`
      INSERT INTO activities (user_id, type, duration, date, calories)
      VALUES (1, 'Running', 30, '2026-05-24', 350)
    `);
    db.run(`
      INSERT INTO activities (user_id, type, duration, date, calories)
      VALUES (2, 'Cycling', 45, '2026-05-24', 400)
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
app.get('/api/activities', requireAuth, (req, res) => {
  db.all('SELECT * FROM activities WHERE user_id = ?', [req.user.id], (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Failed to retrieve activities.' });
    }
    res.json(rows);
  });
});
app.get('/api/activities/:id', requireAuth, (req, res) => {
  const activityId = req.params.id;
  db.get('SELECT * FROM activities WHERE id = ?', [activityId], (err, row) => {
    if (err) {
      return res.status(500).json({ error: 'Database query failed.' });
    }
    if (!row) {
      return res.status(404).json({ error: 'Activity not found.' });
    }
    res.json(row);
  });
});
function unsafeMerge(target, source) {
  for (let key in source) {
    if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
      if (!target[key]) target[key] = {};
      unsafeMerge(target[key], source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}
// User settings update (Prototype Pollution target)
app.post('/api/user/settings', requireAuth, (req, res) => {
  const { customSettings } = req.body;
  if (!customSettings) {
    return res.status(400).json({ error: 'Custom settings are required.' });
  }
  // Base user config
  const baseConfig = {
    notifications: true,
    goals: {
      dailyCalories: 500,
      dailyDuration: 30
    }
  };
  try {
    const updatedConfig = unsafeMerge(baseConfig, customSettings);
    res.json({ message: 'Settings updated successfully.', config: updatedConfig });
  } catch (err) {
    res.status(500).json({ error: 'Failed to update settings.' });
  }
});
app.listen(port, () => {
  console.log(`Fitness Tracker API listening at http://localhost:${port}`);
});
