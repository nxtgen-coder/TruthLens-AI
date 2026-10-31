"""
Model training pipeline for TruthLens AI.
Trains a scikit-learn Logistic Regression classifier with TF-IDF vectorization
on the labelled news dataset, computes comprehensive evaluation metrics,
and saves the trained artifacts for inference and explainability.
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

import csv
import json
import time
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import joblib

def load_data(csv_path: str):
    texts = []
    labels = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = (row.get("title") or "").strip()
            content = (row.get("text") or "").strip()
            # Combine title and content with slight emphasis on title
            combined = f"{title}. {title}. {content}"
            label = int(row.get("label", 0))
            texts.append(combined)
            labels.append(label)
    return texts, np.array(labels)

def train_and_evaluate(dataset_path: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Loading dataset from {dataset_path}...")
    texts, y = load_data(dataset_path)
    print(f"Loaded {len(texts)} samples (Real: {np.sum(y == 1)}, Fake: {np.sum(y == 0)}).")
    
    # 80/20 train/test stratified split
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        texts, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set: {len(X_train_raw)} | Testing set: {len(X_test_raw)}")
    
    # TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        sublinear_tf=True,
        min_df=2,
        stop_words="english"
    )
    
    X_train = vectorizer.fit_transform(X_train_raw)
    X_test = vectorizer.transform(X_test_raw)
    
    # Logistic Regression Classifier
    classifier = LogisticRegression(
        C=1.5,
        max_iter=1000,
        solver="lbfgs",
        random_state=42
    )
    
    classifier.fit(X_train, y_train)
    
    # Evaluation
    y_pred = classifier.predict(X_test)
    y_proba = classifier.predict_proba(X_test)
    
    accuracy = float(accuracy_score(y_test, y_pred))
    precision = float(precision_score(y_test, y_pred))
    recall = float(recall_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred))
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    print(f"\n--- Model Performance ---")
    print(f"Accuracy:  {accuracy * 100:.2f}%")
    print(f"Precision: {precision * 100:.2f}%")
    print(f"Recall:    {recall * 100:.2f}%")
    print(f"F1-Score:  {f1 * 100:.2f}%")
    print(f"Confusion Matrix: [TN={cm[0][0]}, FP={cm[0][1]}], [FN={cm[1][0]}, TP={cm[1][1]}]")
    
    # Extract top influential features
    feature_names = np.array(vectorizer.get_feature_names_out())
    coefs = classifier.coef_[0]
    
    # Positive coef -> Real news, Negative coef -> Fake news
    top_real_idx = np.argsort(coefs)[-15:][::-1]
    top_fake_idx = np.argsort(coefs)[:15]
    
    top_real_features = [{"word": str(feature_names[i]), "weight": float(coefs[i])} for i in top_real_idx]
    top_fake_features = [{"word": str(feature_names[i]), "weight": float(abs(coefs[i]))} for i in top_fake_idx]
    
    # Serialize artifacts
    model_path = os.path.join(output_dir, "model.joblib")
    vectorizer_path = os.path.join(output_dir, "vectorizer.joblib")
    metrics_path = os.path.join(output_dir, "model_metrics.json")
    
    joblib.dump(classifier, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    
    metrics = {
        "model_type": "TF-IDF + Calibrated Logistic Regression",
        "dataset_total": len(texts),
        "train_samples": len(X_train_raw),
        "test_samples": len(X_test_raw),
        "vocabulary_size": len(vectorizer.vocabulary_),
        "accuracy": round(accuracy * 100, 2),
        "precision": round(precision * 100, 2),
        "recall": round(recall * 100, 2),
        "f1_score": round(f1 * 100, 2),
        "confusion_matrix": {
            "true_negatives_fake": cm[0][0],
            "false_positives_real": cm[0][1],
            "false_negatives_fake": cm[1][0],
            "true_positives_real": cm[1][1]
        },
        "top_real_indicators": top_real_features,
        "top_fake_indicators": top_fake_features,
        "trained_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    }
    
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
        
    print(f"\nArtifacts successfully saved to {output_dir}")
    return metrics

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_file = os.path.join(project_root, "data", "news_dataset.csv")
    train_and_evaluate(data_file, current_dir)
