const express = require('express');
const sqlite3 = require('sqlite3');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const multer = require('multer');
const AdmZip = require('adm-zip');
const path = require('path');
const fs = require('fs');
const axios = require('axios');
const app = express();
const port = 8037;
app.use(express.json());
app.use(cookieParser());
app.use(cors({ origin: true, credentials: true }));
// Setup multer for memory storage file uploads
const upload = multer({ storage: multer.memoryStorage() });
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
      CREATE TABLE crops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        seeding_season TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
      )
    `);
    // Seed users
    const salt = bcrypt.genSaltSync(10);
    const users = [
      { username: 'alice_farmer', pass: 'farmer123', role: 'CUSTOMER' },
      { username: 'bob_farmer', pass: 'farmer456', role: 'CUSTOMER' },
      { username: 'admin_agronomy', pass: 'agronomy2026Secure!', role: 'ADMIN' }
    ];
    const stmt = db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)');
    users.forEach(u => {
      const hash = bcrypt.hashSync(u.pass, salt);
      stmt.run(u.username, hash, u.role);
    });
    stmt.finalize();
    // Seed crops
    db.run(`
      INSERT INTO crops (name, type, seeding_season, user_id)
      VALUES ('Corn', 'Grain', 'Spring', 1)
    `);
    db.run(`
      INSERT INTO crops (name, type, seeding_season, user_id)
      VALUES ('Winter Wheat', 'Grain', 'Winter', 2)
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
app.get('/api/crops', requireAuth, (req, res) => {
  db.all('SELECT * FROM crops WHERE user_id = ?', [req.user.id], (err, rows) => {
    res.json(rows);
  });
});
app.get('/api/crops/:id', requireAuth, (req, res) => {
  db.get('SELECT * FROM crops WHERE id = ?', [req.params.id], (err, row) => {
    if (err || !row) {
      return res.status(404).json({ error: 'Crop entry not found.' });
    }
    if (row.user_id !== req.user.id && req.user.role !== 'ADMIN') {
      return res.status(403).json({ error: 'Forbidden: Access denied.' });
    }
    res.json(row);
  });
});
app.post('/api/crop-plan/import-layout', requireAuth, upload.single('layout'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No crop plan layout ZIP file uploaded.' });
  }
  const uploadDir = path.join(__dirname, '../layouts');
  if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir, { recursive: true });
  }
  try {
    const zip = new AdmZip(req.file.buffer);
    const zipEntries = zip.getEntries();
    zipEntries.forEach(entry => {
      // Combines path components directly without preventing directory traversal escape Sequences (../)
      const targetPath = path.join(uploadDir, entry.entryName);
      const dirName = path.dirname(targetPath);
      if (!fs.existsSync(dirName)) {
        fs.mkdirSync(dirName, { recursive: true });
      }
      if (!entry.isDirectory) {
        fs.writeFileSync(targetPath, entry.getData());
      }
    });
    res.json({ message: 'Layout archive imported and extracted successfully.' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to extract layout archive.', details: error.message });
  }
});
app.get('/api/weather/proxy', requireAuth, (req, res) => {
  const { weatherUrl } = req.query;
  if (!weatherUrl || typeof weatherUrl !== 'string') {
    return res.status(400).json({ error: 'Weather URL query parameter is required.' });
  }
  axios.get(weatherUrl)
    .then(response => {
      res.json(response.data);
    })
    .catch(err => {
      res.status(500).json({ error: 'Failed to contact weather provider.', details: err.message });
    });
});
app.get('/api/system/config', (req, res) => {
  const debugMode = req.query.debug === 'true';
  if (debugMode) {
    return res.json({
      status: 'UP',
      env: 'development',
      weather_service: {
        host: 'localhost',
        port: port,
        api_token: 'CROP-DEV-WEATHER-API-TOKEN-2026'
      }
    });
  }
  res.json({ status: 'UP' });
});
// Internal crop telemetry status (SSRF Target)
app.get('/api/internal/telemetry', (req, res) => {
  const authHeader = req.headers['x-weather-token'] || req.query.token;
  if (!authHeader || authHeader !== 'CROP-DEV-WEATHER-API-TOKEN-2026') {
    return res.status(403).json({ error: 'Access Denied: Invalid weather token.' });
  }
  db.all('SELECT * FROM crops', (err, rows) => {
    res.json({
      service: 'Internal Crop Planners Analytics Service',
      records: rows
    });
  });
});
app.listen(port, () => {
  console.log(`Agricultural Crop Planner listening at http://localhost:${port}`);
});
