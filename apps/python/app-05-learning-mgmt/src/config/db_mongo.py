import time

import pymongo
from pymongo import MongoClient

from src.config.settings import MONGO_URI


_client = None


def get_mongo_client(max_retries=15, delay=2):
    global _client
    if _client is not None:
        return _client
    for attempt in range(max_retries):
        try:
            _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            _client.admin.command("ping")
            return _client
        except pymongo.errors.ConnectionFailure:
            if attempt < max_retries - 1:
                time.sleep(delay)
            _client = None
    return None


def get_quiz_collection():
    client = get_mongo_client()
    if client is None:
        return None
    db = client.get_database()
    return db["quiz_definitions"]


def get_submission_collection():
    client = get_mongo_client()
    if client is None:
        return None
    db = client.get_database()
    return db["submissions"]


def init_mongo():
    client = get_mongo_client()
    if client is None:
        return False
    db = client.get_database()
    if "quiz_definitions" not in db.list_collection_names():
        db.create_collection("quiz_definitions")
        db["quiz_definitions"].create_index("quiz_id", unique=True)
        db["quiz_definitions"].create_index("course_id")
        db["quiz_definitions"].insert_many([
            {
                "quiz_id": 1,
                "course_id": 1,
                "title": "Midterm Exam: Network Security",
                "questions": [
                    {"type": "multiple_choice", "prompt": "What is a firewall?", "options": ["A", "B", "C", "D"], "answer": "A"},
                    {"type": "free_text", "prompt": "Define threat modeling.", "answer": "process of identifying threats"},
                ],
                "max_score": 100,
            },
            {
                "quiz_id": 2,
                "course_id": 2,
                "title": "Final Exam: Neural Networks",
                "questions": [
                    {"type": "multiple_choice", "prompt": "What is backpropagation?", "options": ["A", "B", "C", "D"], "answer": "B"},
                    {"type": "code_snippet", "prompt": "Write a linear layer in PyTorch.", "answer": "nn.Linear"},
                ],
                "max_score": 100,
            },
        ])
    if "submissions" not in db.list_collection_names():
        db.create_collection("submissions")
        db["submissions"].create_index("submission_id", unique=True)
        db["submissions"].insert_many([
            {"submission_id": 1, "quiz_id": 1, "user_id": 1, "student_name": "student_alice", "answers": "A,B,C,D,A,B,C,D,A,B", "score": 85, "submitted_at": __import__("datetime").datetime.utcnow()},
            {"submission_id": 2, "quiz_id": 1, "user_id": 2, "student_name": "student_bob", "answers": "A,A,C,D,B,B,C,A,A,B", "score": 72, "submitted_at": __import__("datetime").datetime.utcnow()},
        ])
    return True
