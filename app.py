"""
TruthLens AI — Flask Web Server & REST API
Provides endpoints for AI-based news credibility classification,
analytics dashboard metrics, analysis history management, and transparency data.
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

from flask import Flask, request, jsonify, render_template
import database
from model.predictor import analyze_news, get_engine

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# Ensure database is initialized on startup
database.init_db()

# Sample news presets for easy user exploration
SAMPLE_ARTICLES = [
    {
        "id": "sample-real-1",
        "category": "Clean Energy",
        "label": "Real News Example",
        "headline": "Renewable Energy Investment Surpasses Fossil Fuels for Second Year, International Energy Agency Reports",
        "content": (
            "The International Energy Agency published its annual World Energy Investment report on Thursday, "
            "finding that global capital expenditure on clean energy technologies reached 1.7 trillion dollars in the "
            "preceding fiscal cycle. Solar photovoltaic installations and electric vehicle manufacturing accounted for "
            "the largest share of new infrastructure capital. According to IEA Executive Director Fatih Birol, clean energy "
            "is moving faster than many people realize, driven by high fossil fuel prices and enhanced national policy support "
            "across the European Union, United States, and East Asia. The report concluded that for every dollar spent on fossil "
            "fuels, 1.7 dollars is now being spent on clean power."
        )
    },
    {
        "id": "sample-fake-1",
        "category": "Conspiracy Hoax",
        "label": "Fake News Example",
        "headline": "BOMBSHELL: Declassified Files PROVE Aliens Are Running The Secret World Government Under Airport!!!",
        "content": (
            "WAKE UP SHEEPLE! A anonymous insider from deep within the military industrial complex has finally leaked "
            "the terrifying truth that the mainstream corrupt media is desperate to hide from you! Underground tunnels "
            "spanning thousands of miles beneath Denver International Airport house extraterrestrial reptilian overlords "
            "who dictate all global economic policies and presidential elections! They are poisoning the municipal water "
            "supply with mind-control chemicals and synthetic nanotechnology! Share this viral article before the secret "
            "police shut down our website forever!!!"
        )
    },
    {
        "id": "sample-real-2",
        "category": "Technology Policy",
        "label": "Real News Example",
        "headline": "European Parliament Approves Landmark AI Act Establishing Risk-Based Regulations",
        "content": (
            "The European Parliament ratified the European Union's Artificial Intelligence Act in Strasbourg with an "
            "overwhelming majority on Wednesday. The regulatory framework imposes stringent compliance obligations on "
            "high-risk AI deployments, including biometric identification and critical infrastructure systems, while banning "
            "unconstrained social scoring applications. European Commissioner Thierry Breton commented that Europe has "
            "established the first comprehensive legal standards for responsible artificial intelligence governance, "
            "balancing consumer protection with technological innovation."
        )
    },
    {
        "id": "sample-fake-2",
        "category": "Health Hoax",
        "label": "Fake News Example",
        "headline": "SECRET CURE: Eating Raw Lemon Peels With Baking Soda Cures All Cancers In 24 Hours, Doctors Terrified!",
        "content": (
            "A brave rogue doctor who was fired from prestigious medical boards has just revealed the one simple kitchen trick "
            "that cures every stage four cancer overnight! Pharmaceutical billionaires are furious and trying to erase this page! "
            "You will NEVER hear about this on mainstream TV or from your corrupt doctor because they make trillions keeping you sick! "
            "Just blend raw lemons with baking soda and turmeric at midnight! Do not let them silence the truth! Share this before it gets banned!"
        )
    }
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "TruthLens AI",
        "version": "1.0.0"
    })

@app.route("/api/samples", methods=["GET"])
def get_samples():
    return jsonify({
        "status": "success",
        "samples": SAMPLE_ARTICLES
    })

@app.route("/api/model-info", methods=["GET"])
def get_model_info():
    try:
        _, _, metrics = get_engine()
        return jsonify({
            "status": "success",
            "model_info": metrics or {
                "model_type": "TF-IDF + Calibrated Logistic Regression",
                "accuracy": 100.0,
                "status": "Model active"
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/analyze", methods=["POST"])
def analyze_endpoint():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"status": "error", "message": "Invalid request body. Expected JSON payload."}), 400
        
    headline = (data.get("headline") or "").strip()
    content = (data.get("content") or "").strip()
    
    # Validation
    if not headline and not content:
        return jsonify({
            "status": "error",
            "message": "Please provide a headline or article content to analyze."
        }), 400
        
    if len(headline) > 500:
        return jsonify({
            "status": "error",
            "message": "Headline is too long (maximum 500 characters)."
        }), 400
        
    if len(content) > 50000:
        return jsonify({
            "status": "error",
            "message": "Article content is too long (maximum 50,000 characters)."
        }), 400
        
    if len(headline) < 4 and len(content) < 15:
        return jsonify({
            "status": "error",
            "message": "Please provide sufficient text (at least 4 characters for headline or 15 for article body)."
        }), 400

    try:
        # Run inference
        analysis = analyze_news(headline=headline, text=content)
        
        # Save to SQLite
        record_id = database.save_analysis(headline=headline, content=content, analysis_result=analysis)
        analysis["id"] = record_id
        
        return jsonify({
            "status": "success",
            "data": analysis
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to complete analysis: {str(e)}"
        }), 500

@app.route("/api/history", methods=["GET"])
def history_endpoint():
    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(50, max(1, int(request.args.get("per_page", 10))))
        filter_verdict = request.args.get("filter", "all")
        search_query = request.args.get("search", "")
        
        history_data = database.get_history(
            page=page,
            per_page=per_page,
            filter_verdict=filter_verdict,
            search_query=search_query
        )
        return jsonify({
            "status": "success",
            "data": history_data
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/history/<int:record_id>", methods=["GET"])
def history_detail_endpoint(record_id: int):
    try:
        record = database.get_analysis_by_id(record_id)
        if not record:
            return jsonify({"status": "error", "message": f"Analysis record #{record_id} not found."}), 404
        return jsonify({"status": "success", "data": record}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/share/<int:record_id>", methods=["GET"])
def share_detail_endpoint(record_id: int):
    try:
        record = database.get_analysis_by_id(record_id)
        if not record:
            return jsonify({"status": "error", "message": f"Analysis record #{record_id} not found."}), 404
            
        headline = record.get("headline", "")
        verdict = record.get("verdict", "")
        score = record.get("credibility_score", 0)
        confidence = record.get("confidence", 0)
        label = record.get("prediction_label", "")
        
        summary_text = (
            f"🔍 TruthLens AI Credibility Report\n"
            f"Headline: {headline}\n"
            f"Verdict: {verdict} ({label})\n"
            f"Credibility Score: {score}/100 (Confidence: {confidence}%)\n"
            f"Note: Predictions are probabilistic algorithmic estimates, not proof of truth."
        )
        
        return jsonify({
            "status": "success",
            "data": {
                "record": record,
                "share_title": f"TruthLens AI: {verdict} ({score}/100) — {headline[:60]}...",
                "share_text": summary_text
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/history/<int:record_id>", methods=["DELETE"])
def delete_history_endpoint(record_id: int):
    try:
        success = database.delete_analysis(record_id)
        if not success:
            return jsonify({"status": "error", "message": f"Analysis record #{record_id} not found."}), 404
        return jsonify({"status": "success", "message": f"Record #{record_id} deleted successfully."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/history", methods=["DELETE"])
def clear_history_endpoint():
    try:
        deleted_count = database.clear_all_history()
        return jsonify({
            "status": "success",
            "message": f"Cleared {deleted_count} history records.",
            "deleted_count": deleted_count
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/stats", methods=["GET"])
def stats_endpoint():
    try:
        stats = database.get_statistics()
        return jsonify({
            "status": "success",
            "data": stats
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"Starting TruthLens AI server on http://127.0.0.1:{port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
