const { Router } = require('express');

function createSpotRoutes(controller) {
  const router = Router();
  router.get('/search', controller.search);
  router.get('/:id', controller.detail);
  return router;
}

module.exports = { createSpotRoutes };
