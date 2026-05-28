import { createApp } from "./app";
import { appConfig } from "./config/appConfig";
import { initializeDatabase } from "./db/migrate";

async function main() {
  await initializeDatabase();

  const app = createApp();

  app.listen(appConfig.port, () => {
    console.log(`Telemedicine app listening on ${appConfig.port}`);
  });
}

main().catch((err) => {
  console.error("Failed to start:", err);
  process.exit(1);
});
