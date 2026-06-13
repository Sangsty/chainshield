import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler

MODELS_DIR = Path(__file__).resolve().parent / "models"

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

# ── Train anomaly detector on safe tokens only ────────────────────────────────
def train_anomaly_detector():
    dataset_path = MODELS_DIR.parent.parent.parent.parent / "data" / "datasets" / "fraud_dataset.csv"

    df        = pd.read_csv(dataset_path)
    safe_df   = df[df["label"] == "safe"][FEATURE_COLS]

    scaler    = MinMaxScaler()
    X_scaled  = scaler.fit_transform(safe_df)

    model     = IsolationForest(
        n_estimators  = 100,
        contamination = 0.1,
        random_state  = 42
    )
    model.fit(X_scaled)

    joblib.dump(model,  MODELS_DIR / "anomaly_model.pkl")
    joblib.dump(scaler, MODELS_DIR / "anomaly_scaler.pkl")

    print(f"Anomaly detector trained on {len(safe_df)} safe tokens.")
    print(f"Saved: anomaly_model.pkl")
    print(f"Saved: anomaly_scaler.pkl")

# ── Detect anomaly for a single token ────────────────────────────────────────
def detect_anomaly(feature_dict: dict) -> dict:
    try:
        model_path  = MODELS_DIR / "anomaly_model.pkl"
        scaler_path = MODELS_DIR / "anomaly_scaler.pkl"

        if not model_path.exists() or not scaler_path.exists():
            return {
                "status"  : "error",
                "message" : "Anomaly model not trained yet."
            }

        model  = joblib.load(model_path)
        scaler = joblib.load(scaler_path)

        row       = pd.DataFrame([{col: feature_dict.get(col, 0) for col in FEATURE_COLS}])
        row_scaled= scaler.transform(row)

        prediction = model.predict(row_scaled)[0]   # 1 = normal, -1 = anomaly
        score      = model.decision_function(row_scaled)[0]

        # Normalize score to 0-100 anomaly scale
        # decision_function: more negative = more anomalous
        anomaly_score = round(max(0, min(100, (-score + 0.2) * 200)), 1)
        is_anomaly    = bool(prediction == -1)

        return {
            "status"         : "success",
            "is_anomaly"     : is_anomaly,
            "anomaly_score"  : anomaly_score,
            "verdict"        : "Anomalous pattern detected" if is_anomaly else "Normal token pattern",
            "note"           : "Isolation Forest trained on known safe tokens."
        }

    except Exception as e:
        return {
            "status"  : "error",
            "message" : str(e)
        }

if __name__ == "__main__":
    train_anomaly_detector()