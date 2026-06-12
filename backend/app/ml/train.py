import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score,
    recall_score, f1_score, confusion_matrix,
    classification_report
)

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).resolve().parent.parent.parent.parent
DATASET    = ROOT / "data" / "datasets" / "fraud_dataset.csv"
MODELS_DIR = Path(__file__).resolve().parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# ── Features ──────────────────────────────────────────────────────────────────
FEATURE_COLS = [
    "contract_verified",
    "is_proxy",
    "dangerous_function_count",
    "top_lp_holder_pct",
    "creator_controls_liquidity",
    "mint_count",
    "large_mint_detected",
    "ownership_renounced",
    "honeypot_signal_count",
    "honeypot_risk_encoded",
    "risk_score",
    "contract_risk_score",
    "honeypot_risk_score",
    "event_risk_score",
    "liquidity_risk_score"
]

LABEL_MAP         = {"safe": 0, "scam": 1}
LABEL_MAP_REVERSE = {0: "safe", 1: "scam"}

# ── Load data ─────────────────────────────────────────────────────────────────
def load_data():
    df = pd.read_csv(DATASET)
    df["label_encoded"] = df["label"].map(LABEL_MAP)

    X = df[FEATURE_COLS].copy()
    y = df["label_encoded"].copy()

    print(f"Dataset loaded  : {X.shape[0]} rows, {X.shape[1]} features")
    print(f"Label counts    : {dict(df['label'].value_counts())}\n")
    return X, y

# ── Cross-validation evaluation ───────────────────────────────────────────────
def cross_val_evaluate(pipeline, X, y, model_name):
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    scoring  = ["accuracy", "precision", "recall", "f1"]
    cv_results = cross_validate(pipeline, X, y, cv=cv, scoring=scoring)

    acc  = cv_results["test_accuracy"].mean()
    prec = cv_results["test_precision"].mean()
    rec  = cv_results["test_recall"].mean()
    f1   = cv_results["test_f1"].mean()

    print(f"\n{'='*55}")
    print(f"Model : {model_name}  (5-Fold Cross Validation)")
    print(f"{'='*55}")
    print(f"  Accuracy  : {acc:.4f}  ± {cv_results['test_accuracy'].std():.4f}")
    print(f"  Precision : {prec:.4f}  ± {cv_results['test_precision'].std():.4f}")
    print(f"  Recall    : {rec:.4f}  ± {cv_results['test_recall'].std():.4f}")
    print(f"  F1 Score  : {f1:.4f}  ± {cv_results['test_f1'].std():.4f}")

    return {
        "accuracy"  : round(acc,  4),
        "precision" : round(prec, 4),
        "recall"    : round(rec,  4),
        "f1"        : round(f1,   4)
    }

# ── Feature importance ────────────────────────────────────────────────────────
def print_feature_importance(rf_model, feature_cols):
    importances = rf_model.feature_importances_
    pairs = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)

    print(f"\nFeature Importance (Random Forest):")
    print(f"{'─'*50}")
    for name, score in pairs:
        bar = "█" * int(score * 40)
        print(f"  {name:<35} {bar} {score:.4f}")

# ── Save model ────────────────────────────────────────────────────────────────
def save_model(pipeline, metrics, model_name, filename):
    model_path = MODELS_DIR / filename
    joblib.dump(pipeline, model_path)

    meta = {
        "model_name" : model_name,
        "features"   : FEATURE_COLS,
        "label_map"  : LABEL_MAP,
        "metrics"    : metrics
    }
    meta_path = MODELS_DIR / filename.replace(".pkl", "_meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"  Saved : {model_path.name}")
    print(f"  Saved : {meta_path.name}")

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("ChainShield — Phase 5 Model Training")
    print("="*55)

    X, y = load_data()

    # ── Logistic Regression pipeline (scaler + model) ─────────────────────────
    print("Training Logistic Regression...")
    lr_pipeline = Pipeline([
        ("scaler", MinMaxScaler()),
        ("model",  LogisticRegression(max_iter=2000, random_state=42))
    ])
    lr_metrics = cross_val_evaluate(lr_pipeline, X, y, "Logistic Regression")

    # Fit on full dataset before saving
    lr_pipeline.fit(X, y)
    save_model(lr_pipeline, lr_metrics, "Logistic Regression", "logistic_regression.pkl")

    # ── Random Forest pipeline ────────────────────────────────────────────────
    print("\nTraining Random Forest...")
    rf_pipeline = Pipeline([
        ("scaler", MinMaxScaler()),
        ("model",  RandomForestClassifier(
            n_estimators = 200,
            max_depth    = 4,
            random_state = 42,
            class_weight = "balanced"
        ))
    ])
    rf_metrics = cross_val_evaluate(rf_pipeline, X, y, "Random Forest")

    # Fit on full dataset before saving
    rf_pipeline.fit(X, y)

    # Print feature importance from fitted RF
    rf_model = rf_pipeline.named_steps["model"]
    print_feature_importance(rf_model, FEATURE_COLS)

    save_model(rf_pipeline, rf_metrics, "Random Forest", "random_forest.pkl")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*55}")
    print("FINAL COMPARISON  (5-Fold Cross Validation)")
    print(f"{'='*55}")
    print(f"{'Model':<25} {'Accuracy':>10} {'F1 Score':>10}")
    print(f"{'─'*45}")
    print(f"{'Logistic Regression':<25} {lr_metrics['accuracy']:>10} {lr_metrics['f1']:>10}")
    print(f"{'Random Forest':<25} {rf_metrics['accuracy']:>10} {rf_metrics['f1']:>10}")

    print(f"\nModels saved to: {MODELS_DIR}")
    print("\nTraining complete.")

if __name__ == "__main__":
    main()