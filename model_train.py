"""
AI Model Training & Evaluation — Scam Message Detector
This script trains the Naive Bayes + TF-IDF classifier properly:
splits data into train/test sets, evaluates with standard ML metrics
(accuracy, precision, recall, F1), plots a confusion matrix, and
saves the trained model + vectorizer to disk for reuse.

Run this to generate the results you'll put in your project report.
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # no GUI needed, just save the image
import matplotlib.pyplot as plt
import pickle

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

# ---------- 1. Load the dataset ----------
df = pd.read_csv("scam_dataset.csv")
print(f"Total messages in dataset: {len(df)}")
print(f"Scam messages: {(df['label'] == 'scam').sum()}")
print(f"Safe messages: {(df['label'] == 'safe').sum()}")
print()

X_text = df["message"]
y = (df["label"] == "scam").astype(int)  # 1 = scam, 0 = safe

# ---------- 2. Train-test split (80% train, 20% test) ----------
X_train_text, X_test_text, y_train, y_test = train_test_split(
    X_text, y, test_size=0.2, random_state=42, stratify=y
)
print(f"Training set size: {len(X_train_text)}")
print(f"Test set size: {len(X_test_text)}")
print()

# ---------- 3. TF-IDF vectorization ----------
vectorizer = TfidfVectorizer(stop_words="english", max_features=3000)
X_train = vectorizer.fit_transform(X_train_text)
X_test = vectorizer.transform(X_test_text)

# ---------- 4. Train the Naive Bayes model ----------
model = MultinomialNB()
model.fit(X_train, y_train)

# ---------- 5. Evaluate on the held-out test set ----------
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print("=" * 50)
print("MODEL EVALUATION RESULTS")
print("=" * 50)
print(f"Accuracy:  {accuracy * 100:.1f}%")
print(f"Precision: {precision * 100:.1f}%")
print(f"Recall:    {recall * 100:.1f}%")
print(f"F1-score:  {f1 * 100:.1f}%")
print()
print("Detailed classification report:")
print(classification_report(y_test, y_pred, target_names=["safe", "scam"]))

# ---------- 6. Confusion matrix (as an image) ----------
cm = confusion_matrix(y_test, y_pred)

fig, ax = plt.subplots(figsize=(5, 4))
im = ax.imshow(cm, cmap="Blues")

labels = ["Safe", "Scam"]
ax.set_xticks([0, 1])
ax.set_yticks([0, 1])
ax.set_xticklabels(labels)
ax.set_yticklabels(labels)
ax.set_xlabel("Predicted label")
ax.set_ylabel("Actual label")
ax.set_title("Confusion Matrix — Scam Detector")

for i in range(2):
    for j in range(2):
        ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                 color="white" if cm[i, j] > cm.max() / 2 else "black",
                 fontsize=14, fontweight="bold")

plt.colorbar(im)
plt.tight_layout()
plt.savefig("confusion_matrix.png", dpi=150)
print("\nConfusion matrix saved as confusion_matrix.png")

# ---------- 7. Save the trained model + vectorizer ----------
with open("scam_model.pkl", "wb") as f:
    pickle.dump({"model": model, "vectorizer": vectorizer}, f)
print("Trained model saved as scam_model.pkl")
