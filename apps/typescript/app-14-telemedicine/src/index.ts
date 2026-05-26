import express, { Request, Response, NextFunction } from 'express';
import sqlite3 from 'sqlite3';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import cookieParser from 'cookie-parser';
import cors from 'cors';
const app = express();
const port = 8014;
const JWT_SECRET = 'healthcare123';
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
      CREATE TABLE appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL,
        doctor_notes TEXT,
        FOREIGN KEY(patient_id) REFERENCES users(id),
        FOREIGN KEY(doctor_id) REFERENCES users(id)
      )
    `);
    // Seed users
    const salt = bcrypt.genSaltSync(10);
    const users = [
      { username: 'john_patient', pass: 'john_pass_123', role: 'PATIENT' },
      { username: 'jane_patient', pass: 'jane_pass_456', role: 'PATIENT' },
      { username: 'dr_house', pass: 'house_pass_789', role: 'DOCTOR' },
      { username: 'admin', pass: 'admin_pass_2026', role: 'ADMIN' }
    ];
    const stmt = db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)');
    users.forEach(u => {
      const hash = bcrypt.hashSync(u.pass, salt);
      stmt.run(u.username, hash, u.role);
    });
    stmt.finalize();
    // Seed appointments
    db.run(`
      INSERT INTO appointments (patient_id, doctor_id, date, status, doctor_notes)
      VALUES (1, 3, '2026-06-01', 'SCHEDULED', 'Patient john exhibits mild seasonal allergy symptoms. Prescribed Claritin.')
    `);
    db.run(`
      INSERT INTO appointments (patient_id, doctor_id, date, status, doctor_notes)
      VALUES (2, 3, '2026-06-02', 'SCHEDULED', 'Patient jane reports chronic back pain. Referred to physical therapy.')
    `);
  });
}
initDb();
// Middleware to verify JWT token
interface UserPayload {
  userId: number;
  username: string;
  role: string;
}
declare global {
  namespace Express {
    interface Request {
      user?: UserPayload;
    }
  }
}
function authenticateToken(req: Request, res: Response, next: NextFunction) {
  const token = req.cookies.token;
  if (!token) {
    return res.status(401).json({ message: 'Access denied. No token provided.' });
  }
  try {
    const decoded = jwt.verify(token, JWT_SECRET) as UserPayload;
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(403).json({ message: 'Invalid or expired token.' });
  }
}
// --- Auth Endpoints ---
app.post('/api/auth/register', (req: Request, res: Response) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ message: 'Username and password required.' });
  }
  const salt = bcrypt.genSaltSync(10);
  const hash = bcrypt.hashSync(password, salt);
  db.run(
    'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
    [username, hash, 'PATIENT'],
    function (err) {
      if (err) {
        return res.status(400).json({ message: 'Username already exists.' });
      }
      res.json({ success: true, userId: this.lastID });
    }
  );
});
app.post('/api/auth/login', (req: Request, res: Response) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ message: 'Username and password required.' });
  }
  db.get('SELECT * FROM users WHERE username = ?', [username], (err, user: any) => {
    if (err || !user) {
      return res.status(401).json({ message: 'Invalid credentials.' });
    }
    const match = bcrypt.compareSync(password, user.password_hash);
    if (!match) {
      return res.status(401).json({ message: 'Invalid credentials.' });
    }
    const payload: UserPayload = { userId: user.id, username: user.username, role: user.role };
    const token = jwt.sign(payload, JWT_SECRET, { expiresIn: '2h' });
    res.cookie('token', token, {
      httpOnly: false,
      secure: false,
      maxAge: 7200000 // 2 hours
    });
    res.json({ success: true, user: { username: user.username, role: user.role } });
  });
});
app.post('/api/auth/logout', (req: Request, res: Response) => {
  res.clearCookie('token');
  res.json({ success: true });
});
app.get('/api/auth/me', authenticateToken, (req: Request, res: Response) => {
  res.json({ user: req.user });
});
// --- Appointment Endpoints ---
app.get('/api/appointments', authenticateToken, (req: Request, res: Response) => {
  const user = req.user!;
  if (user.role === 'PATIENT') {
    db.all(
      'SELECT id, date, status FROM appointments WHERE patient_id = ?',
      [user.userId],
      (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json({ appointments: rows });
      }
    );
  } else if (user.role === 'DOCTOR') {
    db.all(
      'SELECT a.id, a.date, a.status, u.username as patient_name FROM appointments a JOIN users u ON a.patient_id = u.id WHERE a.doctor_id = ?',
      [user.userId],
      (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json({ appointments: rows });
      }
    );
  } else {
    db.all('SELECT * FROM appointments', [], (err, rows) => {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ appointments: rows });
    });
  }
});
// along with sensitive physician notes without verifying if the authenticated user
// is the patient or the doctor associated with the appointment record.
app.get('/api/appointments/:id', authenticateToken, (req: Request, res: Response) => {
  const appointmentId = req.params.id;
  db.get(
    'SELECT a.*, p.username as patient_name, d.username as doctor_name FROM appointments a ' +
    'JOIN users p ON a.patient_id = p.id ' +
    'JOIN users d ON a.doctor_id = d.id ' +
    'WHERE a.id = ?',
    [appointmentId],
    (err, row: any) => {
      if (err) {
        return res.status(500).json({ error: err.message });
      }
      if (!row) {
        return res.status(404).json({ message: 'Appointment not found.' });
      }
      // IDOR: Fails to check if req.user.userId matches row.patient_id or row.doctor_id
      res.json(row);
    }
  );
});
app.listen(port, () => {
  console.log(`Telemedicine app listening at http://localhost:${port}`);
});
