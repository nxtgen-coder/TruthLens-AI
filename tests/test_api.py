"""
Integration tests for TruthLens AI Flask REST API endpoints.
"""

import unittest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as flask_app
import database

class TestAPI(unittest.TestCase):

    def setUp(self):
        self.app = flask_app.app.test_client()
        self.app.testing = True
        database.init_db()

    def test_health_check(self):
        res = self.app.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "healthy")

    def test_get_samples(self):
        res = self.app.get("/api/samples")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(len(data["samples"]), 2)

    def test_get_model_info(self):
        res = self.app.get("/api/model-info")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("accuracy", data["model_info"])

    def test_analyze_endpoint_success(self):
        payload = {
            "headline": "European Union Approves Landmark AI Regulation Act",
            "content": (
                "The European Parliament ratified comprehensive artificial intelligence standards on Wednesday. "
                "According to official statements released by regulatory representatives, the law mandates risk assessments."
            )
        }
        res = self.app.post("/api/analyze", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)
        self.assertIn("credibility_score", data["data"])
        self.assertIn("verdict", data["data"])
        self.assertIn("id", data["data"])

    def test_analyze_validation_empty(self):
        payload = {"headline": "", "content": ""}
        res = self.app.post("/api/analyze", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "error")

    def test_history_and_stats_endpoints(self):
        # Stats
        res_stats = self.app.get("/api/stats")
        self.assertEqual(res_stats.status_code, 200)
        stats = json.loads(res_stats.data)
        self.assertEqual(stats["status"], "success")
        
        # History
        res_hist = self.app.get("/api/history?page=1&per_page=5")
        self.assertEqual(res_hist.status_code, 200)
        hist = json.loads(res_hist.data)
        self.assertEqual(hist["status"], "success")
        self.assertIn("items", hist["data"])

    def test_share_endpoint(self):
        # First create an analysis
        payload = {
            "headline": "WHO Announces Progress in Global Malaria Prevention",
            "content": "According to the World Health Organization, vaccination programs demonstrated 75% efficacy."
        }
        res_analyze = self.app.post("/api/analyze", data=json.dumps(payload), content_type="application/json")
        data_analyze = json.loads(res_analyze.data)
        rec_id = data_analyze["data"]["id"]

        # Call share endpoint
        res_share = self.app.get(f"/api/share/{rec_id}")
        self.assertEqual(res_share.status_code, 200)
        data_share = json.loads(res_share.data)
        self.assertEqual(data_share["status"], "success")
        self.assertIn("share_title", data_share["data"])
        self.assertIn("share_text", data_share["data"])
        self.assertEqual(data_share["data"]["record"]["id"], rec_id)

if __name__ == "__main__":
    unittest.main()
