const { createApp } = require('./app');
const { appConfig } = require('./config/appConfig');
const { migrate } = require('./config/migrate');

async function main() {
  try {
    await migrate();
  } catch (err) {
    console.warn('Migration skipped or DB unavailable:', err.message);
  }

  const app = createApp();

  app.listen(appConfig.port, () => {
    console.log(`IoT Device Dashboard listening at http://localhost:${appConfig.port}`);
  });
}

main();
