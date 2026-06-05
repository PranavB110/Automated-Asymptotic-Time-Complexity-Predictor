import sys
sys.path.append("D:\\complexity-predictor")

import pandas as pd
import numpy as np
import joblib
import os
from feature_extraction.extractor import extract_features
from data.dataset import dataset
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import xgboost as xgb
import warnings
warnings.filterwarnings("ignore")

# ── 1. Build feature matrix ──────────────────────────────────────────────────
print("Extracting features from dataset...")
X, y = [], []
for code, label in dataset:
    feats = extract_features(code)
    if feats:
        X.append(list(feats.values()))
        y.append(label)

feature_names = list(extract_features(dataset[0][0]).keys())
X = np.array(X)
print(f"Dataset shape: {X.shape}  |  Labels: {len(y)}")

# ── 2. Encode labels ─────────────────────────────────────────────────────────
le = LabelEncoder()
y_enc = le.fit_transform(y)
print(f"Classes: {list(le.classes_)}\n")

# ── 3. Train/test split ───────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=0.2, random_state=42, stratify=None
)

# ── 4. Train multiple models ──────────────────────────────────────────────────
models = {
    "Random Forest":        RandomForestClassifier(n_estimators=100, random_state=42),
    "Gradient Boosting":    GradientBoostingClassifier(n_estimators=100, random_state=42),
    "SVM":                  SVC(kernel="rbf", probability=True, random_state=42),
    "XGBoost":              xgb.XGBClassifier(n_estimators=100, random_state=42,
                                               eval_metric="mlogloss",
                                               num_class=len(le.classes_)),
}

print("=" * 55)
best_score, best_name, best_model = 0, "", None

for name, model in models.items():
    model.fit(X_train, y_train)
    cv_scores = cross_val_score(model, X, y_enc, cv=3, scoring="accuracy")
    test_acc  = model.score(X_test, y_test)
    print(f"{name:<25} | CV: {cv_scores.mean():.2f} ± {cv_scores.std():.2f} | Test: {test_acc:.2f}")
    if test_acc > best_score:
        best_score, best_name, best_model = test_acc, name, model

print("=" * 55)
print(f"\n✅ Best Model: {best_name}  (Test Accuracy: {best_score:.2f})\n")

# ── 5. Detailed report for best model ────────────────────────────────────────
y_pred = best_model.predict(X_test)
print("Classification Report:")
present_labels = sorted(set(y_test) | set(y_pred))
present_names  = le.inverse_transform(present_labels)
print(classification_report(y_test, y_pred, labels=present_labels, target_names=present_names))

# ── 6. Save model & encoder ──────────────────────────────────────────────────
os.makedirs("D:\\complexity-predictor\\model", exist_ok=True)
joblib.dump(best_model, "D:\\complexity-predictor\\model\\model.pkl")
joblib.dump(le,         "D:\\complexity-predictor\\model\\label_encoder.pkl")
joblib.dump(feature_names, "D:\\complexity-predictor\\model\\feature_names.pkl")
print("💾 Model saved to D:\\complexity-predictor\\model\\")