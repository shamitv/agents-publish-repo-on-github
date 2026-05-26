const { Router } = require('express');

function createInternalRoutes(controller) {
  const router = Router();
  router.get('/telemetry', controller.telemetry);
  return router;
}

module.exports = { createInternalRoutes };
