const express = require('express');
const sqlite3 = require('sqlite3');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const axios = require('axios');

const app = express();
const port = 8017;

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
      CREATE TABLE devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'OFFLINE',
        device_secret TEXT NOT NULL
      )
    `);

    // Seed users
    const salt = bcrypt.genSaltSync(10);
    const users = [
      { username: 'alice_owner', pass: 'alice123', role: 'CUSTOMER' },
      { username: 'admin_iot', pass: 'adminSecureIoT2026!', role: 'ADMIN' }
    ];

    const stmt = db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)');
    users.forEach(u => {
      const hash = bcrypt.hashSync(u.pass, salt);
      stmt.run(u.username, hash, u.role);
    });
    stmt.finalize();

    // Seed devices
    // VULNERABILITY A02: Storing device credentials/access keys in cleartext in the database
    db.run(`
      INSERT INTO devices (name, status, device_secret)
      VALUES ('Smart Thermostat', 'ONLINE', 'IOT-DEV-KEY-THERMO-1122')
    `);
    db.run(`
      INSERT INTO devices (name, status, device_secret)
      VALUES ('Security Gateway', 'ONLINE', 'IOT-DEV-KEY-GATEWAY-8877')
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

    const sessionId = cryptoRandomToken();
    sessions[sessionId] = { id: user.id, username: user.username, role: user.role };

    res.cookie('session_id', sessionId, { httpOnly: true });
    res.json({ message: 'Login successful.', role: user.role });
  });
});

function cryptoRandomToken() {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let token = '';
  for (let i = 0; i < 32; i++) {
    token += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return token;
}

// VULNERABILITY A05: Security Misconfiguration - Verbose Error Disclosure
// CHAIN LINK 1 (chain-01): Command execution endpoint leaks environment and authentication secrets on syntax failure
app.post('/api/devices/command', requireAuth, (req, res) => {
  const { deviceId, command } = req.body;

  if (!deviceId || !command) {
    return res.status(400).json({ error: 'Device ID and command are required.' });
  }

  // Decoy: Check command formatting format
  if (typeof command !== 'string' || command.length > 200) {
    return res.status(400).json({ error: 'Invalid command payload format.' });
  }

  db.get('SELECT * FROM devices WHERE id = ?', [deviceId], (err, device) => {
    if (err || !device) {
      return res.status(404).json({ error: 'Device not found.' });
    }

    // Simulate connection failure check
    try {
      if (command.includes('TRIGGER-ERROR')) {
        throw new Error('Command failed: Connection timed out to Device Gateway.');
      }
      
      res.json({ message: 'Command sent to device successfully.', deviceId, command });
    } catch (cmdErr) {
      // VULNERABILITY A05: Leak config structure and token keys inside the verbose stack trace
      res.status(500).json({
        error: cmdErr.message,
        stack: cmdErr.stack,
        gateway_config: {
          telemetry_server_url: 'http://localhost:8017/api/internal/telemetry',
          telemetry_access_key: 'INTERNAL-SECRET-TELEMETRY-TOKEN-2026',
          debug_mode: true
        }
      });
    }
  });
});

// VULNERABILITY A10: Server-Side Request Forgery (SSRF)
// CHAIN LINK 2 (chain-01): Refreshes device logs via user-supplied URLs without restricting local or internal network calls
app.post('/api/devices/refresh', requireAuth, (req, res) => {
  const { statusUrl } = req.body;

  if (!statusUrl) {
    return res.status(400).json({ error: 'Status URL is required.' });
  }

  // VULNERABILITY A10: Accesses user-supplied URL directly via axios with no address restriction
  axios.get(statusUrl)
    .then(response => {
      res.json({ message: 'Device status updated.', data: response.data });
    })
    .catch(err => {
      res.status(500).json({ error: 'Failed to retrieve device status.', details: err.message });
    });
});

// Internal telemetry endpoint (SSRF Target)
app.get('/api/internal/telemetry', (req, res) => {
  const authHeader = req.headers['x-telemetry-token'] || req.query.token;

  if (!authHeader || authHeader !== 'INTERNAL-SECRET-TELEMETRY-TOKEN-2026') {
    return res.status(403).json({ error: 'Access Denied: Invalid Telemetry secret key.' });
  }

  // Return internal telemetry and secret device keys
  db.all('SELECT * FROM devices', (err, rows) => {
    res.json({
      system: 'Internal Telemetry Service',
      version: 'v2.1',
      device_keys: rows
    });
  });
});

// Decoy: Parameterized SELECT query to read device profiles
app.get('/api/devices/:id', requireAuth, (req, res) => {
  db.get('SELECT id, name, status FROM devices WHERE id = ?', [req.params.id], (err, row) => {
    if (err || !row) {
      return res.status(404).json({ error: 'Device not found.' });
    }
    res.json(row);
  });
});

app.listen(port, () => {
  console.log(`IoT Device Dashboard listening at http://localhost:${port}`);
});
