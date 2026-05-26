const { createApp } = require('./app');
const { appConfig } = require('./config/appConfig');

const app = createApp();

app.listen(appConfig.port, () => {
  console.log(`Parking Management System listening at http://localhost:${appConfig.port}`);
});
