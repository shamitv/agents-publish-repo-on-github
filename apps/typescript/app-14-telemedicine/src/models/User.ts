export type UserRole = "PATIENT" | "DOCTOR" | "ADMIN";

export interface User {
  id: number;
  username: string;
  passwordHash: string;
  role: UserRole;
}

export interface AuthenticatedUser {
  userId: number;
  username: string;
  role: UserRole;
}
