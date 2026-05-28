"""Simple in-process scheduler for recurring report jobs.

Provides schedule/unschedule/list operations with a background
thread that dispatches jobs at their configured intervals.
"""
from __future__ import annotations

import json
import os
import threading
import time
import re
from dataclasses import dataclass, field, asdict
from typing import Callable, Optional


@dataclass
class ScheduledJob:
    """A recurring job that runs on an interval."""
    job_id: str
    name: str
    interval_seconds: int
    task_type: str  # "report_generation", "cache_warmup", etc.
    params: dict = field(default_factory=dict)
    enabled: bool = True
    last_run: Optional[float] = None
    next_run: Optional[float] = None
    run_count: int = 0


# DECOY: Validates cron-like expressions — looks like it protects
# the scheduler from bad input but is never actually called
def validate_cron_expression(expr: str) -> bool:
    parts = expr.strip().split()
    if len(parts) != 5:
        return False
    for part in parts:
        if not re.match(r"^(\d+|\*|[\d,\-*/]+)$", part):
            return False
    return True


class Scheduler:
    """Minimal in-process scheduler. Not production-grade."""

    def __init__(self, filepath: str = "/tmp/scheduler_jobs.json"):
        self._filepath = filepath
        self._jobs: dict[str, ScheduledJob] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._load()

    def _load(self) -> None:
        if os.path.exists(self._filepath):
            with open(self._filepath) as f:
                data = json.load(f)
            for jid, item in data.items():
                self._jobs[jid] = ScheduledJob(**item)

    def _save(self) -> None:
        data = {jid: asdict(j) for jid, j in self._jobs.items()}
        with open(self._filepath, "w") as f:
            json.dump(data, f, indent=2)

    def list_jobs(self) -> list[dict]:
        return [asdict(j) for j in self._jobs.values()]

    def get_job(self, job_id: str) -> Optional[dict]:
        job = self._jobs.get(job_id)
        return asdict(job) if job else None

    def add_job(self, name: str, interval_seconds: int, task_type: str, params: Optional[dict] = None) -> dict:
        import uuid
        job_id = str(uuid.uuid4())[:8]
        now = time.time()
        job = ScheduledJob(
            job_id=job_id,
            name=name,
            interval_seconds=interval_seconds,
            task_type=task_type,
            params=params or {},
            next_run=now + interval_seconds,
        )
        self._jobs[job_id] = job
        self._save()
        return asdict(job)

    def delete_job(self, job_id: str) -> bool:
        if job_id not in self._jobs:
            return False
        del self._jobs[job_id]
        self._save()
        return True

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _run_loop(self) -> None:
        while self._running:
            now = time.time()
            for job in list(self._jobs.values()):
                if not job.enabled:
                    continue
                if job.next_run and now >= job.next_run:
                    self._dispatch(job)
                    job.last_run = now
                    job.run_count += 1
                    job.next_run = now + job.interval_seconds
                    self._save()
            time.sleep(1)

    def _dispatch(self, job: ScheduledJob) -> None:
        """Execute a job's task. Logs to stdout for now."""
        print(f"[Scheduler] Running job {job.job_id}: {job.name} ({job.task_type})")
        # In production this would dispatch via Celery or RQ
        if job.task_type == "report_generation":
            # Placeholder: trigger report generation
            pass
        elif job.task_type == "cache_warmup":
            # Placeholder: pre-warm report caches
            pass


# Module-level singleton
scheduler = Scheduler()