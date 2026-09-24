"""
AI Scam Message Detector & Digital Safety Assistant
Flask backend: combines a TF-IDF + Naive Bayes ML classifier with a
rule-based red-flag scanner to produce a risk score, verdict, flagged
signals, and safety tips for any pasted message.
"""
import re
import pandas as pd
from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from detector import rule_based_scan, build_highlighted_html

app = Flask(__name__)

# ---------- Train the ML model once at startup ----------
DATA_PATH = "scam_dataset.csv"
df = pd.read_csv(DATA_PATH)

vectorizer = TfidfVectorizer(stop_words="english", max_features=3000)
X = vectorizer.fit_transform(df["message"])
y = (df["label"] == "scam").astype(int)

model = MultinomialNB()
model.fit(X, y)

ML_WEIGHT = 0.5
RULE_WEIGHT = 0.5


def clean_for_model(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+", " link ", text)
    return text


def verdict_for(score: int):
    if score < 30:
        return "Looks safe", "safe"
    if score < 60:
        return "Some caution signs", "caution"
    return "High risk of scam", "danger"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "Please paste a message to analyze."}), 400

    cleaned = clean_for_model(message)
    vec = vectorizer.transform([cleaned])
    ml_probability = float(model.predict_proba(vec)[0][1])
    ml_score = ml_probability * 100

    rule_score, triggered_rules = rule_based_scan(message)

    final_score = round(ML_WEIGHT * ml_score + RULE_WEIGHT * rule_score)
    final_score = max(0, min(100, final_score))

    label, level = verdict_for(final_score)

    flags = [{"name": r["name"], "tip": r["tip"]} for r in triggered_rules]

    tips = [f["tip"] for f in flags]
    if not tips:
        if final_score >= 30:
            tips.append(
                "The wording resembles known scam patterns even without an exact match. Verify the sender through an official channel before acting."
            )
        else:
            tips.append(
                "No major red flags found, but always verify unexpected requests for money, OTPs, or personal details independently."
            )

    return jsonify(
        {
            "score": final_score,
            "verdict": label,
            "level": level,
            "ml_probability": round(ml_probability * 100, 1),
            "rule_score": rule_score,
            "flags": flags,
            "tips": tips,
            "highlighted_message": build_highlighted_html(message, triggered_rules),
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)