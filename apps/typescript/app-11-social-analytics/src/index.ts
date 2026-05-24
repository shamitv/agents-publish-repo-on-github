import express, { Request, Response } from 'express';
import path from 'path';
import cookieParser from 'cookie-parser';
import cors from 'cors';
import axios from 'axios';

const app = express();
const PORT = process.env.PORT || 8011;

// Middleware
app.use(express.json());
app.use(cookieParser());
app.use(cors());

// Serve static assets from public directory
app.use(express.static(path.join(__dirname, '../public')));

// --- MOCK DATABASE ---
const db = {
    users: [
        { id: 1, username: 'alice', password: 'alice123', role: 'MARKETER' },
        { id: 2, username: 'bob', password: 'bob123', role: 'MARKETER' }
    ],
    widgets: [
        { id: 1, userId: 1, title: 'Total Engagement', type: 'metric', value: '45,230' },
        { id: 2, userId: 1, title: 'Campaign Reach', type: 'chart', value: '1.2M' },
        { id: 3, userId: 2, title: 'Follower Growth', type: 'metric', value: '+12%' }
    ]
};

// --- AUTH APIs ---
app.post('/api/auth/login', (req: Request, res: Response) => {
    const { username, password } = req.body;
    const user = db.users.find(u => u.username === username && u.password === password);
    
    if (user) {
        res.cookie('session_id', user.id.toString(), {
            httpOnly: true,
            sameSite: 'lax'
        });
        return res.json({ success: true, user: { username: user.username, role: user.role } });
    }
    return res.status(401).json({ success: false, message: 'Invalid credentials' });
});

app.post('/api/auth/logout', (req: Request, res: Response) => {
    res.clearCookie('session_id');
    return res.json({ success: true });
});

app.get('/api/auth/me', (req: Request, res: Response) => {
    const sessionId = req.cookies.session_id;
    if (!sessionId) {
        return res.status(401).json({ message: 'Unauthenticated' });
    }
    const user = db.users.find(u => u.id.toString() === sessionId);
    if (user) {
        return res.json({ username: user.username, role: user.role });
    }
    return res.status(401).json({ message: 'Unauthenticated' });
});

// --- WIDGET APIs (Vulnerable to XSS on frontend) ---
app.get('/api/widgets', (req: Request, res: Response) => {
    const sessionId = req.cookies.session_id;
    if (!sessionId) {
        return res.status(401).json({ message: 'Unauthenticated' });
    }
    const userWidgets = db.widgets.filter(w => w.userId.toString() === sessionId);
    return res.json(userWidgets);
});

app.post('/api/widgets', (req: Request, res: Response) => {
    const sessionId = req.cookies.session_id;
    if (!sessionId) {
        return res.status(401).json({ message: 'Unauthenticated' });
    }
    const { title, type, value } = req.body;
    
    const newWidget = {
        id: db.widgets.length + 1,
        userId: parseInt(sessionId),
        title,
        type,
        value
    };
    db.widgets.push(newWidget);
    return res.json({ success: true, widget: newWidget });
});

// --- OWASP VULNERABILITY A10: Server-Side Request Forgery (SSRF) ---
app.post('/api/preview', async (req: Request, res: Response) => {
    const { url } = req.body;
    if (!url) {
        return res.status(400).json({ success: false, message: 'URL is required' });
    }

    try {
        // Vulnerability: Fetches remote asset bytes using axios without IP restrictions,
        // hostname validation, or DNS sandboxing. Permits probing localhost/private subnet nodes.
        const response = await axios.get(url, { timeout: 3000 });
        
        // CHAIN LINK 2 (chain-01): Full response body returned without truncation.
        // Previously limited to 500 chars; removing the cap allows complete exfiltration
        // of cloud metadata API responses (e.g. AWS IMDSv1 returns hundreds of bytes of
        // IAM credentials that would have been cut off at 500 chars).
        return res.json({
            success: true,
            status_code: response.status,
            content_type: response.headers['content-type'],
            data_preview: typeof response.data === 'string' ? response.data : JSON.stringify(response.data)
        });
    } catch (error: any) {
        return res.status(400).json({ 
            success: false, 
            error: error.message 
        });
    }
});

// CHAIN LINK 3 (chain-01): Debug endpoint returns all incoming request headers verbatim,
// including Authorization tokens or internal proxy headers forwarded from the SSRF probe.
// When the SSRF reaches the cloud metadata service, the response headers contain
// metadata that can be retrieved here to cross-correlate internal routing.
app.get('/api/debug/headers', (req: Request, res: Response) => {
    return res.json({ headers: req.headers });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
