import express, { Request, Response, NextFunction } from 'express';
import path from 'path';
import cookieParser from 'cookie-parser';
import cors from 'cors';

const app = express();
const PORT = process.env.PORT || 8013;

app.use(express.json());
app.use(cookieParser());
app.use(cors());

app.use(express.static(path.join(__dirname, '../public')));

// --- MOCK DATABASE ---
const db = {
    users: [
        { id: 1, username: 'alice', password: 'alice123', orgId: 101, role: 'MANAGER' },
        { id: 2, username: 'bob', password: 'bob123', orgId: 101, role: 'MEMBER' },
        { id: 3, username: 'charlie', password: 'charlie123', orgId: 202, role: 'MANAGER' }
    ],
    boards: [
        { id: 1, title: 'Q3 Product Launch', orgId: 101, visibility: 'INTERNAL' },
        { id: 2, title: 'Marketing Site Redesign', orgId: 101, visibility: 'PUBLIC' },
        { id: 3, title: 'Secret Project X (Confidential)', orgId: 202, visibility: 'PRIVATE' }
    ],
    tasks: [
        { id: 1, boardId: 1, title: 'Draft Press Release', description: 'Write the initial draft for the Q3 launch.' },
        { id: 2, boardId: 1, title: 'Finalize Assets', description: 'Get marketing assets approved by legal.' },
        { id: 3, boardId: 3, title: 'Acquisition Target Analysis', description: 'Review financials for target company.' }
    ]
};

// --- AUTH MIDDLEWARE ---
const requireAuth = (req: Request, res: Response, next: NextFunction) => {
    const sessionId = req.cookies.session_id;
    if (!sessionId) {
        return res.status(401).json({ message: 'Unauthenticated' });
    }
    const user = db.users.find(u => u.id.toString() === sessionId);
    if (!user) {
        return res.status(401).json({ message: 'Invalid session' });
    }
    (req as any).user = user;
    next();
};

// --- AUTH APIs ---
app.post('/api/auth/login', (req: Request, res: Response) => {
    const { username, password } = req.body;
    const user = db.users.find(u => u.username === username && u.password === password);
    
    if (user) {
        res.cookie('session_id', user.id.toString(), { httpOnly: true, sameSite: 'lax' });
        return res.json({ success: true, user: { username: user.username, orgId: user.orgId, role: user.role } });
    }
    return res.status(401).json({ success: false, message: 'Invalid credentials' });
});

app.post('/api/auth/logout', (req: Request, res: Response) => {
    res.clearCookie('session_id');
    return res.json({ success: true });
});

app.get('/api/auth/me', requireAuth, (req: Request, res: Response) => {
    const user = (req as any).user;
    return res.json({ username: user.username, orgId: user.orgId, role: user.role });
});

// --- BOARD APIs ---

// Get all boards for the user's organization
app.get('/api/boards', requireAuth, (req: Request, res: Response) => {
    const user = (req as any).user;
    const orgBoards = db.boards.filter(b => b.orgId === user.orgId);
    return res.json(orgBoards);
});

// OWASP VULNERABILITY A01: Broken Access Control (Insecure Direct Object Reference)
// This endpoint fetches the board entirely by ID. It completely fails to check if 
// the requested board belongs to the user's organization (user.orgId).
app.get('/api/boards/:id', requireAuth, (req: Request, res: Response) => {
    const boardId = parseInt(req.params.id);
    const board = db.boards.find(b => b.id === boardId);
    
    if (!board) {
        return res.status(404).json({ message: 'Board not found' });
    }
    
    // VULNERABLE: Missing check `if (board.orgId !== user.orgId) throw 403;`

    const boardTasks = db.tasks.filter(t => t.boardId === boardId);
    return res.json({ board, tasks: boardTasks });
});

// Create task
app.post('/api/boards/:id/tasks', requireAuth, (req: Request, res: Response) => {
    const boardId = parseInt(req.params.id);
    const { title, description } = req.body;
    
    const newTask = {
        id: db.tasks.length + 1,
        boardId,
        title,
        description
    };
    db.tasks.push(newTask);
    return res.status(201).json({ success: true, task: newTask });
});

// OWASP VULNERABILITY A09: Security Logging and Monitoring Failures
// This endpoint performs a highly sensitive action (modifying board access visibility)
// but fails to generate any audit logs, traces, or system alerts about the change.
app.put('/api/boards/:id/permissions', requireAuth, (req: Request, res: Response) => {
    const user = (req as any).user;
    const boardId = parseInt(req.params.id);
    const { visibility } = req.body;
    
    if (user.role !== 'MANAGER') {
        return res.status(403).json({ message: 'Requires MANAGER role' });
    }

    const board = db.boards.find(b => b.id === boardId);
    if (!board) {
        return res.status(404).json({ message: 'Board not found' });
    }

    // VULNERABLE: No audit log generated before or after this sensitive mutation.
    // E.g., Missing: logger.info(`User ${user.id} modified board ${board.id} visibility to ${visibility}`);
    
    board.visibility = visibility;

    return res.json({ success: true, board });
});

app.listen(PORT, () => {
    console.log(`Project Management API running on port ${PORT}`);
});
