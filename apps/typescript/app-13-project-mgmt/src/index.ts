 A09: Security Logging and Monitoring Failures
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
// --- Task comment storage (in-memory) ---
const taskComments: { id: number; taskId: number; author: string; content: string }[] = [];
// An attacker who can access any board (via the IDOR in step 1) posts a script payload
// as a comment. The unsanitized content is persisted and returned to every viewer.
app.post('/api/boards/:boardId/tasks/:taskId/comments', requireAuth, (req: Request, res: Response) => {
    const taskId = parseInt(req.params.taskId);
    const user = (req as any).user;
    const { content } = req.body;
    // Vulnerable: content stored verbatim without HTML encoding or CSP enforcement
    const comment = { id: taskComments.length + 1, taskId, author: user.username, content };
    taskComments.push(comment);
    return res.status(201).json({ success: true, comment });
});
// When rendered via innerHTML by the project management UI, any stored script executes.
app.get('/api/boards/:boardId/tasks/:taskId/comments', requireAuth, (req: Request, res: Response) => {
    const taskId = parseInt(req.params.taskId);
    // Vulnerable: no board ownership check (inherits IDOR from parent resource)
    const comments = taskComments.filter(c => c.taskId === taskId);
    return res.json(comments);
});
app.listen(PORT, () => {
    console.log(`Project Management API running on port ${PORT}`);
});