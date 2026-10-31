# 🛡️ TruthLens AI — AI-Powered Fake News & Credibility Detection

TruthLens AI is a full-stack, machine-learning-powered web application that analyzes news headlines and article bodies to estimate journalistic credibility, detect hallmarks of misinformation, and provide transparent confidence explanations.

Built with **Python**, **Flask**, **scikit-learn**, **SQLite**, **HTML5**, **CSS3**, and **JavaScript (with Chart.js)**.

---

## 🌟 Key Features

- **Headline & Article Analysis**: Input arbitrary news headlines and full article bodies, or select from curated sample presets.
- **Genuine Machine Learning Classifier**: Powered by a trained scikit-learn pipeline (TF-IDF sublinear vectorizer + calibrated logistic regression). No hardcoded predictions.
- **Credibility Gauge & Confidence Score**: Generates a composite Credibility Score (0–100%) and confidence probability.
- **Explainable AI (Salient Keywords)**: Highlights specific words and phrases that swayed the model toward Credible or Misinformation verdicts.
- **Linguistic & Stylistic Risk Detection**:
  - Sensationalist punctuation tracking (multiple exclamation marks `!` and question marks `?`)
  - Headline capitalization shouting detection (ALL-CAPS words)
  - Clickbait buzzword scanning
  - Direct quotes and named source attribution verification (e.g. *Reuters*, *AP*, *spokesperson*, *peer-reviewed study*)
- **Interactive Dashboard with Chart.js**:
  - Classification distribution doughnut chart (Real vs Fake vs Dubious)
  - Credibility score bracket histogram (0–25%, 26–50%, 51–75%, 76–100%)
  - Analysis activity timeline
  - Linguistic risk factor radar comparison
- **Persistent SQLite History**:
  - Full search by keyword or headline
  - Filter by verdict (All, Real, Fake)
  - Detail modal for inspecting past analyses
  - Single record deletion & bulk history wipe
  - One-click CSV and JSON exports
- **Multi-Platform Share Feature**:
  - Direct shareable URLs (`?id=<analysis_id>`) that instantly load and render any analysis report
  - Web Share API integration (native device share sheet on supported browsers)
  - One-click social sharing to **X (Twitter)**, **WhatsApp**, **LinkedIn**, **Telegram**, and **Email**
  - Instant copy of formatted Markdown/text reports with complete credibility metrics and ethical disclaimers
- **Model Methodology & Transparency Tab**:
  - Live model accuracy, precision, recall, and F1 metrics
  - Confusion matrix visualization
  - Top learned predictive n-grams for real news vs fake news
- **Modern, Responsive Design**:
  - Glassmorphic UI with light/dark theme toggle (persisted via `localStorage`)
  - Mobile, tablet, and desktop responsive layouts
  - Animated SVG circular credibility gauge and toast alerts

---

## ⚠️ Important Methodological Disclaimer

> **Model Predictions are Statistical Estimates, Not Proof of Truth or Falsehood**
> 
> TruthLens AI evaluates linguistic syntax, vocabulary patterns, sensationalist markers, and attribution cues based on statistical pattern recognition. High credibility scores reflect journalistic tone and source attribution structures, while low credibility scores reflect sensationalist, hyperbolic, or conspiratorial linguistic markers. Predictions should be used as **decision support**, never as definitive or legal proof of truth. Users must always cross-reference critical claims with certified fact-checkers and authoritative primary sources.

---

## 🏗️ Architecture & Folder Structure

```
truthlens-ai/
├── app.py                     # Flask web server & REST API
├── database.py                # SQLite schema, CRUD operations & analytics
├── requirements.txt           # Dependencies (Flask, scikit-learn, numpy, joblib)
├── truthlens.db               # SQLite database
├── data/
│   └── news_dataset.csv       # Labelled dataset (700 balanced Real & Fake articles)
├── model/
│   ├── dataset.py             # Dataset generator script
│   ├── train.py               # Model training, evaluation & artifact exporter
│   ├── predictor.py           # ML inference engine & linguistic heuristics
│   ├── model.joblib           # Serialized scikit-learn classifier
│   ├── vectorizer.joblib      # Serialized TF-IDF vectorizer
│   └── model_metrics.json     # Saved accuracy, precision, recall, F1 & weights
├── static/
│   ├── css/
│   │   └── style.css          # Responsive design, light/dark themes, glassmorphism
│   └── js/
│       ├── app.js             # Main frontend app controller & history management
│       └── charts.js          # Chart.js visualization wrappers
├── templates/
│   └── index.html             # Single-page application HTML interface
└── tests/
    ├── test_model.py          # ML inference & linguistic tests
    ├── test_db.py             # SQLite CRUD & aggregation tests
    └── test_api.py            # Flask API endpoint integration tests
```

---

## 🚀 Quickstart & Setup Instructions

### 1. Prerequisites
- Python 3.9+ installed on your machine.
- macOS, Linux, or Windows.

### 2. Navigate to Project Directory & Create Virtual Environment
```bash
cd truthlens-ai
python3 -m venv venv

# Activate on macOS/Linux:
source venv/bin/activate

# Or on Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Regenerate Dataset & Retrain Model
The repository comes pre-trained with serialized model artifacts. To re-train or expand the dataset at any time:
```bash
# Generate the 700-article labelled dataset:
python3 model/dataset.py

# Train the model and export metrics:
python3 model/train.py
```

### 5. Run the Unit & Integration Tests
```bash
python3 -m unittest discover tests
```
*All 13 unit and integration tests will execute, validating the ML inference pipeline, SQLite database, and REST endpoints.*

### 6. Start the Web Server
```bash
export PORT=5050
python3 app.py
```
Open your web browser and navigate to:
👉 **[http://127.0.0.1:5050](http://127.0.0.1:5050)**

*(Note: Port 5050 is chosen by default to avoid macOS AirPlay Receiver port 5000 conflicts).*

---

## 📡 REST API Reference

### `POST /api/analyze`
Analyzes a headline and optional article text.
- **Request Body (JSON)**:
  ```json
  {
    "headline": "Renewable Energy Investment Surpasses Fossil Fuels for Second Year",
    "content": "According to the International Energy Agency, clean energy investments reached $1.7 trillion..."
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "data": {
      "id": 1,
      "verdict": "Real",
      "prediction_label": "Likely Credible",
      "credibility_score": 88.5,
      "confidence": 94.2,
      "probability_real": 88.5,
      "probability_fake": 11.5,
      "attributions": {
        "real_supporting_terms": [
          {"term": "international", "impact": 0.16},
          {"term": "capacity", "impact": 0.14}
        ],
        "fake_supporting_terms": []
      },
      "linguistics": {
        "word_count": 30,
        "stylistic_risk_score": 0,
        "attribution_terms_detected": ["According to"]
      },
      "explanation_points": [
        "Model identified formal journalistic terminology and factual syntax with a statistical probability of 88.5%.",
        "Contains source attribution cues such as: According to."
      ],
      "disclaimer": "Predictions are algorithmic estimates..."
    }
  }
  ```

### `GET /api/history`
Retrieves paginated analysis history.
- **Query Params**: `page` (default `1`), `per_page` (default `10`), `filter` (`all`, `Real`, `Fake`), `search` (string)

### `GET /api/history/<id>`
Retrieves full analysis record including linguistic details and explanation points.

### `GET /api/share/<id>`
Retrieves full analysis record alongside pre-formatted share titles and social text summaries.

### `DELETE /api/history/<id>`
Deletes a single analysis record from SQLite.

### `DELETE /api/history`
Clears all analysis records from SQLite.

### `GET /api/stats`
Returns aggregated analytics (total counts, average scores, score distributions, and 7-day timeline).

### `GET /api/model-info`
Returns current model type, accuracy, confusion matrix, and top weighted terms.

### `GET /api/samples`
Returns preset sample articles for quick interactive testing.

---

## 🔬 Machine Learning Pipeline Details

1. **Feature Engineering**:
   - Sublinear term-frequency scaling ($1 + \log(\text{tf})$).
   - Unigrams and Bigrams (`ngram_range=(1, 2)`).
   - English stop-word filtering and minimum document frequency (`min_df=2`).
2. **Classifier**:
   - Scikit-Learn `LogisticRegression` with calibrated probability estimates (`predict_proba`).
   - Regularization strength $C=1.5$, L-BFGS solver.
3. **Credibility Score Fusion**:
   - The statistical model's calibrated probability is combined with a heuristic penalty based on detected stylistic risk (clickbait, screaming capitalization, excessive exclamation marks, lack of named source attribution) to compute the final 0–100 Credibility Score.
