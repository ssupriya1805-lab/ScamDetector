"""
Day 2 unit test: runs the combined detector against 20 sample messages
(mix of scam and safe) and reports how many were classified correctly.

Run this AFTER app.py's model has trained — this script reuses the same
vectorizer/model/rule-scan logic by importing straight from app.py.
"""
from app import vectorizer, model, clean_for_model, ML_WEIGHT, RULE_WEIGHT, verdict_for
from detector import rule_based_scan

# (message, expected_label) — expected_label is "scam" or "safe"
TEST_MESSAGES = [
    ("Congratulations! You have won Rs 5,00,000 in Amazon lucky draw, click here to claim", "scam"),
    ("Your OTP for login is 774512, do not share it with anyone", "safe"),
    ("URGENT: Your bank account will be suspended today, verify KYC immediately via this link", "scam"),
    ("Hi, are we still meeting for lunch tomorrow at 1pm?", "safe"),
    ("Instant loan of Rs 2,00,000 approved, no documents needed, click to receive amount", "scam"),
    ("Your Swiggy order has been delivered, enjoy your meal!", "safe"),
    ("Share your ATM PIN to receive government subsidy of Rs 10,000", "scam"),
    ("Reminder: Your electricity bill of Rs 890 is due on the 28th", "safe"),
    ("You are selected for a work from home job, pay Rs 999 registration fee to start", "scam"),
    ("The quarterly report is attached, please review before Monday's meeting", "safe"),
    ("Double your investment in 7 days guaranteed, invest now with zero risk", "scam"),
    ("Your flight is confirmed, check-in opens 48 hours before departure", "safe"),
    ("Final notice: pay Rs 5000 immediately or legal action will be taken against you", "scam"),
    ("Thanks for the update, I'll get back to you by end of day", "safe"),
    ("Your Aadhaar will be deactivated, verify now at this link to avoid losing benefits", "scam"),
    ("Your salary has been credited to your account ending 4521", "safe"),
    ("Free iPhone for the first 50 users, just pay Rs 99 shipping, click now", "scam"),
    ("Doctor's appointment confirmed for tomorrow 11am", "safe"),
    ("Your parcel is held at customs, pay Rs 350 duty to release it immediately", "scam"),
    ("Team, don't forget the submission deadline is this Friday", "safe"),
]


def classify(message: str):
    cleaned = clean_for_model(message)
    vec = vectorizer.transform([cleaned])
    ml_probability = float(model.predict_proba(vec)[0][1])
    ml_score = ml_probability * 100

    rule_score, triggered = rule_based_scan(message)

    final_score = round(ML_WEIGHT * ml_score + RULE_WEIGHT * rule_score)
    final_score = max(0, min(100, final_score))

    verdict, level = verdict_for(final_score)
    predicted_label = "scam" if final_score >= 30 else "safe"
    return final_score, predicted_label, verdict, [t["name"] for t in triggered]


def run_tests():
    correct = 0
    print(f"{'MESSAGE':<55} {'EXPECT':<6} {'GOT':<6} {'SCORE':<6} RESULT")
    print("-" * 95)

    for message, expected in TEST_MESSAGES:
        score, predicted, verdict, flags = classify(message)
        is_correct = predicted == expected
        correct += is_correct
        mark = "PASS" if is_correct else "FAIL"

        short_msg = (message[:52] + "...") if len(message) > 52 else message
        print(f"{short_msg:<55} {expected:<6} {predicted:<6} {score:<6} {mark}")

    total = len(TEST_MESSAGES)
    accuracy = round((correct / total) * 100, 1)
    print("-" * 95)
    print(f"Result: {correct}/{total} correct  |  Accuracy: {accuracy}%")


if __name__ == "__main__":
    run_tests()
