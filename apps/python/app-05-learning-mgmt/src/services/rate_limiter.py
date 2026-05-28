import time


class RateLimiter:
    def __init__(self, max_attempts=3, window_seconds=300):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._entries = {}

    def check_rate_limit(self, user_id, quiz_id):
        key = (int(user_id), int(quiz_id) if quiz_id else 0)
        now = time.time()
        if key not in self._entries:
            self._entries[key] = []
        self._entries[key] = [t for t in self._entries[key] if now - t < self.window_seconds]
        if len(self._entries[key]) >= self.max_attempts:
            return False
        self._entries[key].append(now)
        return True


rate_limiter = RateLimiter()
