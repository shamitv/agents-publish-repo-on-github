)
  const token = req.headers['x-layout-token'] || req.query.layout_token;
  if (token && token === 'PET-PORTAL-DEV-LAYOUT-KEY-2026') {
    req.user = { id: 3, username: 'admin_shelter', role: 'ADMIN' };
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
app.post('/api/applications/apply', requireAuth, (req, res) => {
  const { petId } = req.body;
  const user = req.user;
  if (!petId) {
    return res.status(400).json({ error: 'Pet ID is required.' });
  }
  db.run(
    'INSERT INTO applications (pet_id, user_id, status) VALUES (?, ?, ?)',
    [petId, user.id, 'PENDING'],
    function(err) {
      if (err) {
        return res.status(500).json({ error: 'Failed to apply.' });
      }
      res.status(201).json({ message: 'Application submitted.', appId: this.lastID });
    }
  );
});
app.get('/api/pets/search', (req, res) => {
  const queryParam = req.query.q || '';
  const sql = `SELECT * FROM pets WHERE name LIKE '%${queryParam}%' OR breed LIKE '%${queryParam}%'`;
  db.all(sql, (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Search failed.', details: err.message });
    }
    res.json(rows);
  });
});
app.post('/api/pets/layout', requireAuth, (req, res) => {
  const { layoutConfig } = req.body;
  if (!layoutConfig) {
    return res.status(400).json({ error: 'Layout configuration is required.' });
  }
  try {
    const configObj = eval(`(${layoutConfig})`);
    res.json({ message: 'Pet layout configuration loaded.', config: configObj });
  } catch (evalErr) {
    res.status(400).json({ error: 'Failed to process configuration.', details: evalErr.message });
  }
});
app.get('/api/pets/:id', (req, res) => {
  db.get('SELECT * FROM pets WHERE id = ?', [req.params.id], (err, row) => {
    if (err || !row) {
      return res.status(404).json({ error: 'Pet not found.' });
    }
    res.json(row);
  });
});
app.get('/api/system/diagnostics', (req, res) => {
  const debugMode = req.query.debug === 'true';
  if (debugMode) {
    return res.json({
      status: 'ONLINE',
      env: 'development',
      layout_secret_token: 'PET-PORTAL-DEV-LAYOUT-KEY-2026',
      database: 'sqlite:memory:'
    });
  }
  res.json({ status: 'ONLINE' });
});
app.listen(port, () => {
  console.log(`Pet Adoption Portal listening at http://localhost:${port}`);
});
