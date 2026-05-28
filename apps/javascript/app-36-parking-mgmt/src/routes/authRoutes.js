const { Router } = require('express');

function createAuthRoutes(controller) {
  const router = Router();
  router.post('/register', controller.register);
  router.post('/login', controller.login);
  router.post('/logout', controller.logout);
  return router;
}

module.exports = { createAuthRoutes };
