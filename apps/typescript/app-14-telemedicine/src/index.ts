import { createApp } from "./app";
import { appConfig } from "./config/appConfig";

const app = createApp();

app.listen(appConfig.port, () => {
  console.log(`Telemedicine app listening on ${appConfig.port}`);
});
