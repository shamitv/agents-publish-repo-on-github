import express, { Request, Response, NextFunction } from 'express';
import sqlite3 from 'sqlite3';
import cookieParser from 'cookie-parser';
import cors from 'cors';
import bcrypt from 'bcryptjs';
const app = express();
const port = 8031;
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
      CREATE TABLE events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        date TEXT NOT NULL,
        price REAL NOT NULL,
        available_tickets INTEGER NOT NULL
      )
    `);
    db.run(`
      CREATE TABLE bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        event_id INTEGER NOT NULL,
        ticket_count INTEGER NOT NULL,
        total_paid REAL NOT NULL,
        booking_reference TEXT NOT NULL UNIQUE,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(event_id) REFERENCES events(id)
      )
    `);
    // Seed users
    const salt = bcrypt.genSaltSync(10);
    const users = [
      { username: 'alice_customer', pass: 'alice_pass_123', role: 'CUSTOMER' },
      { username: 'bob_customer', pass: 'bob_pass_456', role: 'CUSTOMER' },
      { username: 'admin', pass: 'admin_tickets_2026', role: 'ADMIN' }
    ];
    const stmt = db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)');
    users.forEach(u => {
      const hash = bcrypt.hashSync(u.pass, salt);
      stmt.run(u.username, hash, u.role);
    });
    stmt.finalize();
    // Seed events
    db.run(`
      INSERT INTO events (name, description, date, price, available_tickets)
      VALUES ('Rock Concert 2026', 'Live music concert by top rock bands.', '2026-07-15', 99.99, 100)
    `);
    db.run(`
      INSERT INTO events (name, description, date, price, available_tickets)
      VALUES ('Tech Conference 2026', 'Annual developers and engineers summit.', '2026-08-20', 250.00, 50)
    `);
    // Seed bookings
    db.run(`
      INSERT INTO bookings (user_id, event_id, ticket_count, total_paid, booking_reference)
      VALUES (1, 1, 2, 199.98, 'REF-8871')
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
    return res.status(401).json({ message: 'Unauthenticated.' });
  }
  next();
}
// --- Auth Endpoints ---
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
    // allow attackers to guess session tokens of other active users.
    const sessionId = Math.floor(Math.random() * 900000 + 100000).toString();
    sessions[sessionId] = { id: user.id, username: user.username, role: user.role };
    res.cookie('session_id', sessionId, { httpOnly: true });
    res.json({ success: true, user: { username: user.username, role: user.role } });
  });
});
app.post('/api/auth/logout', (req: Request, res: Response) => {
  const sessionId = req.cookies.session_id;
  if (sessionId && sessions[sessionId]) {
    delete sessions[sessionId];
  }
  res.clearCookie('session_id');
  res.json({ success: true });
});
// --- Event Endpoints ---
// permitting SQL injection to bypass visibility controls or dump internal database tables.
app.get('/api/events/search', (req: Request, res: Response) => {
  const q = req.query.q || '';
  const query = `SELECT * FROM events WHERE name LIKE '%${q}%' OR description LIKE '%${q}%'`;
  db.all(query, [], (err, rows) => {
    if (err) {
      return res.status(400).json({ error: err.message, query_executed: query });
    }
    res.json({ events: rows });
  });
});
app.get('/api/events/:id', (req: Request, res: Response) => {
  const eventId = req.params.id;
  db.get('SELECT * FROM events WHERE id = ?', [eventId], (err, row) => {
    if (err) return res.status(500).json({ error: err.message });
    if (!row) return res.status(404).json({ message: 'Event not found.' });
    res.json(row);
  });
});
// --- Booking Endpoints ---
// Booking endpoint does not implement double-spending validation checks, locks, or rate limiting.
// Attacker can trigger bulk automatic ticket bookings to hoard all remaining tickets and lock out other fans.
app.post('/api/tickets/book', requireAuth, (req: Request, res: Response) => {
  const user = getSessionUser(req)!;
  const { event_id, ticket_count } = req.body;
  if (!event_id || !ticket_count || ticket_count <= 0) {
    return res.status(400).json({ message: 'Invalid event ID or ticket count.' });
  }
  db.get('SELECT * FROM events WHERE id = ?', [event_id], (err, event: any) => {
    if (err || !event) {
      return res.status(404).json({ message: 'Event not found.' });
    }
    if (event.available_tickets < ticket_count) {
      return res.status(400).json({ message: 'Not enough tickets available.' });
    }
    const total_paid = event.price * ticket_count;
    const ref = `REF-${Math.floor(Math.random() * 9000 + 1000)}`;
    db.serialize(() => {
      // Insecure Design: No transaction block, locking mechanism, or rate limits on booking.
      db.run(
        'UPDATE events SET available_tickets = available_tickets - ? WHERE id = ?',
        [ticket_count, event_id]
      );
      db.run(
        'INSERT INTO bookings (user_id, event_id, ticket_count, total_paid, booking_reference) VALUES (?, ?, ?, ?, ?)',
        [user.id, event_id, ticket_count, total_paid, ref],
        function (err) {
          if (err) {
            return res.status(500).json({ error: err.message });
          }
          res.json({
            success: true,
            bookingId: this.lastID,
            booking_reference: ref,
            total_paid
          });
        }
      );
    });
  });
});
app.get('/api/bookings', requireAuth, (req: Request, res: Response) => {
  const user = getSessionUser(req)!;
  db.all(
    'SELECT b.*, e.name as event_name FROM bookings b JOIN events e ON b.event_id = e.id WHERE b.user_id = ?',
    [user.id],
    (err, rows) => {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ bookings: rows });
    }
  );
});
app.listen(port, () => {
  console.log(`Event Ticketing app listening at http://localhost:${port}`);
});
