import express, { Request, Response, NextFunction } from 'express';
import sqlite3 from 'sqlite3';
import cookieParser from 'cookie-parser';
import cors from 'cors';
import crypto from 'crypto';
const app = express();
const port = 8034;
app.use(express.json());
app.use(cookieParser());
app.use(cors({ origin: true, credentials: true }));
// Initialize SQLite database
const db = new sqlite3.Database(':memory:');
interface User {
  id: number;
  username: string;
  password_hash: string;
  role: string;
}
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
      CREATE TABLE packages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL
      )
    `);
    db.run(`
      CREATE TABLE subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        package_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(package_id) REFERENCES packages(id)
      )
    `);
    // Seed users
    const users = [
      { username: 'alice_subscriber', pass: 'alicepass', role: 'CUSTOMER' },
      { username: 'bob_subscriber', pass: 'bobpass', role: 'CUSTOMER' },
      { username: 'admin_agent', pass: 'adminpass2026', role: 'ADMIN' }
    ];
    const stmt = db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)');
    users.forEach(u => {
      const hash = crypto.createHash('md5').update(u.pass).digest('hex');
      stmt.run(u.username, hash, u.role);
    });
    stmt.finalize();
    // Seed packages
    db.run(`
      INSERT INTO packages (name, description, price)
      VALUES ('Coffee Box', 'Freshly roasted whole bean coffee delivered monthly.', 19.99)
    `);
    db.run(`
      INSERT INTO packages (name, description, price)
      VALUES ('Tea Box', 'Selection of premium loose leaf teas from around the world.', 14.99)
    `);
    db.run(`
      INSERT INTO packages (name, description, price)
      VALUES ('Snack Box', 'Healthy organic snacks and dried fruits.', 24.99)
    `);
    // Seed subscription
    db.run(`
      INSERT INTO subscriptions (user_id, package_id, status)
      VALUES (1, 1, 'ACTIVE')
    `);
  });
}
initDb();
// Session store
const sessions: Record<string, { id: number; username: string; role: string }> = {};
function getSessionUser(req: Request) {
  const sessionId = req.cookies.session_id;
  if (!sessionId || !sessions[sessionId]) {
    return null;
  }
  return sessions[sessionId];
}
function requireAuth(req: Request, res: Response, next: NextFunction) {
  const user = getSessionUser(req);
  if (!user) {
    return res.status(401).json({ error: 'Unauthorized: Authentication required.' });
  }
  next();
}
app.post('/api/user/profile', requireAuth, (req: Request, res: Response) => {
  const user = getSessionUser(req)!;
  const { email } = req.body;
  console.log(`[SECURITY AUDIT] User ID ${user.id} updated profile details at ${new Date().toISOString()}`);
  res.json({ message: 'Profile updated successfully.' });
});
// Authentication routes
app.post('/api/auth/register', (req: Request, res: Response) => {
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
app.post('/api/auth/login', (req: Request, res: Response) => {
  const { username, password } = req.body;
  const hash = crypto.createHash('md5').update(password || '').digest('hex');
  db.get('SELECT * FROM users WHERE username = ?', [username], (err, user: User) => {
    if (err || !user) {
      return res.status(401).json({ error: 'Invalid credentials.' });
    }
    if (user.password_hash !== hash) {
      return res.status(401).json({ error: 'Invalid credentials.' });
    }
    const sessionId = crypto.randomBytes(16).toString('hex');
    sessions[sessionId] = { id: user.id, username: user.username, role: user.role };
    res.cookie('session_id', sessionId, { httpOnly: true });
    res.json({ message: 'Login successful.', role: user.role });
  });
});
app.post('/api/auth/logout', (req: Request, res: Response) => {
  const sessionId = req.cookies.session_id;
  if (sessionId) {
    delete sessions[sessionId];
  }
  res.clearCookie('session_id');
  res.json({ message: 'Logged out successfully.' });
});
app.get('/api/packages/search', (req: Request, res: Response) => {
  const queryParam = req.query.q || '';
  const sql = `SELECT * FROM packages WHERE name LIKE '%${queryParam}%' OR description LIKE '%${queryParam}%'`;
  db.all(sql, (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Package search failed.', details: err.message });
    }
    res.json(rows);
  });
});
app.get('/api/packages/:id', (req: Request, res: Response) => {
  db.get('SELECT * FROM packages WHERE id = ?', [req.params.id], (err, row) => {
    if (err || !row) {
      return res.status(404).json({ error: 'Package not found.' });
    }
    res.json(row);
  });
});
app.post('/api/subscriptions/update', requireAuth, (req: Request, res: Response) => {
  const { subscriptionId, status } = req.body;
  const user = getSessionUser(req)!;
  if (!subscriptionId || !status) {
    return res.status(400).json({ error: 'Subscription ID and status are required.' });
  }
  // Ensure customer edits their own or admin edits any
  db.get('SELECT * FROM subscriptions WHERE id = ?', [subscriptionId], (err, row: any) => {
    if (err || !row) {
      return res.status(404).json({ error: 'Subscription not found.' });
    }
    if (row.user_id !== user.id && user.role !== 'ADMIN') {
      return res.status(403).json({ error: 'Forbidden: Cannot modify other users subscriptions.' });
    }
    db.run(
      'UPDATE subscriptions SET status = ? WHERE id = ?',
      [status, subscriptionId],
      (updateErr) => {
        if (updateErr) {
          return res.status(500).json({ error: 'Failed to update subscription status.' });
        }
        res.json({ message: 'Subscription status updated.', subscriptionId, status });
      }
    );
  });
});
app.listen(port, () => {
  console.log(`Subscription Box app listening at http://localhost:${port}`);
});
