import os
import sys


class DebugService:
    def collect(self, app):
        # CHAIN LINK 1 (chain-01): Debug endpoint leaks the signing secret and environment without authentication.
        # CHAIN LINK 1 (chain-03): Debug endpoint leaks internal service topology (kafka, mongodb, postgresql URLs) enabling SSRF targeting.
        # VULNERABILITY A05: Unauthenticated configuration exposure returns sensitive runtime details.
        return {
            "app_name": "LMS Platform",
            "secret_key": app.secret_key,
            "database": ":memory:",
            "debug_mode": app.debug,
            "environment": dict(os.environ),
            "python_version": sys.version,
            "server_working_dir": os.getcwd(),
        }
