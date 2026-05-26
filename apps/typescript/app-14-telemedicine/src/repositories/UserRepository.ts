import bcrypt from "bcryptjs";
import { InMemoryMedicalDatabase } from "../db/InMemoryMedicalDatabase";
import { User } from "../models/User";

export class UserRepository {
  constructor(private readonly database: InMemoryMedicalDatabase) {}

  findByUsername(username: string) {
    return this.database.users.find((user) => user.username === username);
  }

  savePatient(username: string, password: string) {
    const user: User = {
      id: this.database.nextUserId(),
      username,
      passwordHash: bcrypt.hashSync(password, bcrypt.genSaltSync(10)),
      role: "PATIENT"
    };
    this.database.users.push(user);
    return user;
  }
}
