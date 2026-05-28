from src.repositories.quiz_repository import QuizRepository


class GradingService:
    def __init__(self, quiz_repo=None):
        self.quizzes = quiz_repo or QuizRepository()

    def grade_submission(self, quiz_id, answers_text):
        quiz = self.quizzes.find_by_id(quiz_id)
        if not quiz:
            return {"score": 0, "max_score": 0, "per_question_results": [], "error": "Quiz not found"}
        questions = quiz.get("questions", [])
        max_score = quiz.get("max_score", len(questions))
        answers_list = [a.strip() for a in (answers_text or "").split(",")]
        results = []
        correct_count = 0
        for i, q in enumerate(questions):
            student_answer = answers_list[i] if i < len(answers_list) else ""
            correct_answer = q.get("answer", "")
            q_type = q.get("type", "multiple_choice")
            if q_type == "multiple_choice":
                is_correct = student_answer.upper() == correct_answer.upper()
            elif q_type == "free_text":
                is_correct = any(kw.lower() in student_answer.lower() for kw in (correct_answer or "").split())
            elif q_type == "code_snippet":
                is_correct = any(kw.lower() in student_answer.lower() for kw in (correct_answer or "").split())
            else:
                is_correct = False
            if is_correct:
                correct_count += 1
            results.append({
                "question_index": i,
                "student_answer": student_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
            })
        score_per_q = max_score / max(len(questions), 1)
        total_score = round(correct_count * score_per_q, 1)
        return {
            "score": total_score,
            "max_score": max_score,
            "correct_count": correct_count,
            "total_questions": len(questions),
            "per_question_results": results,
        }
