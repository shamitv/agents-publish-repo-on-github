import unittest
from fastapi.testclient import TestClient
from app import app, db

class App03TestCase(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_seeding_complete(self):
        # Verify mongomock records populated
        user = db.users.find_one({"username": "alice"})
        self.assertIsNotNone(user)
        self.assertEqual(user["account_number"], "10002819")

    def test_login_successful_with_valid_creds(self):
        payload = {"username": "alice", "password": "alice123"}
        response = self.client.post("/api/auth/login", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["username"], "alice")

    def test_login_rejected_with_invalid_creds(self):
        payload = {"username": "alice", "password": "wrong_password"}
        response = self.client.post("/api/auth/login", json=payload)
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
