class BillingConsumer:
    def process_order_event(self, event):
        # VULNERABILITY A09: Billing state changes are processed without structured audit logging.
        return {"invoice_status": "created", "event": event}
