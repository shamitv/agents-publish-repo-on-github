import json
import unittest
from pathlib import Path

from app import app


ROOT = Path(__file__).resolve().parents[1]


class App05ModularContractTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_core_endpoints_still_work(self):
        self.assertEqual(self.client.get("/api/health").status_code, 200)
        self.assertEqual(self.client.get("/api/courses").status_code, 200)
        login = self.client.post("/api/auth/login", json={"username": "student_alice", "password": "alice_pass_123"})
        self.assertEqual(login.status_code, 200)
        self.assertEqual(self.client.get("/api/submissions/2").status_code, 200)

    def test_entrypoint_is_bootstrap_only(self):
        entrypoint = (ROOT / "app.py").read_text()
        self.assertLessEqual(len(entrypoint.splitlines()), 12)
        self.assertNotIn("@app.route", entrypoint)
        self.assertNotIn("CREATE TABLE", entrypoint)

    def test_benchmark_annotations_are_present(self):
        source = "\n".join(path.read_text() for path in (ROOT / "src").rglob("*.py"))
        checked = [
            "VULNERABILITY A01", "VULNERABILITY A05", "VULNERABILITY A08",
            "VULNERABILITY A04", "VULNERABILITY A09", "VULNERABILITY A10",
            "VULNERABILITY A07",
            "CHAIN LINK 1 (chain-01)", "CHAIN LINK 2 (chain-01)", "CHAIN LINK 3 (chain-01)",
            "CHAIN LINK 1 (chain-02)", "CHAIN LINK 2 (chain-02)",
            "CHAIN LINK 1 (chain-03)", "CHAIN LINK 2 (chain-03)",
        ]
        for annotation in checked:
            self.assertIn(annotation, source, f"Missing annotation: {annotation}")

    def test_vulnerability_manifest_is_valid(self):
        manifest = json.loads((ROOT / ".vulns").read_text())
        self.assertEqual(manifest["app_id"], "app-05")
        self.assertEqual(len(manifest["chained_attacks"]), 3)
        self.assertGreaterEqual(len(manifest["decoys"]), 7)


if __name__ == "__main__":
    unittest.main()
