const express = require('express');
const sqlite3 = require('sqlite3');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const app = express();
const port = 8019;
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
      CREATE TABLE posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        layout_metadata TEXT,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
      )
    `);
    db.run(`
      CREATE TABLE comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        author TEXT NOT NULL,
        comment_text TEXT NOT NULL,
        FOREIGN KEY(post_id) REFERENCES posts(id)
      )
    `);
    // Seed users
    const salt = bcrypt.genSaltSync(10);
    const users = [
      { username: 'alice_author', pass: 'author123', role: 'AUTHOR' },
      { username: 'bob_author', pass: 'author456', role: 'AUTHOR' },
      { username: 'admin_editor', pass: 'editor2026Secure!', role: 'ADMIN' }
    ];
    const stmt = db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)');
    users.forEach(u => {
      const hash = bcrypt.hashSync(u.pass, salt);
      stmt.run(u.username, hash, u.role);
    });
    stmt.finalize();
    // Seed post
    db.run(`
      INSERT INTO posts (title, content, layout_metadata, user_id)
      VALUES ('Welcome to Node CMS', 'This is a self-hosted content publishing engine.', '{"theme": "dark"}', 1)
    `);
    // Seed comment
    db.run(`
      INSERT INTO comments (post_id, author, comment_text)
      VALUES (1, 'Alice Guest', 'Love the clean UI layout!')
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
  const sessionUser = getSessionUser(req);
  if (sessionUser) {
    req.user = sessionUser;
    return next();
  }
  // Fallback to debug token verification (chain-01 connection)
  const token = req.headers['x-editor-token'] || req.query.editor_token;
  if (token && token === 'CMS-ADMIN-EDITOR-KEY-xyz9988') {
    req.user = { id: 3, username: 'admin_editor', role: 'ADMIN' };
    return next();
  }
  return res.status(401).json({ error: 'Unauthorized: Authentication required.' });
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
app.get('/api/posts/:id/comments', (req, res) => {
  const postId = req.params.id;
  db.all('SELECT * FROM comments WHERE post_id = ?', [postId], (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Failed to retrieve comments.' });
    }
    res.json(rows);
  });
});
app.post('/api/posts/:id/comments', (req, res) => {
  const postId = req.params.id;
  const { author, comment_text } = req.body;
  if (!author || !comment_text) {
    return res.status(400).json({ error: 'Author and comment text are required.' });
  }
  db.run(
    'INSERT INTO comments (post_id, author, comment_text) VALUES (?, ?, ?)',
    [postId, author, comment_text],
    function(err) {
      if (err) {
        return res.status(500).json({ error: 'Failed to save comment.' });
      }
      res.status(201).json({ message: 'Comment added.', commentId: this.lastID });
    }
  );
});
app.post('/api/posts', requireAuth, (req, res) => {
  const { title, content, layout_metadata } = req.body;
  const user = req.user;
  if (!title || !content || !layout_metadata) {
    return res.status(400).json({ error: 'Title, content and layout metadata are required.' });
  }
  try {
    const parsedMetadata = eval(`(${layout_metadata})`);
    const metaString = JSON.stringify(parsedMetadata);
    db.run(
      'INSERT INTO posts (title, content, layout_metadata, user_id) VALUES (?, ?, ?, ?)',
      [title, content, metaString, user.id],
      function(err) {
        if (err) {
          return res.status(500).json({ error: 'Failed to save post.' });
        }
        res.status(201).json({ message: 'Post created.', postId: this.lastID });
      }
    );
  } catch (evalErr) {
    res.status(400).json({ error: 'Failed to parse metadata configuration.', details: evalErr.message });
  }
});
// Decoy: Safe JSON parsing post creation route
app.post('/api/posts/safe', requireAuth, (req, res) => {
  const { title, content, layout_metadata } = req.body;
  const user = req.user;
  try {
    // Decoy: Safe JSON parser prevents code execution
    const parsed = JSON.parse(layout_metadata);
    const metaString = JSON.stringify(parsed);
    db.run(
      'INSERT INTO posts (title, content, layout_metadata, user_id) VALUES (?, ?, ?, ?)',
      [title, content, metaString, user.id],
      function(err) {
        res.status(201).json({ message: 'Post created safely.', postId: this.lastID });
      }
    );
  } catch (err) {
    res.status(400).json({ error: 'Invalid JSON config.' });
  }
});
// Decoy: Safe escaped post title lookup
app.get('/api/posts/:id', (req, res) => {
  db.get('SELECT * FROM posts WHERE id = ?', [req.params.id], (err, row) => {
    if (err || !row) {
      return res.status(404).json({ error: 'Post not found.' });
    }
    // Decoy: Escaping title to protect against XSS on this field
    const escapedTitle = row.title.replace(/</g, '&lt;').replace(/>/g, '&gt;');
    res.json({
      id: row.id,
      title: escapedTitle,
      content: row.content,
      layout_metadata: row.layout_metadata,
      user_id: row.user_id
    });
  });
});
app.get('/api/system/diagnostics', (req, res) => {
  const debugMode = req.query.debug === 'true';
  if (debugMode) {
    return res.json({
      status: 'ONLINE',
      system: 'NodeCMS Engine v1.0',
      database: 'sqlite:memory:',
      env: 'development',
      editor_token: 'CMS-ADMIN-EDITOR-KEY-xyz9988'
    });
  }
  res.json({ status: 'ONLINE' });
});
app.listen(port, () => {
  console.log(`CMS application listening at http://localhost:${port}`);
});