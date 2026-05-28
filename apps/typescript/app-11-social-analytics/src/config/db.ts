import { Pool } from "pg";
import { appConfig } from "./appConfig";

let pool: Pool | null = null;

export function getPool(): Pool {
  if (!pool) {
    pool = new Pool({ connectionString: appConfig.databaseUrl });
  }
  return pool;
}

export async function waitForDb(): Promise<void> {
  const p = getPool();
  for (let i = 0; i < 30; i++) {
    try {
      await p.query("SELECT 1");
      return;
    } catch {
      await new Promise((r) => setTimeout(r, 2000));
    }
  }
  throw new Error("Database did not become ready within timeout");
}
