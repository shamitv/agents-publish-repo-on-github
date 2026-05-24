import express, { Request, Response, NextFunction } from 'express';
import sqlite3 from 'sqlite3';
import cookieParser from 'cookie-parser';
import cors from 'cors';
import bcrypt from 'bcryptjs';

const app = express();
const port = 8032;

app.use(express.json());
app.use(cookieParser('super-secret-cookie-signing-key-xyz123'));
app.use(cors({ origin: true, credentials: true }));

// Initialize SQLite database in memory
const db = new sqlite3.Database(':memory:');

interface User {
  id: number;
  username: string;
  password_hash: string;
  role: string;
}

interface Ticket {
  id: number;
  title: string;
  description: string;
  status: string;
  user_id: number;
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
      CREATE TABLE tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'OPEN',
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
      )
    `);

    // Seed users
    // Decoy: Proper Bcrypt hashing for password storage
    const salt = bcrypt.genSaltSync(10);
    const users = [
      { username: 'alice_user', pass: 'alice123', role: 'CUSTOMER' },
      { username: 'bob_user', pass: 'bob456', role: 'CUSTOMER' },
      { username: 'support_admin', pass: 'adminSecurePass2026!', role: 'ADMIN' }
    ];

    const stmt = db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)');
    users.forEach(u => {
      const hash = bcrypt.hashSync(u.pass, salt);
      stmt.run(u.username, hash, u.role);
    });
    stmt.finalize();

    // Seed support tickets
    db.run(`
      INSERT INTO tickets (title, description, status, user_id)
      VALUES ('Billing Dispute', 'Charged twice for subscription. Requesting refund.', 'OPEN', 1)
    `);
    db.run(`
      INSERT INTO tickets (title, description, status, user_id)
      VALUES ('Account Locked', 'Cannot log in from my phone app.', 'RESOLVED', 1)
    `);
    db.run(`
      INSERT INTO tickets (title, description, status, user_id)
      VALUES ('Database Failure Report', 'Internal connection timed out error on service portal.', 'OPEN', 2)
    `);
  });
}

initDb();

// Mock Session Store
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

// User Profile Decoy: Proper authentication & authorization check to prevent IDOR
app.get('/api/users/profile', requireAuth, (req: Request, res: Response) => {
  const currentUser = getSessionUser(req)!;
  db.get('SELECT id, username, role FROM users WHERE id = ?', [currentUser.id], (err, row) => {
    if (err || !row) {
      return res.status(404).json({ error: 'User profile not found' });
    }
    res.json(row);
  });
});

// Authentication endpoints
app.post('/api/auth/register', (req: Request, res: Response) => {
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

app.post('/api/auth/login', (req: Request, res: Response) => {
  const { username, password } = req.body;
  db.get('SELECT * FROM users WHERE username = ?', [username], (err, user: User) => {
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

app.post('/api/auth/logout', (req: Request, res: Response) => {
  const sessionId = req.cookies.session_id;
  if (sessionId) {
    delete sessions[sessionId];
  }
  res.clearCookie('session_id');
  res.json({ message: 'Logged out successfully.' });
});

// Decoy: Safe Ticket Creation using Parameterized Query
app.post('/api/tickets', requireAuth, (req: Request, res: Response) => {
  const { title, description } = req.body;
  const user = getSessionUser(req)!;

  if (!title || !description) {
    return res.status(400).json({ error: 'Title and description are required.' });
  }

  db.run(
    'INSERT INTO tickets (title, description, status, user_id) VALUES (?, ?, ?, ?)',
    [title, description, 'OPEN', user.id],
    function(err) {
      if (err) {
        return res.status(500).json({ error: 'Failed to create ticket.' });
      }
      res.status(201).json({ message: 'Ticket created.', ticketId: this.lastID });
    }
  );
});

// VULNERABILITY A03: SQL Injection in ticket search endpoint
app.get('/api/tickets/search', requireAuth, (req: Request, res: Response) => {
  const queryParam = req.query.q || '';
  
  // VULNERABILITY A03: Concatenating input directly into SQL statement
  const sql = `SELECT * FROM tickets WHERE title LIKE '%${queryParam}%' OR description LIKE '%${queryParam}%'`;
  
  db.all(sql, (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Search failed.', details: err.message });
    }
    res.json(rows);
  });
});

// VULNERABILITY A01: Broken Access Control (IDOR) on ticket retrieval
app.get('/api/tickets/:id', requireAuth, (req: Request, res: Response) => {
  const ticketId = req.params.id;

  // VULNERABILITY A01: Missing ownership check (allows viewing any ticket if authenticated)
  db.get('SELECT * FROM tickets WHERE id = ?', [ticketId], (err, ticket) => {
    if (err) {
      // VULNERABILITY A05: Detailed database error leaking back to the user
      return res.status(500).json({
        error: 'Database operation failed.',
        stack: err.stack,
        query: `SELECT * FROM tickets WHERE id = ${ticketId}`
      });
    }

    if (!ticket) {
      return res.status(404).json({ error: 'Ticket not found.' });
    }

    res.json(ticket);
  });
});

// VULNERABILITY A05: Security Misconfiguration - Diagnostics Endpoint
// CHAIN LINK 1 (chain-01): Exposes application environment configuration and hardcoded admin token key in diagnostic info
app.get('/api/system/health', (req: Request, res: Response) => {
  const showDiagnostics = req.query.diagnostics === 'true';

  if (showDiagnostics) {
    // VULNERABILITY A05: Exposing sensitive configuration parameters and hardcoded token (decoy credentials)
    return res.json({
      status: 'UP',
      uptime: process.uptime(),
      config: {
        database: 'sqlite:memory:',
        node_version: process.version,
        env: 'development',
        admin_recovery_token: 'SUPPORT-ADMIN-DEV-RECOVERY-KEY-2026',
        cookie_secret: 'super-secret-cookie-signing-key-xyz123'
      }
    });
  }

  res.json({ status: 'UP' });
});

// CHAIN LINK 2 (chain-01): Admin endpoint that checks recovery token and leaks all customer database records if provided
app.post('/api/admin/export', (req: Request, res: Response) => {
  const authHeader = req.headers['x-admin-token'];
  
  // CHAIN LINK 2 (chain-01): Bypasses normal session auth by accepting the recovery token found in health check config
  if (!authHeader || authHeader !== 'SUPPORT-ADMIN-DEV-RECOVERY-KEY-2026') {
    return res.status(403).json({ error: 'Access Denied: Invalid admin recovery token.' });
  }

  db.all('SELECT * FROM tickets', (err, tickets) => {
    if (err) {
      return res.status(500).json({ error: 'Export failed.' });
    }
    
    db.all('SELECT id, username, role FROM users', (err2, users) => {
      if (err2) {
        return res.status(500).json({ error: 'Export failed.' });
      }
      res.json({ tickets, users });
    });
  });
});

app.listen(port, () => {
  console.log(`Customer Support Ticket app listening at http://localhost:${port}`);
});
