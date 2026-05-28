from src.config.db_sql import get_db_cursor


class GradeOverrideService:
    def override_grade(self, instructor_id, student_id, course_id, quiz_id, new_score):
        # CHAIN LINK 2 (chain-02): Grade override writes scores without course-ownership check and without audit log entries — tampering is undetectable
        with get_db_cursor() as cur:
            cur.execute(
                "INSERT INTO grades (user_id, course_id, quiz_id, score) VALUES (%s, %s, %s, %s) RETURNING id",
                (student_id, course_id, quiz_id, new_score),
            )
            new_id = cur.fetchone()["id"]
        # NOTE: No audit_log entry is written here
        return new_id
