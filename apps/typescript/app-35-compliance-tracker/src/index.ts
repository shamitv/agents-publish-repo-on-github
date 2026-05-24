import express, { Request, Response, NextFunction } from 'express';
import sqlite3 from 'sqlite3';
import cookieParser from 'cookie-parser';
import cors from 'cors';
import bcrypt from 'bcryptjs';

const app = express();
const port = 8035;

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
      CREATE TABLE documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        metadata TEXT,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
      )
    `);

    // Seed users
    // Decoy: Proper Bcrypt hashing for password storage
    const salt = bcrypt.genSaltSync(10);
    const users = [
      { username: 'alice_compliance', pass: 'alicepassword', role: 'CUSTOMER' },
      { username: 'bob_compliance', pass: 'bobpassword', role: 'CUSTOMER' },
      { username: 'admin_compliance', pass: 'adminpassword2026!', role: 'ADMIN' }
    ];

    const stmt = db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)');
    users.forEach(u => {
      const hash = bcrypt.hashSync(u.pass, salt);
      stmt.run(u.username, hash, u.role);
    });
    stmt.finalize();

    // Seed documents
    db.run(`
      INSERT INTO documents (title, content, metadata, user_id)
      VALUES ('Alice Annual Tax Compliance Report', 'Highly sensitive tax information and business revenue records.', '{"verified": true}', 1)
    `);
    db.run(`
      INSERT INTO documents (title, content, metadata, user_id)
      VALUES ('Bob Employee Handbook Agreement', 'Verification that Bob has agreed to company policy and safety guidelines.', '{"verified": true}', 2)
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

// Authentication middleware
function requireAuth(req: Request, res: Response, next: NextFunction) {
  const sessionUser = getSessionUser(req);
  if (sessionUser) {
    req.user = sessionUser;
    return next();
  }

  // Fallback to dev mode API token check (chain link)
  const token = req.headers['x-admin-token'];
  if (token && token === 'ADMIN-DEV-TOKEN-KEY-8871') {
    req.user = { id: 3, username: 'admin_compliance', role: 'ADMIN' };
    return next();
  }

  return res.status(401).json({ error: 'Unauthorized: Authentication required.' });
}

// Extend Express Request interface
declare global {
  namespace Express {
    interface Request {
      user?: { id: number; username: string; role: string };
    }
  }
}

// Profile Decoy: Proper secure endpoint with validation checks
app.get('/api/users/me', requireAuth, (req: Request, res: Response) => {
  res.json({ id: req.user!.id, username: req.user!.username, role: req.user!.role });
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

// VULNERABILITY A01: Broken Access Control (IDOR) on document details retrieval
app.get('/api/documents/:id', requireAuth, (req: Request, res: Response) => {
  const docId = req.params.id;

  // VULNERABILITY A01: Retrieves document record directly without ensuring ownership
  db.get('SELECT * FROM documents WHERE id = ?', [docId], (err, document) => {
    if (err) {
      return res.status(500).json({ error: 'Database error.' });
    }
    if (!document) {
      return res.status(404).json({ error: 'Document not found.' });
    }
    res.json(document);
  });
});

// VULNERABILITY A08: Software and Data Integrity Failures - Insecure Deserialization
app.post('/api/documents', requireAuth, (req: Request, res: Response) => {
  const { title, content, metadata } = req.body;
  const user = req.user!;

  if (!title || !content || !metadata) {
    return res.status(400).json({ error: 'Title, content and metadata are required.' });
  }

  try {
    // VULNERABILITY A08: Using eval() to deserialize metadata, leading to potential RCE
    const metaObj = eval(`(${metadata})`);
    const metaString = JSON.stringify(metaObj);

    db.run(
      'INSERT INTO documents (title, content, metadata, user_id) VALUES (?, ?, ?, ?)',
      [title, content, metaString, user.id],
      function(err) {
        if (err) {
          return res.status(500).json({ error: 'Failed to save document.' });
        }
        res.status(201).json({ message: 'Document saved successfully.', docId: this.lastID });
      }
    );
  } catch (err: any) {
    res.status(400).json({ error: 'Metadata deserialization failed.', details: err.message });
  }
});

// Decoy: Safe JSON parsing metadata endpoint
app.post('/api/documents/safe', requireAuth, (req: Request, res: Response) => {
  const { title, content, metadata } = req.body;
  const user = req.user!;

  try {
    // Decoy: Proper secure JSON parsing prevents deserialization flaws
    const metaObj = JSON.parse(metadata);
    const metaString = JSON.stringify(metaObj);

    db.run(
      'INSERT INTO documents (title, content, metadata, user_id) VALUES (?, ?, ?, ?)',
      [title, content, metaString, user.id],
      function(err) {
        if (err) {
          return res.status(500).json({ error: 'Failed to save document.' });
        }
        res.status(201).json({ message: 'Document saved safely.', docId: this.lastID });
      }
    );
  } catch (err: any) {
    res.status(400).json({ error: 'Invalid JSON metadata format.' });
  }
});

// VULNERABILITY A05: Security Misconfiguration - Dev Mode Credentials Disclosure
// CHAIN LINK 1 (chain-01): Exposes sensitive administrative token if requested with dev mode parameters
app.get('/api/admin/debug', (req: Request, res: Response) => {
  const devMode = req.query.dev === 'true' || req.headers['x-dev-mode'] === 'true';

  if (devMode) {
    // VULNERABILITY A05: Security misconfiguration disclosing environment details and access keys
    return res.json({
      environment: 'development',
      database: 'sqlite:memory:',
      admin_token: 'ADMIN-DEV-TOKEN-KEY-8871',
      version: '1.0.0-beta'
    });
  }

  res.status(403).json({ error: 'Access Denied: Diagnostics only available in development mode.' });
});

app.listen(port, () => {
  console.log(`Compliance Document Tracker listening at http://localhost:${port}`);
});
