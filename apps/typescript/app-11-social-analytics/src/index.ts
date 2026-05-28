import { createApp } from "./app";
import { appConfig } from "./config/appConfig";
import { waitForDb } from "./config/db";
import { waitForRedis } from "./config/cache";

async function main() {
  await waitForDb();
  await waitForRedis();

  const app = createApp();

  app.listen(appConfig.port, () => {
    console.log(`Social analytics server listening on ${appConfig.port}`);
  });
}

main().catch((err) => {
  console.error("Failed to start server:", err);
  process.exit(1);
});
