"""
TruthLens AI — Database Module
Handles SQLite schema creation, CRUD operations, analysis history,
filtering, searching, and dashboard analytics aggregation.
"""

import os
import sqlite3
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "truthlens.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            headline TEXT NOT NULL,
            content TEXT,
            verdict TEXT NOT NULL,
            prediction_label TEXT NOT NULL,
            credibility_score REAL NOT NULL,
            confidence REAL NOT NULL,
            word_count INTEGER DEFAULT 0,
            risk_score INTEGER DEFAULT 0,
            top_real_terms TEXT,
            top_fake_terms TEXT,
            explanation TEXT,
            linguistics_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_verdict ON analyses(verdict)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON analyses(created_at)")
    conn.commit()
    conn.close()

def save_analysis(headline: str, content: str, analysis_result: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    
    top_real = json.dumps(analysis_result.get("attributions", {}).get("real_supporting_terms", []))
    top_fake = json.dumps(analysis_result.get("attributions", {}).get("fake_supporting_terms", []))
    explanation = json.dumps(analysis_result.get("explanation_points", []))
    linguistics = json.dumps(analysis_result.get("linguistics", {}))
    
    cursor.execute("""
        INSERT INTO analyses (
            headline, content, verdict, prediction_label, credibility_score,
            confidence, word_count, risk_score, top_real_terms, top_fake_terms,
            explanation, linguistics_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (
        headline,
        content,
        analysis_result.get("verdict", "Unverified"),
        analysis_result.get("prediction_label", "Unknown"),
        analysis_result.get("credibility_score", 50.0),
        analysis_result.get("confidence", 50.0),
        analysis_result.get("word_count", 0),
        analysis_result.get("linguistics", {}).get("stylistic_risk_score", 0),
        top_real,
        top_fake,
        explanation,
        linguistics
    ))
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id

def get_history(page: int = 1, per_page: int = 10, filter_verdict: str = None, search_query: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    
    where_clauses = []
    params = []
    
    if filter_verdict and filter_verdict.lower() != "all":
        where_clauses.append("LOWER(verdict) = ?")
        params.append(filter_verdict.lower())
        
    if search_query and search_query.strip():
        where_clauses.append("(headline LIKE ? OR content LIKE ?)")
        wildcard = f"%{search_query.strip()}%"
        params.extend([wildcard, wildcard])
        
    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    
    # Count total
    count_query = f"SELECT COUNT(*) FROM analyses {where_sql}"
    cursor.execute(count_query, params)
    total_count = cursor.fetchone()[0]
    
    # Fetch paginated rows
    offset = max(0, (page - 1) * per_page)
    data_query = f"""
        SELECT id, headline, verdict, prediction_label, credibility_score, confidence,
               word_count, risk_score, created_at
        FROM analyses
        {where_sql}
        ORDER BY created_at DESC, id DESC
        LIMIT ? OFFSET ?
    """
    cursor.execute(data_query, params + [per_page, offset])
    rows = cursor.fetchall()
    
    items = []
    for r in rows:
        items.append({
            "id": r["id"],
            "headline": r["headline"],
            "verdict": r["verdict"],
            "prediction_label": r["prediction_label"],
            "credibility_score": r["credibility_score"],
            "confidence": r["confidence"],
            "word_count": r["word_count"],
            "risk_score": r["risk_score"],
            "created_at": r["created_at"]
        })
        
    conn.close()
    return {
        "items": items,
        "total": total_count,
        "page": page,
        "per_page": per_page,
        "total_pages": max(1, (total_count + per_page - 1) // per_page)
    }

def get_analysis_by_id(record_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analyses WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
        
    return {
        "id": row["id"],
        "headline": row["headline"],
        "content": row["content"],
        "verdict": row["verdict"],
        "prediction_label": row["prediction_label"],
        "credibility_score": row["credibility_score"],
        "confidence": row["confidence"],
        "word_count": row["word_count"],
        "risk_score": row["risk_score"],
        "top_real_terms": json.loads(row["top_real_terms"] or "[]"),
        "top_fake_terms": json.loads(row["top_fake_terms"] or "[]"),
        "explanation": json.loads(row["explanation"] or "[]"),
        "linguistics": json.loads(row["linguistics_json"] or "{}"),
        "created_at": row["created_at"]
    }

def delete_analysis(record_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analyses WHERE id = ?", (record_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def clear_all_history() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analyses")
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_count

def get_statistics():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM analyses")
    total = cursor.fetchone()[0]
    
    if total == 0:
        conn.close()
        return {
            "total_analyses": 0,
            "real_count": 0,
            "fake_count": 0,
            "unverified_count": 0,
            "avg_credibility": 0.0,
            "avg_confidence": 0.0,
            "score_distribution": {"0-25": 0, "26-50": 0, "51-75": 0, "76-100": 0},
            "timeline": []
        }
        
    cursor.execute("SELECT COUNT(*) FROM analyses WHERE verdict = 'Real'")
    real_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM analyses WHERE verdict = 'Fake'")
    fake_count = cursor.fetchone()[0]
    
    unverified_count = total - (real_count + fake_count)
    
    cursor.execute("SELECT AVG(credibility_score), AVG(confidence) FROM analyses")
    avg_cred, avg_conf = cursor.fetchone()
    
    # Score distribution
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN credibility_score <= 25 THEN 1 ELSE 0 END),
            SUM(CASE WHEN credibility_score > 25 AND credibility_score <= 50 THEN 1 ELSE 0 END),
            SUM(CASE WHEN credibility_score > 50 AND credibility_score <= 75 THEN 1 ELSE 0 END),
            SUM(CASE WHEN credibility_score > 75 THEN 1 ELSE 0 END)
        FROM analyses
    """)
    b1, b2, b3, b4 = cursor.fetchone()
    
    # Timeline: count by date for last 7 dates
    cursor.execute("""
        SELECT date(created_at) as day, 
               COUNT(*) as count,
               SUM(CASE WHEN verdict = 'Real' THEN 1 ELSE 0 END) as real_cnt,
               SUM(CASE WHEN verdict = 'Fake' THEN 1 ELSE 0 END) as fake_cnt
        FROM analyses
        GROUP BY date(created_at)
        ORDER BY day DESC
        LIMIT 7
    """)
    timeline_rows = cursor.fetchall()
    timeline = [
        {"date": r["day"], "total": r["count"], "real": r["real_cnt"], "fake": r["fake_cnt"]}
        for r in reversed(timeline_rows)
    ]
    
    conn.close()
    return {
        "total_analyses": total,
        "real_count": real_count,
        "fake_count": fake_count,
        "unverified_count": unverified_count,
        "avg_credibility": round(avg_cred or 0.0, 1),
        "avg_confidence": round(avg_conf or 0.0, 1),
        "score_distribution": {
            "0-25": b1 or 0,
            "26-50": b2 or 0,
            "51-75": b3 or 0,
            "76-100": b4 or 0
        },
        "timeline": timeline
    }
