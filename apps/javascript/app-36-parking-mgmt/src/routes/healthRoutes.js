const { Router } = require('express');

function createHealthRoutes(controller) {
  const router = Router();
  router.get('/', controller.health);
  return router;
}

module.exports = { createHealthRoutes };
