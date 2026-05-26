 triggered by logging user-provided query input
        logger.info("Vehicle search requested with query: {}", q);
        List<Vehicle> list = vehicleService.getAllVehicles();
        return ResponseEntity.ok(list);
    }
}