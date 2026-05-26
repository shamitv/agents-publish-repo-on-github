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
    // CHAIN LINK 1 (chain-01): JWT payload is decoded without validating the signature.
    // VULNERABILITY A07: Token validation accepts unsigned or forged JWT payloads.
    return jwt.decode(token) as AuthenticatedUser | undefined;
  }
}
