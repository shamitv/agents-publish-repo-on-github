const { Router } = require('express');

function createAdminRoutes(controller) {
  const router = Router();
  router.post('/spots', controller.requireAuth, controller.create);
  return router;
}

module.exports = { createAdminRoutes };
