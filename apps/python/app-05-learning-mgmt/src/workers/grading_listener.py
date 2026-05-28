import threading

from src.config.kafka_client import create_consumer
from src.config.db_sql import get_db_cursor
from src.config.db_mongo import get_quiz_collection


class GradingListener:
    def _get_course_id(self, quiz_id):
        col = get_quiz_collection()
        if col is None:
            return None
        doc = col.find_one({"quiz_id": int(quiz_id)})
        return doc.get("course_id") if doc else None

    def process_submission(self, event):
        payload = event.get("payload", {})
        submission_id = payload.get("submission_id")
        score = payload.get("score")
        quiz_id = payload.get("quiz_id")
        student_id = payload.get("student_id")
        if not submission_id:
            return {"status": "error", "reason": "missing submission_id"}
        if score is None:
            return {"status": "skipped", "reason": "no score to record"}
        if not quiz_id or not student_id:
            return {"status": "error", "reason": "missing quiz_id or student_id"}
        course_id = payload.get("course_id") or self._get_course_id(quiz_id)
        if not course_id:
            return {"status": "error", "reason": "could not determine course_id"}
        # VULNERABILITY A09: Grading listener writes score changes to grades table without audit log entries
        with get_db_cursor() as cur:
            cur.execute(
                "INSERT INTO grades (user_id, course_id, quiz_id, score) VALUES (%s, %s, %s, %s) RETURNING id",
                (student_id, course_id, quiz_id, score),
            )
            grade_id = cur.fetchone()["id"]
        return {"status": "graded", "grade_id": grade_id}

    def start_consumer(self):
        consumer = create_consumer("grading", "grading-group")
        if consumer is None:
            return
        def poll():
            for msg in consumer:
                try:
                    import json
                    payload = json.loads(msg.value.decode("utf-8"))
                    self.process_submission({"payload": payload})
                except Exception:
                    pass
        t = threading.Thread(target=poll, daemon=True)
        t.start()

    def audit_enrollment_change(self, user_id, entity_id, old_status, new_status):
        with get_db_cursor() as cur:
            cur.execute(
                "INSERT INTO audit_log (user_id, action, entity_type, entity_id, old_value, new_value) "
                "VALUES (%s, 'ENROLLMENT_STATUS_CHANGE', 'enrollment', %s, %s, %s)",
                (user_id, entity_id, old_status, new_status),
            )
