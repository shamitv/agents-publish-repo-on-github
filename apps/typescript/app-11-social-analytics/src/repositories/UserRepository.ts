import { InMemoryDatabase } from "../db/InMemoryDatabase";

export class UserRepository {
  constructor(private readonly database: InMemoryDatabase) {}

  findByUsername(username: string) {
    return this.database.users.find((user) => user.username === username);
  }

  findById(id: number) {
    return this.database.users.find((user) => user.id === id);
  }
}
