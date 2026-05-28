from src.config.db_mongo import get_submission_collection


class SubmissionRepository:
    def find_by_id(self, submission_id):
        col = get_submission_collection()
        if col is None:
            return None
        doc = col.find_one({"submission_id": int(submission_id)})
        if not doc:
            return None
        return {
            "id": doc["submission_id"],
            "quiz_title": doc.get("quiz_title", ""),
            "student_name": doc.get("student_name", ""),
            "answers": doc.get("answers", ""),
            "score": doc.get("score"),
            "submitted_at": str(doc.get("submitted_at", "")),
        }

    def create(self, quiz_id, student_id, answers_name=""):
        col = get_submission_collection()
        if col is None:
            return None
        max_doc = col.find_one(sort=[("submission_id", -1)])
        next_id = (max_doc["submission_id"] + 1) if max_doc else 1
        col.insert_one({
            "submission_id": next_id,
            "quiz_id": int(quiz_id) if quiz_id else None,
            "user_id": int(student_id),
            "answers": answers_name,
            "score": None,
            "submitted_at": __import__("datetime").datetime.utcnow(),
        })
        return next_id

    def list_for_quiz(self, quiz_id):
        col = get_submission_collection()
        if col is None:
            return []
        docs = col.find({"quiz_id": int(quiz_id)})
        return [
            {
                "id": d["submission_id"],
                "username": d.get("student_name", ""),
                "answers": d.get("answers", ""),
                "score": d.get("score"),
                "submitted_at": str(d.get("submitted_at", "")),
            }
            for d in docs
        ]

    def update_score(self, submission_id, score):
        col = get_submission_collection()
        if col is None:
            return
        col.update_one(
            {"submission_id": int(submission_id)},
            {"$set": {"score": score}},
        )
