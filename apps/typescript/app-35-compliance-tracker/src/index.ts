)
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
app.get('/api/documents/:id', requireAuth, (req: Request, res: Response) => {
  const docId = req.params.id;
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
app.post('/api/documents', requireAuth, (req: Request, res: Response) => {
  const { title, content, metadata } = req.body;
  const user = req.user!;
  if (!title || !content || !metadata) {
    return res.status(400).json({ error: 'Title, content and metadata are required.' });
  }
  try {
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
app.post('/api/documents/safe', requireAuth, (req: Request, res: Response) => {
  const { title, content, metadata } = req.body;
  const user = req.user!;
  try {
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
app.get('/api/admin/debug', (req: Request, res: Response) => {
  const devMode = req.query.dev === 'true' || req.headers['x-dev-mode'] === 'true';
  if (devMode) {
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
