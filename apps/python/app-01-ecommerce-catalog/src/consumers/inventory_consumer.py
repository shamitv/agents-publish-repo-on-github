class InventoryConsumer:
    def process_order_event(self, event):
        return {"inventory_status": "reserved", "event": event}
