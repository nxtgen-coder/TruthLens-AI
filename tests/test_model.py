"""
Unit tests for TruthLens AI machine learning model and inference engine.
"""

import unittest
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.predictor import analyze_news, analyze_linguistics, get_engine

class TestModelPredictor(unittest.TestCase):

    def test_model_loaded(self):
        model, vectorizer, metrics = get_engine()
        self.assertIsNotNone(model)
        self.assertIsNotNone(vectorizer)
        self.assertIsNotNone(metrics)
        self.assertIn("accuracy", metrics)

    def test_credible_news_prediction(self):
        headline = "Department of Energy Announces $50 Million Grant for Clean Hydrogen Research"
        content = (
            "Federal officials and energy researchers confirmed on Wednesday that fifty million dollars in federal "
            "funding will support university laboratories developing green hydrogen infrastructure. According to the "
            "agency's spokesperson, the initiative seeks to lower industrial carbon emissions by 2030."
        )
        res = analyze_news(headline, content)
        
        self.assertEqual(res["verdict"], "Real")
        self.assertGreaterEqual(res["credibility_score"], 60.0)
        self.assertGreater(res["probability_real"], res["probability_fake"])
        self.assertIn("explanation_points", res)
        self.assertGreater(len(res["explanation_points"]), 0)
        self.assertIn("attributions", res)

    def test_fake_news_prediction(self):
        headline = "BOMBSHELL: Proof Aliens Control Secret World Government From Denver Airport!!!"
        content = (
            "WAKE UP SHEEPLE! Anonymous insiders leaked top secret files proving reptilian aliens operate underground "
            "bases beneath Denver airport and use 5G weapons to brainwash citizens! Big pharma is hiding the truth!"
        )
        res = analyze_news(headline, content)
        
        self.assertEqual(res["verdict"], "Fake")
        self.assertLess(res["credibility_score"], 50.0)
        self.assertGreater(res["probability_fake"], res["probability_real"])
        self.assertGreater(res["linguistics"]["sensational_punct_score"], 0)
        self.assertGreaterEqual(len(res["linguistics"]["caps_words_in_headline"]), 1)

    def test_linguistic_analysis(self):
        headline = "SHOCKING BOMBSHELL: Leaked Truth About Cures!"
        text = 'According to Dr. Smith, "This study published in Nature shows 15% improvement."'
        ling = analyze_linguistics(headline, text)
        
        self.assertIn("SHOCKING", ling["caps_words_in_headline"])
        self.assertIn("BOMBSHELL", ling["caps_words_in_headline"])
        self.assertGreater(ling["exclamation_count"], 0)
        self.assertGreater(ling["quote_count"], 0)
        self.assertIn("shocking", [m.lower() for m in ling["clickbait_terms_detected"]])
        self.assertIn("according to", [m.lower() for m in ling["attribution_terms_detected"]])

    def test_empty_input_validation(self):
        with self.assertRaises(ValueError):
            analyze_news("", "")

if __name__ == "__main__":
    unittest.main()
