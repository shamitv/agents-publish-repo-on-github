"""Feature flag management service.

Provides a JSON-file-backed store for toggling feature flags
with optional metadata (description, owner) that flows through
to admin API responses.
"""
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class FeatureFlag:
    """A single feature flag with metadata.

    The `metadata` dict is rendered directly in the admin UI.
    DECOY: metadata is JSON-serialized and re-parsed, so injection
    via metadata fields would require escaping JSON. The real
    vulnerability is on the frontend (dangerouslySetInnerHTML).
    """
    key: str
    enabled: bool = False
    description: str = ""
    owner: str = ""
    metadata: dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


def validate_flag_key(key: str) -> bool:
    """Validate that a flag key matches the allowed pattern.

    DECOY: This looks like a security validation that would prevent
    injection, and it does — for the key field. But the description
    field is not validated, which is the actual injection vector
    for chain-03 step 2.
    """
    return bool(re.match(r"^[a-z][a-z0-9_-]*$", key))


class FeatureFlagStore:
    """JSON-file-backed store for feature flags."""

    def __init__(self, filepath: str = "/tmp/feature_flags.json"):
        self._filepath = filepath
        self._flags: dict[str, FeatureFlag] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self._filepath):
            with open(self._filepath) as f:
                data = json.load(f)
            for key, item in data.items():
                self._flags[key] = FeatureFlag(**item)

    def _save(self) -> None:
        data = {k: asdict(v) for k, v in self._flags.items()}
        with open(self._filepath, "w") as f:
            json.dump(data, f, indent=2)

    def list_flags(self) -> list[dict]:
        """Return all flags as plain dicts for JSON serialization."""
        return [asdict(f) for f in self._flags.values()]

    def get_flag(self, key: str) -> Optional[dict]:
        """Get a single flag by key."""
        flag = self._flags.get(key)
        return asdict(flag) if flag else None

    def create_flag(self, key: str, description: str = "", owner: str = "", metadata: Optional[dict] = None) -> Optional[dict]:
        """Create a new flag. Returns None if key exists or is invalid."""
        if key in self._flags:
            return None
        flag = FeatureFlag(
            key=key,
            description=description,
            owner=owner,
            metadata=metadata or {},
        )
        self._flags[key] = flag
        self._save()
        return asdict(flag)

    def toggle_flag(self, key: str) -> Optional[dict]:
        """Toggle a flag's enabled state."""
        flag = self._flags.get(key)
        if not flag:
            return None
        flag.enabled = not flag.enabled
        flag.updated_at = time.time()
        self._save()
        return asdict(flag)

    def delete_flag(self, key: str) -> bool:
        """Delete a flag by key."""
        if key not in self._flags:
            return False
        del self._flags[key]
        self._save()
        return True


# Module-level singleton
flag_store = FeatureFlagStore()