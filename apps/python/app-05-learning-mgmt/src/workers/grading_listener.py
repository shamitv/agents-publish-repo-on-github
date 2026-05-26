class GradingListener:
    def process_submission(self, event):
        return {"status": "queued", "event": event}
