import express, { Request, Response, NextFunction } from 'express';
import sqlite3 from 'sqlite3';
import cookieParser from 'cookie-parser';
import cors from 'cors';
import bcrypt from 'bcryptjs';
import multer from 'multer';
import AdmZip from 'adm-zip';
import path from 'path';
import fs from 'fs';
import crypto from 'crypto';
const app = express();
const port = 8033;
app.use(express.json());
app.use(cookieParser());
app.use(cors({ origin: true, credentials: true }));
// Setup multer in-memory storage for handling ZIP files
const upload = multer({ storage: multer.memoryStorage() });
// Initialize SQLite database
const db = new sqlite3.Database(':memory:');
interface User {
  id: number;
  username: string;
  password_hash: string;
  role: string;
}
interface Application {
  id: number;
  candidate_name: string;
  email: string;
  resume_text: string;
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
      CREATE TABLE applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_name TEXT NOT NULL,
        email TEXT NOT NULL,
        resume_text TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'PENDING',
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
      )
    `);
    // Seed users
    // Decoy: Proper Bcrypt hashing for password storage
    const salt = bcrypt.genSaltSync(10);
    const users = [
      { username: 'alice_candidate', pass: 'candidate123', role: 'CANDIDATE' },
      { username: 'bob_candidate', pass: 'candidate456', role: 'CANDIDATE' },
      { username: 'charlie_recruiter', pass: 'recruiter2026ATS!', role: 'RECRUITER' }
    ];
    const stmt = db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)');
    users.forEach(u => {
      const hash = bcrypt.hashSync(u.pass, salt);
      stmt.run(u.username, hash, u.role);
    });
    stmt.finalize();
    // Seed applications
    db.run(`
      INSERT INTO applications (candidate_name, email, resume_text, user_id)
      VALUES ('Alice Smith', 'alice@example.com', 'Senior Software Engineer with 6 years experience in Node.js and TypeScript.', 1)
    `);
    db.run(`
      INSERT INTO applications (candidate_name, email, resume_text, user_id)
      VALUES ('Bob Jones', 'bob@example.com', 'Junior Frontend Developer skilled in React, HTML, and CSS.', 2)
    `);
  });
}
initDb();
// Session Store
const sessions: Record<string, { id: number; username: string; role: string }> = {};
function getSessionUser(req: Request) {
  const sessionId = req.cookies.session_id;
  if (!sessionId || !sessions[sessionId]) {
    return null;
  }
  return sessions[sessionId];
}
// Authentication Middleware (Session or API Key)
function requireAuth(req: Request, res: Response, next: NextFunction) {
  const sessionUser = getSessionUser(req);
  if (sessionUser) {
    req.user = sessionUser;
    return next();
  }
  // Fallback to API Key auth
  const apiKey = req.headers['x-api-key'] || req.query.api_key;
  if (apiKey && typeof apiKey === 'string') {
    // Look up user based on MD5 key logic
    // MD5 is derived directly from user ID: md5(userId)
    db.all('SELECT id, username, role FROM users', (err, rows: User[]) => {
      if (err) return res.status(500).json({ error: 'Auth lookup failed.' });
      const matchedUser = rows.find(r => {
        const hash = crypto.createHash('md5').update(r.id.toString()).digest('hex');
        return hash === apiKey;
      });
      if (matchedUser) {
        req.user = { id: matchedUser.id, username: matchedUser.username, role: matchedUser.role };
        return next();
      }
      return res.status(401).json({ error: 'Unauthorized: Invalid API key.' });
    });
  } else {
    return res.status(401).json({ error: 'Unauthorized: Authentication required.' });
  }
}
// Extend Express Request interface to include user
declare global {
  namespace Express {
    interface Request {
      user?: { id: number; username: string; role: string };
    }
  }
}
// Decoy: Recruiter Dashboard Endpoint with strict role protection
app.get('/api/recruiter/dashboard', requireAuth, (req: Request, res: Response) => {
  if (req.user!.role !== 'RECRUITER') {
    return res.status(403).json({ error: 'Forbidden: Recruiter access only.' });
  }
  db.all('SELECT * FROM applications', (err, rows) => {
    res.json({ dashboard: 'ATS Recruiter Dashboard', applications: rows });
  });
});
// Decoy: Safe applicant list endpoint (no IDOR)
app.get('/api/applications/my', requireAuth, (req: Request, res: Response) => {
  db.all('SELECT * FROM applications WHERE user_id = ?', [req.user!.id], (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Failed to fetch applications.' });
    }
    res.json(rows);
  });
});
// Authentication routes
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
app.post('/api/auth/api-key', requireAuth, (req: Request, res: Response) => {
  const apiKey = crypto.createHash('md5').update(req.user!.id.toString()).digest('hex');
  res.json({ api_key: apiKey });
});
app.get('/api/applications/:id', requireAuth, (req: Request, res: Response) => {
  const appId = req.params.id;
  db.get('SELECT * FROM applications WHERE id = ?', [appId], (err, row) => {
    if (err) {
      return res.status(500).json({ error: 'Database query failed.' });
    }
    if (!row) {
      return res.status(404).json({ error: 'Application not found.' });
    }
    res.json(row);
  });
});
app.post('/api/applications/upload-portfolio', requireAuth, upload.single('portfolio'), (req: Request, res: Response) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No portfolio ZIP file uploaded.' });
  }
  // Ensure recruiter/admin privilege
  if (req.user!.role !== 'RECRUITER') {
    return res.status(403).json({ error: 'Forbidden: Admin portfolio ingestion only.' });
  }
  const uploadDir = path.join(__dirname, '../uploads');
  if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir, { recursive: true });
  }
  try {
    const zip = new AdmZip(req.file.buffer);
    const zipEntries = zip.getEntries();
    zipEntries.forEach(entry => {
      // Combines entryName directly without preventing directory traversal sequences (../)
      const targetPath = path.join(uploadDir, entry.entryName);
      // Ensure target subdirectories exist
      const dirName = path.dirname(targetPath);
      if (!fs.existsSync(dirName)) {
        fs.mkdirSync(dirName, { recursive: true });
      }
      if (!entry.isDirectory) {
        fs.writeFileSync(targetPath, entry.getData());
      }
    });
    res.json({ message: 'Portfolio files uploaded and extracted successfully.' });
  } catch (error: any) {
    res.status(500).json({ error: 'Zip extraction failed.', details: error.message });
  }
});
app.listen(port, () => {
  console.log(`ATS Recruitment app listening at http://localhost:${port}`);
});