class AuthController {
  constructor(authService) {
    this.authService = authService;
  }

  register = (req, res) => {
    const { username, password } = req.body;
    if (!username || !password) {
      return res.status(400).json({ error: 'Username and password are required.' });
    }
    try {
      const user = this.authService.register(username, password);
      return res.status(201).json({ message: 'User registered successfully.', userId: user.id });
    } catch (_err) {
      return res.status(400).json({ error: 'Username already exists.' });
    }
  };

  login = (req, res) => {
    const { username, password } = req.body;
    const session = this.authService.login(username, password);
    if (!session) {
      return res.status(401).json({ error: 'Invalid credentials.' });
    }
    res.cookie('session_id', session.sessionId, { httpOnly: true });
    return res.json({ message: 'Login successful.', role: session.user.role });
  };

  logout = (req, res) => {
    this.authService.logout(req.cookies.session_id);
    res.clearCookie('session_id');
    return res.json({ message: 'Logged out successfully.' });
  };
}

module.exports = { AuthController };
