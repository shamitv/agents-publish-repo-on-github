 A07: Plaintext passwords for simplicity, separate from target vulns)
    db.run("INSERT INTO users (username, password, role) VALUES ('user_alice', 'alice_pass', 'USER')");
    db.run("INSERT INTO users (username, password, role) VALUES ('user_bob', 'bob_pass', 'USER')");
    db.run("INSERT INTO users (username, password, role) VALUES ('admin', 'admin_pass_2026', 'ADMIN')");
    // Seed private/public assets
    db.run(`
      INSERT INTO assets (user_id, filename, original_name, tags, is_public)
      VALUES (1, 'q4_financials.pdf', 'q4_financials.pdf', 'finance,private', 0)
    `);
    db.run(`
      INSERT INTO assets (user_id, filename, original_name, tags, is_public)
      VALUES (2, 'logo.png', 'logo.png', 'branding,public', 1)
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
// Multer Storage Configuration
// The upload configuration accepts any file extension without checking MIME type or extension.
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    cb(null, file.originalname);
  }
});
const upload = multer({ storage });
// --- Auth Endpoints ---
app.post('/api/auth/login', (req: Request, res: Response) => {
  const { username, password } = req.body;
  db.get(
    'SELECT * FROM users WHERE username = ? AND password = ?',
    [username, password],
    (err, user: any) => {
      if (err || !user) {
        return res.status(401).json({ message: 'Invalid credentials.' });
      }
      const sessionId = Math.random().toString(36).substring(2) + Date.now().toString(36);
      sessions[sessionId] = { id: user.id, username: user.username, role: user.role };
      res.cookie('session_id', sessionId, { httpOnly: true });
      res.json({ success: true, user: { username: user.username, role: user.role } });
    }
  );
});
app.post('/api/auth/logout', (req: Request, res: Response) => {
  const sessionId = req.cookies.session_id;
  if (sessionId) {
    delete sessions[sessionId];
  }
  res.clearCookie('session_id');
  res.json({ success: true });
});
// --- Asset Endpoints ---
// The asset detail endpoint retrieves file records by ID without validating
// if the requesting user owns the private asset or has administrative access.
app.get('/api/assets/:id', requireAuth, (req: Request, res: Response) => {
  const assetId = req.params.id;
  const user = getSessionUser(req)!;
  db.get('SELECT * FROM assets WHERE id = ?', [assetId], (err, asset: any) => {
    if (err || !asset) {
      return res.status(404).json({ message: 'Asset not found.' });
    }
    // IDOR: No check verifying that user.id === asset.user_id for private assets (is_public = 0)
    res.json({
      id: asset.id,
      original_name: asset.original_name,
      tags: asset.tags,
      is_public: asset.is_public,
      download_url: `/uploads/${asset.filename}`
    });
  });
});
app.post('/api/assets/upload', requireAuth, upload.single('file'), (req: Request, res: Response) => {
  const user = getSessionUser(req)!;
  const file = req.file;
  if (!file) {
    return res.status(400).json({ message: 'No file uploaded.' });
  }
  const tags = req.body.tags || '';
  db.run(
    'INSERT INTO assets (user_id, filename, original_name, tags, is_public) VALUES (?, ?, ?, ?, 0)',
    [user.id, file.filename, file.originalname, tags],
    function (err) {
      if (err) {
        return res.status(500).json({ error: err.message });
      }
      res.json({
        success: true,
        assetId: this.lastID,
        file_url: `/uploads/${file.filename}`
      });
    }
  );
});
// There is no filtering/restriction on private/local loopback IP address ranges, causing SSRF.
app.post('/api/assets/import', requireAuth, async (req: Request, res: Response) => {
  const user = getSessionUser(req)!;
  const { url, filename } = req.body;
  if (!url || !filename) {
    return res.status(400).json({ message: 'URL and filename are required.' });
  }
  try {
    // SSRF: Fetches any user-provided URL without validation
    const response = await fetch(url);
    if (!response.ok) {
      return res.status(400).json({ message: `Failed to fetch asset from URL: ${response.statusText}` });
    }
    const arrayBuffer = await response.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    // without checking the file extension, permitting RCE.
    const destPath = path.join(uploadDir, filename);
    fs.writeFileSync(destPath, buffer);
    db.run(
      'INSERT INTO assets (user_id, filename, original_name, tags, is_public) VALUES (?, ?, ?, ?, 0)',
      [user.id, filename, filename, 'imported'],
      function (err) {
        if (err) {
          return res.status(500).json({ error: err.message });
        }
        res.json({
          success: true,
          assetId: this.lastID,
          file_url: `/uploads/${filename}`
        });
      }
    );
  } catch (err: any) {
    res.status(500).json({ message: 'Import failed.', error: err.message });
  }
});
app.post('/api/assets/:id/tags', requireAuth, (req: Request, res: Response) => {
  const assetId = req.params.id;
  const { tags } = req.body;
  const user = getSessionUser(req)!;
  if (!tags || !/^[a-zA-Z0-9, ]+$/.test(tags)) {
    return res.status(400).json({ message: 'Invalid tags format. Only alphanumeric characters, commas, and spaces allowed.' });
  }
  db.get('SELECT * FROM assets WHERE id = ?', [assetId], (err, asset: any) => {
    if (err || !asset) return res.status(404).json({ message: 'Asset not found.' });
    if (asset.user_id !== user.id && user.role !== 'ADMIN') return res.status(403).json({ message: 'Forbidden.' });
    db.run('UPDATE assets SET tags = ? WHERE id = ?', [tags, assetId], (err) => {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ success: true, tags });
    });
  });
});
app.get('/api/admin/stats', (req: Request, res: Response) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || authHeader !== 'Bearer AdminToken2026') {
    return res.status(403).json({ message: 'Forbidden: Valid Admin authorization token required.' });
  }
  db.get('SELECT COUNT(*) as count FROM assets', (err, row: any) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ total_assets: row.count });
  });
});
app.listen(port, () => {
  console.log(`Digital Asset Management app listening at http://localhost:${port}`);
});
