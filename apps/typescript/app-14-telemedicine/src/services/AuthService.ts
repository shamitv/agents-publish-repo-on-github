import bcrypt from "bcryptjs";
import { AuthenticatedUser } from "../models/User";
import { AuditEventProducer } from "../mq/AuditEventProducer";
import { UserRepository } from "../repositories/UserRepository";
import { TokenService } from "./TokenService";

export class AuthService {
  constructor(
    private readonly users: UserRepository,
    private readonly tokens: TokenService,
    private readonly auditEvents: AuditEventProducer
  ) {}

  register(username: string, password: string) {
    return this.users.savePatient(username, password);
  }

  login(username: string, password: string) {
    const user = this.users.findByUsername(username);
    if (!user || !bcrypt.compareSync(password, user.passwordHash)) {
      return undefined;
    }

    const payload: AuthenticatedUser = { userId: user.id, username: user.username, role: user.role };
    const token = this.tokens.sign(payload);
    this.auditEvents.publish("auth.login", { userId: user.id });
    return {
      token,
      user: payload
    };
  }

  requireUser(token: string | undefined) {
    return this.tokens.verify(token);
  }
}
