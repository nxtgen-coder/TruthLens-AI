"""
Unit tests for TruthLens AI SQLite database operations.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

class TestDatabase(unittest.TestCase):

    def setUp(self):
        # Ensure fresh table
        database.init_db()

    def test_save_and_retrieve_analysis(self):
        mock_result = {
            "verdict": "Real",
            "prediction_label": "Likely Credible",
            "credibility_score": 88.5,
            "confidence": 92.0,
            "word_count": 45,
            "attributions": {
                "real_supporting_terms": [{"term": "officials", "impact": 0.4}],
                "fake_supporting_terms": []
            },
            "explanation_points": ["Formal journalistic terminology identified."],
            "linguistics": {
                "stylistic_risk_score": 10,
                "quote_count": 1
            }
        }
        
        record_id = database.save_analysis("Test Headline Clean Energy", "Test body copy here.", mock_result)
        self.assertIsInstance(record_id, int)
        self.assertGreater(record_id, 0)

        # Retrieve by id
        record = database.get_analysis_by_id(record_id)
        self.assertIsNotNone(record)
        self.assertEqual(record["headline"], "Test Headline Clean Energy")
        self.assertEqual(record["verdict"], "Real")
        self.assertEqual(record["credibility_score"], 88.5)

        # Retrieve history
        history = database.get_history(page=1, per_page=5, search_query="Clean Energy")
        self.assertGreaterEqual(history["total"], 1)
        found = any(item["id"] == record_id for item in history["items"])
        self.assertTrue(found)

        # Delete record
        deleted = database.delete_analysis(record_id)
        self.assertTrue(deleted)
        
        # Verify deleted
        rec_after = database.get_analysis_by_id(record_id)
        self.assertIsNone(rec_after)

    def test_statistics(self):
        stats = database.get_statistics()
        self.assertIn("total_analyses", stats)
        self.assertIn("real_count", stats)
        self.assertIn("fake_count", stats)
        self.assertIn("score_distribution", stats)

if __name__ == "__main__":
    unittest.main()
