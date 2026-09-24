# AI Scam Message Detector & Digital Safety Assistant

A Flask web app that scores a pasted message (SMS / WhatsApp / email) for
scam risk, combining:
- a **TF-IDF + Naive Bayes** ML classifier trained on `scam_dataset.csv`
- a **rule-based red-flag scanner** (`detector.py`) for explainable signals
  like OTP requests, urgency pressure, fake prizes, and suspicious links

The two scores are blended into a single 0–100 risk score with a verdict
(Looks safe / Some caution signs / High risk of scam), the specific flags
that triggered, and matching safety tips.

## Run it in VS Code

1. Open this folder in VS Code (`File → Open Folder…`).
2. Open a terminal in VS Code (`` Ctrl+` ``) and create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate it:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the app:
   ```bash
   python app.py
   ```
6. Open **http://127.0.0.1:5000** in your browser.

## Project structure

```
scam-detector/
├── app.py              # Flask server + ML training + risk blending
├── detector.py         # Rule-based red-flag patterns and tips
├── scam_dataset.csv    # Training data (scam vs safe messages)
├── requirements.txt
├── templates/
│   └── index.html      # Page markup
└── static/
    ├── style.css        # Dark console UI
    └── script.js        # Fetches /analyze and renders result
```

## How the risk score works

`final_score = 0.5 × ML_score + 0.5 × rule_score`

- **ML score**: probability the Naive Bayes model assigns to "scam" for
  the message, based on word patterns learned from the dataset.
- **Rule score**: sum of weights for every red-flag pattern matched
  (OTP request, urgency language, upfront payment ask, prize language,
  suspicious link, account threat, easy loan, guaranteed-return
  investment) — capped at 100.

Thresholds: `<30` = Looks safe, `30–59` = Some caution signs, `≥60` =
High risk of scam.

## Extending it (Day 3+ ideas)

- Swap in a bigger dataset (merge with Kaggle's SMS Spam Collection) for
  a stronger ML model.
- Add a basic URL-reputation check (e.g. against a downloaded PhishTank
  feed) for the suspicious-link rule.
- Persist analyzed messages to a small SQLite log for a "history" view.
- Add multilingual rule patterns for Tamil/Hindi transliterated scam text.
