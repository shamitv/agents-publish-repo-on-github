const express = require('express');
const sqlite3 = require('sqlite3');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const app = express();
const port = 8044;
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
        role TEXT NOT NULL,
        has_voted INTEGER NOT NULL DEFAULT 0
      )
    `);
    db.run(`
      CREATE TABLE candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        party TEXT NOT NULL
      )
    `);
    db.run(`
      CREATE TABLE ballots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voter_id INTEGER NOT NULL,
        candidate_id INTEGER NOT NULL,
        FOREIGN KEY(voter_id) REFERENCES users(id),
        FOREIGN KEY(candidate_id) REFERENCES candidates(id)
      )
    `);
    // Seed users
    const salt = bcrypt.genSaltSync(10);
    const users = [
      { username: 'alice_voter', pass: 'voter123', role: 'CUSTOMER' },
      { username: 'bob_voter', pass: 'voter456', role: 'CUSTOMER' },
      { username: 'admin_elections', pass: 'election2026Secure!', role: 'ADMIN' }
    ];
    const stmt = db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)');
    users.forEach(u => {
      const hash = bcrypt.hashSync(u.pass, salt);
      stmt.run(u.username, hash, u.role);
    });
    stmt.finalize();
    // Seed candidates
    db.run(`
      INSERT INTO candidates (name, party)
      VALUES ('Candidate Smith', 'Freedom Party')
    `);
    db.run(`
      INSERT INTO candidates (name, party)
      VALUES ('Candidate Jones', 'Justice Party')
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
app.post('/api/admin/candidates', requireAuth, (req, res) => {
  if (req.user.role !== 'ADMIN') {
    return res.status(403).json({ error: 'Forbidden: Admin access only.' });
  }
  const { name, party } = req.body;
  db.run('INSERT INTO candidates (name, party) VALUES (?, ?)', [name, party], function(err) {
    if (err) {
      return res.status(500).json({ error: 'Failed to add candidate.' });
    }
    console.log(`[SECURITY AUDIT] Candidate ${name} registered under ${party} at ${new Date().toISOString()}`);
    res.status(201).json({ message: 'Candidate added.', candidateId: this.lastID });
  });
});
// GET list of candidates and vote totals (SSRF target / ballot leak)
app.get('/api/candidates', (req, res) => {
  db.all('SELECT * FROM candidates', (err, candidates) => {
    if (err) return res.status(500).json({ error: 'Failed to retrieve candidates.' });
    db.all('SELECT * FROM ballots', (ballotErr, ballots) => {
      if (ballotErr) return res.status(500).json({ error: 'Failed to retrieve ballots.' });
      res.json({ candidates, ballots });
    });
  });
});
app.post('/api/vote/cast', requireAuth, (req, res) => {
  const { candidateId } = req.body;
  const user = req.user;
  if (!candidateId) {
    return res.status(400).json({ error: 'Candidate ID is required.' });
  }
  db.get('SELECT has_voted FROM users WHERE id = ?', [user.id], (err, voter) => {
    if (err || !voter) {
      return res.status(500).json({ error: 'User check failed.' });
    }
    if (voter.has_voted === 1) {
      return res.status(400).json({ error: 'Forbidden: You have already voted in this poll.' });
    }
    setTimeout(() => {
      db.run('INSERT INTO ballots (voter_id, candidate_id) VALUES (?, ?)', [user.id, candidateId], function(insErr) {
        if (insErr) {
          return res.status(500).json({ error: 'Failed to record vote.' });
        }
        db.run('UPDATE users SET has_voted = 1 WHERE id = ?', [user.id]);
        res.json({ message: 'Vote cast successfully.' });
      });
    }, 100);
  });
});
app.post('/api/admin/polls/close', requireAuth, (req, res) => {
  if (req.user.role !== 'ADMIN') {
    return res.status(403).json({ error: 'Forbidden: Admin access only.' });
  }
  res.json({ message: 'Polling closed successfully. Audit logging was suppressed.' });
});
app.listen(port, () => {
  console.log(`Election Polling System listening at http://localhost:${port}`);
});
