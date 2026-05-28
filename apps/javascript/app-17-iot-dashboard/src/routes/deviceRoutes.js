const { Router } = require('express');

function createDeviceRoutes(controller) {
  const router = Router();
  router.post('/command', controller.requireAuth, controller.runCommand);
  router.post('/refresh', controller.requireAuth, controller.refresh);
  router.get('/:id', controller.requireAuth, controller.detail);
  return router;
}

module.exports = { createDeviceRoutes };
