import sys
sys.path.append("D:\\complexity-predictor")

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import joblib
import os
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score
from feature_extraction.extractor import extract_features
from data.dataset import dataset

# ── Load model ────────────────────────────────────────────────────────────────
model         = joblib.load("D:\\complexity-predictor\\model\\model.pkl")
le            = joblib.load("D:\\complexity-predictor\\model\\label_encoder.pkl")
feature_names = joblib.load("D:\\complexity-predictor\\model\\feature_names.pkl")

# ── Build full dataset ────────────────────────────────────────────────────────
X, y = [], []
for code, label in dataset:
    feats = extract_features(code)
    if feats:
        X.append(list(feats.values()))
        y.append(label)

X      = np.array(X)
y_enc  = le.transform(y)
y_pred = model.predict(X)
labels = list(le.classes_)

os.makedirs("D:\\complexity-predictor\\report", exist_ok=True)

plt.style.use("dark_background")
COLORS = ["#6366f1","#8b5cf6","#ec4899","#ef4444","#f97316","#eab308","#10b981"]

# ── Chart 1: Confusion Matrix ─────────────────────────────────────────────────
cm = confusion_matrix(y_enc, y_pred)
fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(cm, annot=True, fmt="d", cmap="PuBu",
            xticklabels=labels, yticklabels=labels,
            linewidths=0.5, linecolor="#1e293b", ax=ax,
            annot_kws={"size": 13, "weight": "bold"})
ax.set_title("Confusion Matrix — Time Complexity Prediction", fontsize=15, fontweight="bold", pad=16, color="#f1f5f9")
ax.set_xlabel("Predicted Label", fontsize=12, color="#94a3b8")
ax.set_ylabel("True Label",      fontsize=12, color="#94a3b8")
ax.tick_params(colors="#cbd5e1", labelsize=10)
plt.tight_layout()
plt.savefig("D:\\complexity-predictor\\report\\confusion_matrix.png", dpi=150, bbox_inches="tight", facecolor="#0f172a")
plt.close()
print("✅ confusion_matrix.png saved")

# ── Chart 2: Feature Importance ───────────────────────────────────────────────
importances = model.feature_importances_
indices     = np.argsort(importances)[::-1]
sorted_feat = [feature_names[i] for i in indices]
sorted_imp  = importances[indices]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(sorted_feat[::-1], sorted_imp[::-1],
               color=[COLORS[i % len(COLORS)] for i in range(len(sorted_feat))],
               edgecolor="#1e293b", height=0.6)
ax.set_title("Feature Importance — Random Forest", fontsize=15, fontweight="bold", pad=16, color="#f1f5f9")
ax.set_xlabel("Importance Score", fontsize=12, color="#94a3b8")
ax.tick_params(colors="#cbd5e1", labelsize=10)
ax.set_facecolor("#0f172a")
fig.patch.set_facecolor("#0f172a")
for bar, val in zip(bars, sorted_imp[::-1]):
    ax.text(val + 0.002, bar.get_y() + bar.get_height()/2,
            f"{val:.3f}", va="center", fontsize=9, color="#94a3b8")
plt.tight_layout()
plt.savefig("D:\\complexity-predictor\\report\\feature_importance.png", dpi=150, bbox_inches="tight", facecolor="#0f172a")
plt.close()
print("✅ feature_importance.png saved")

# ── Chart 3: Class Distribution ───────────────────────────────────────────────
from collections import Counter
counts = Counter(y)
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(counts.keys(), counts.values(),
              color=COLORS[:len(counts)], edgecolor="#1e293b", width=0.55)
ax.set_title("Dataset Class Distribution", fontsize=15, fontweight="bold", pad=16, color="#f1f5f9")
ax.set_xlabel("Complexity Class", fontsize=12, color="#94a3b8")
ax.set_ylabel("Number of Samples",fontsize=12, color="#94a3b8")
ax.tick_params(colors="#cbd5e1", labelsize=11)
ax.set_facecolor("#0f172a")
fig.patch.set_facecolor("#0f172a")
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
            str(int(bar.get_height())), ha="center", fontsize=11,
            fontweight="bold", color="#f1f5f9")
plt.tight_layout()
plt.savefig("D:\\complexity-predictor\\report\\class_distribution.png", dpi=150, bbox_inches="tight", facecolor="#0f172a")
plt.close()
print("✅ class_distribution.png saved")

# ── Chart 4: Model Accuracy Comparison ───────────────────────────────────────
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
import xgboost as xgb
import warnings
warnings.filterwarnings("ignore")

model_names = ["Random Forest", "Gradient Boosting", "SVM", "XGBoost"]
cv_means, cv_stds = [], []

clf_list = [
    RandomForestClassifier(n_estimators=100, random_state=42),
    GradientBoostingClassifier(n_estimators=100, random_state=42),
    SVC(kernel="rbf", probability=True, random_state=42),
    xgb.XGBClassifier(n_estimators=100, random_state=42, eval_metric="mlogloss", num_class=len(labels)),
]

for clf in clf_list:
    scores = cross_val_score(clf, X, y_enc, cv=3, scoring="accuracy")
    cv_means.append(scores.mean())
    cv_stds.append(scores.std())

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(model_names, cv_means, yerr=cv_stds,
              color=COLORS[:4], edgecolor="#1e293b",
              width=0.5, capsize=6, error_kw={"ecolor": "#94a3b8", "linewidth": 2})
ax.set_title("Model Accuracy Comparison (3-Fold CV)", fontsize=15, fontweight="bold", pad=16, color="#f1f5f9")
ax.set_ylabel("CV Accuracy", fontsize=12, color="#94a3b8")
ax.set_ylim(0, 1.05)
ax.tick_params(colors="#cbd5e1", labelsize=11)
ax.set_facecolor("#0f172a")
fig.patch.set_facecolor("#0f172a")
for bar, val in zip(bars, cv_means):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03,
            f"{val:.2f}", ha="center", fontsize=12,
            fontweight="bold", color="#f1f5f9")
plt.tight_layout()
plt.savefig("D:\\complexity-predictor\\report\\model_comparison.png", dpi=150, bbox_inches="tight", facecolor="#0f172a")
plt.close()
print("✅ model_comparison.png saved")

print("\n🎉 All 4 charts saved to D:\\complexity-predictor\\report\\")