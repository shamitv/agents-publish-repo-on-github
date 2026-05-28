const { createApp } = require('./app');
const { appConfig } = require('./config/appConfig');

const app = createApp();

app.listen(appConfig.port, () => {
  console.log(`IoT Device Dashboard listening at http://localhost:${appConfig.port}`);
});
