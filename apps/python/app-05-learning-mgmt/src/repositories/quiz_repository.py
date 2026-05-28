from src.config.db_mongo import get_quiz_collection


class QuizRepository:
    def find_by_id(self, quiz_id):
        col = get_quiz_collection()
        if col is None:
            return None
        doc = col.find_one({"quiz_id": int(quiz_id)})
        if not doc:
            return None
        return {
            "quiz_id": doc["quiz_id"],
            "course_id": doc.get("course_id"),
            "title": doc.get("title", ""),
            "questions": doc.get("questions", []),
            "max_score": doc.get("max_score", 100),
        }
