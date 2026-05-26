from src.config.kafka_client import event_publisher
from src.repositories.submission_repository import SubmissionRepository
from src.workers.grading_listener import GradingListener


class SubmissionService:
    def __init__(self, submissions=None, publisher=None):
        self.submissions = submissions or SubmissionRepository()
        self.publisher = publisher or event_publisher
        self.grading = GradingListener()

    def get_submission(self, submission_id):
        # CHAIN LINK 3 (chain-01): Forged sessions can read any submission because ownership is not checked.
        # VULNERABILITY A01: Submission lookup does not verify the current session owns the record.
        row = self.submissions.find_by_id(submission_id)
        if not row:
            return None
        return {
            "id": row["id"],
            "quiz_title": row["quiz_title"],
            "student_name": row["student_name"],
            "answers": row["answers"],
            "score": row["score"],
            "submitted_at": row["submitted_at"],
        }

    def submit(self, user_id, data):
        submission_id = self.submissions.create(data.get("quiz_id"), user_id, data.get("answers", ""))
        event = self.publisher.publish("grading", {"submission_id": submission_id})
        self.grading.process_submission(event)
        return submission_id

    def list_for_quiz(self, quiz_id):
        return [
            {"id": r["id"], "student": r["username"], "answers": r["answers"], "score": r["score"], "submitted_at": r["submitted_at"]}
            for r in self.submissions.list_for_quiz(quiz_id)
        ]
