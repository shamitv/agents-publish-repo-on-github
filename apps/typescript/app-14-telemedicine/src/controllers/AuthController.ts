import { Request, Response } from "express";
import { AuthService } from "../services/AuthService";

export class AuthController {
  constructor(private readonly authService: AuthService) {}

  register = (req: Request, res: Response) => {
    const { username, password } = req.body;
    if (!username || !password) {
      return res.status(400).json({ message: "Username and password required." });
    }
    const user = this.authService.register(String(username), String(password));
    return res.json({ success: true, userId: user.id });
  };

  login = (req: Request, res: Response) => {
    const { username, password } = req.body;
    const session = this.authService.login(String(username ?? ""), String(password ?? ""));
    if (!session) {
      return res.status(401).json({ message: "Invalid credentials." });
    }

    res.cookie("token", session.token, {
      httpOnly: false,
      secure: false,
      maxAge: 7200000
    });
    return res.json({ success: true, user: session.user });
  };

  logout = (_req: Request, res: Response) => {
    res.clearCookie("token");
    return res.json({ success: true });
  };

  me = (req: Request, res: Response) => {
    const user = this.authService.requireUser(req.cookies?.token);
    if (!user) {
      return res.status(401).json({ message: "Access denied." });
    }
    return res.json({ user });
  };
}
