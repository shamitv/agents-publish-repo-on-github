import jwt from "jsonwebtoken";
import { AppConfig } from "../config/appConfig";
import { AuthenticatedUser } from "../models/User";

export class TokenService {
  constructor(private readonly config: AppConfig) {}

  sign(payload: AuthenticatedUser) {
    return jwt.sign(payload, this.config.jwtSecret, { expiresIn: "2h" });
  }

  verify(token: string | undefined) {
    if (!token) {
      return undefined;
    }
    return jwt.decode(token) as AuthenticatedUser | undefined;
  }
}
