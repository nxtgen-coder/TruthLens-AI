"""
TruthLens AI — Inference & Explainability Engine
Combines the trained scikit-learn model with linguistic analysis,
stylistic heuristics, and feature attribution for explainable predictions.
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

import re
import json
import joblib
import numpy as np

# Load model and vectorizer at module level for high-throughput reuse
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "model.joblib")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.joblib")
METRICS_PATH = os.path.join(MODEL_DIR, "model_metrics.json")

_model = None
_vectorizer = None
_metrics = None

def get_engine():
    global _model, _vectorizer, _metrics
    if _model is None or _vectorizer is None:
        if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
            raise FileNotFoundError("Model artifacts not found. Please run model/train.py first.")
        _model = joblib.load(MODEL_PATH)
        _vectorizer = joblib.load(VECTORIZER_PATH)
    if _metrics is None and os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            _metrics = json.load(f)
    return _model, _vectorizer, _metrics

CLICKBAIT_PATTERNS = [
    r"\b(shocking|bombshell|unbelievable|miracle|secret cure|wake up|sheeple)\b",
    r"\b(they don'?t want you to know|what they hide|exposed|hidden truth|leaked)\b",
    r"\b(doctors are (stunned|terrified)|you won'?t believe|this one (weird )?trick)\b",
    r"\b(illuminati|reptilian|deep state|chemtrail|mind control|depopulation)\b"
]

ATTRIBUTION_PATTERNS = [
    r"\baccording to\b",
    r"\b(stated|confirmed|reported|announced|indicated|noted)\b",
    r"\b(spokesperson|officials|researchers|scientists|investigators|analysts)\b",
    r"\b(published in|peer-reviewed|clinical trial|data shows|study found)\b",
    r"\b(reuters|associated press|bbc|court|ministry|department|agency)\b"
]

def analyze_linguistics(headline: str, text: str):
    combined = f"{headline} {text}"
    words = re.findall(r"\b[A-Za-z0-9'-]+\b", combined)
    word_count = len(words)
    sentences = [s.strip() for s in re.split(r"[.!?]+", combined) if s.strip()]
    sentence_count = max(1, len(sentences))
    
    # Uppercase analysis
    caps_words = [w for w in re.findall(r"\b[A-Z]{2,}\b", headline) if w not in {"USA", "NASA", "CERN", "COVID", "FDA", "CDC", "AI", "EU", "UN"}]
    headline_caps_ratio = len(caps_words) / max(1, len(headline.split()))
    
    # Punctuation anomalies (sensationalism)
    exclamations = combined.count("!")
    questions = combined.count("?")
    sensational_punct_score = min(100, (exclamations * 15) + (max(0, questions - 1) * 10))
    
    # Clickbait keyword search
    clickbait_matches = []
    for pattern in CLICKBAIT_PATTERNS:
        found = re.findall(pattern, combined, re.IGNORECASE)
        for match in found:
            term = match[0] if isinstance(match, tuple) else match
            if term.lower() not in [m.lower() for m in clickbait_matches]:
                clickbait_matches.append(term)
                
    # Attribution patterns
    attribution_matches = []
    for pattern in ATTRIBUTION_PATTERNS:
        found = re.findall(pattern, text, re.IGNORECASE)
        for match in found:
            term = match[0] if isinstance(match, tuple) else match
            if term.lower() not in [m.lower() for m in attribution_matches]:
                attribution_matches.append(term)
                
    # Quote marks count (evidence of direct quotes)
    quote_count = len(re.findall(r'["“][^"”]+["”]', combined))
    
    # Numbers and percentages count
    stats_count = len(re.findall(r"\b\d+(\.\d+)?%|\b\$\d+(\.\d+)?|\b\d{4}\b", combined))
    
    # Assess stylistic risk level (0-100)
    risk_score = 0
    if len(caps_words) >= 2 or headline_caps_ratio > 0.25:
        risk_score += 25
    if sensational_punct_score >= 15:
        risk_score += 25
    if len(clickbait_matches) >= 1:
        risk_score += min(35, len(clickbait_matches) * 15)
    if quote_count == 0 and len(attribution_matches) == 0:
        risk_score += 15
        
    risk_score = min(100, risk_score)
    
    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_words_per_sentence": round(word_count / sentence_count, 1),
        "exclamation_count": exclamations,
        "caps_words_in_headline": caps_words,
        "sensational_punct_score": sensational_punct_score,
        "clickbait_terms_detected": clickbait_matches,
        "attribution_terms_detected": attribution_matches,
        "quote_count": quote_count,
        "stats_count": stats_count,
        "stylistic_risk_score": risk_score
    }

def extract_feature_attributions(model, vectorizer, input_text: str, top_k: int = 5):
    """
    Computes local feature contribution weights by multiplying the TF-IDF representation
    with the model's learned weights.
    """
    tfidf_vec = vectorizer.transform([input_text])
    feature_names = np.array(vectorizer.get_feature_names_out())
    coefs = model.coef_[0]
    
    # Non-zero terms in this document
    row = tfidf_vec.tocoo()
    contributions = []
    for col_idx, tfidf_val in zip(row.col, row.data):
        feat_name = feature_names[col_idx]
        weight = coefs[col_idx]
        impact = float(tfidf_val * weight)
        contributions.append({
            "term": feat_name,
            "impact": impact,
            "weight": float(weight),
            "tfidf": float(tfidf_val)
        })
        
    # Sort positive (supports Credible/Real) and negative (supports Fake/Questionable)
    real_supporting = sorted([c for c in contributions if c["impact"] > 0], key=lambda x: x["impact"], reverse=True)[:top_k]
    fake_supporting = sorted([c for c in contributions if c["impact"] < 0], key=lambda x: x["impact"])[:top_k]
    
    # Convert impact to absolute value for cleaner UI representation
    for item in fake_supporting:
        item["impact_abs"] = abs(item["impact"])
        
    return {
        "real_supporting_terms": real_supporting,
        "fake_supporting_terms": fake_supporting
    }

def analyze_news(headline: str, text: str):
    """
    Comprehensive news analysis pipeline returning classification,
    credibility score, confidence explanation, and stylistic indicators.
    """
    headline = (headline or "").strip()
    text = (text or "").strip()
    
    if not headline and not text:
        raise ValueError("Please provide a news headline or article text.")
        
    model, vectorizer, metrics = get_engine()
    
    # 1. Feature & Text Prep
    full_text = f"{headline}. {headline}. {text}"
    linguistics = analyze_linguistics(headline, text)
    
    # 2. Machine Learning Inference
    X = vectorizer.transform([full_text])
    probabilities = model.predict_proba(X)[0] # [P(Fake), P(Real)]
    prob_fake = float(probabilities[0])
    prob_real = float(probabilities[1])
    
    # 3. Credibility Score Calculation (0-100)
    # Blend probabilistic model with linguistic heuristic penalties
    raw_score = prob_real * 100
    
    # Stylistic adjustment penalty if heavy clickbait/sensationalism detected
    risk_penalty = linguistics["stylistic_risk_score"] * 0.15
    credibility_score = max(2.0, min(98.5, raw_score - risk_penalty if raw_score > 50 else raw_score))
    credibility_score = round(credibility_score, 1)
    
    # Classification Category
    if credibility_score >= 70:
        prediction_label = "Likely Credible"
        verdict = "Real"
        verdict_class = "credible"
        badge_color = "emerald"
    elif credibility_score >= 45:
        prediction_label = "Dubious / Mixed Credibility"
        verdict = "Unverified"
        verdict_class = "warning"
        badge_color = "amber"
    else:
        prediction_label = "High Risk / Likely Misinformation"
        verdict = "Fake"
        verdict_class = "fake"
        badge_color = "crimson"
        
    # Model confidence
    confidence = round(max(prob_real, prob_fake) * 100, 1)
    
    # 4. Feature Attributions
    attributions = extract_feature_attributions(model, vectorizer, full_text, top_k=6)
    
    # 5. Dynamic Explanation Builder
    explanation_points = []
    if prob_real > prob_fake:
        explanation_points.append(f"Model identified formal journalistic terminology and factual syntax with a statistical probability of {round(prob_real * 100, 1)}%.")
    else:
        explanation_points.append(f"Model detected linguistic patterns characteristic of fabricated or conspiracy claims with a probability of {round(prob_fake * 100, 1)}%.")
        
    if linguistics["caps_words_in_headline"]:
        explanation_points.append(f"Sensationalist headline formatting detected: capitalized emphasis on '{', '.join(linguistics['caps_words_in_headline'][:3])}'.")
        
    if linguistics["exclamation_count"] > 1:
        explanation_points.append(f"Contains {linguistics['exclamation_count']} exclamation marks, often correlated with sensationalism.")
        
    if linguistics["clickbait_terms_detected"]:
        explanation_points.append(f"Clickbait buzzwords flagged: {', '.join(linguistics['clickbait_terms_detected'][:4])}.")
        
    if linguistics["attribution_terms_detected"]:
        explanation_points.append(f"Contains source attribution cues such as: {', '.join(linguistics['attribution_terms_detected'][:4])}.")
    else:
        explanation_points.append("Minimal or no formal source attributions (e.g. 'according to', official spokesperson) detected.")
        
    if linguistics["quote_count"] > 0:
        explanation_points.append(f"Contains {linguistics['quote_count']} direct quoted statement(s), indicating potential journalistic sourcing.")
        
    disclaimer = (
        "Disclaimer: TruthLens AI predictions are algorithmic estimates based on statistical text modeling "
        "and linguistic pattern recognition. Machine learning models can make errors. This score does not constitute "
        "absolute proof of truth or falsehood. Always verify critical news through authoritative primary sources "
        "and recognized fact-checking networks."
    )
    
    return {
        "prediction_label": prediction_label,
        "verdict": verdict,
        "verdict_class": verdict_class,
        "badge_color": badge_color,
        "credibility_score": credibility_score,
        "confidence": confidence,
        "probability_real": round(prob_real * 100, 1),
        "probability_fake": round(prob_fake * 100, 1),
        "linguistics": linguistics,
        "attributions": attributions,
        "explanation_points": explanation_points,
        "disclaimer": disclaimer,
        "headline_preview": headline[:120] + ("..." if len(headline) > 120 else ""),
        "word_count": linguistics["word_count"]
    }
