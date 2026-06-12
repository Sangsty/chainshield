import shap
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

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

LABEL_MAP_REVERSE = {0: "safe", 1: "scam"}

# ── Load model ────────────────────────────────────────────────────────────────
def load_model():
    model_path = MODELS_DIR / "random_forest.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")
    return joblib.load(model_path)

# ── Safely extract flat float array from any SHAP output format ───────────────
def extract_shap_array(shap_values, row_scaled):
    """
    SHAP returns different formats depending on version.
    This handles all of them and always returns a flat 1D numpy float array
    corresponding to class 1 (scam) for the single input row.
    """
    # Case 1: list of arrays (older shap) — one array per class
    if isinstance(shap_values, list):
        arr = np.array(shap_values[1])
        return arr.flatten().astype(float)

    # Case 2: newer shap Explanation object
    if hasattr(shap_values, 'values'):
        sv = shap_values.values
        sv = np.array(sv)
        if sv.ndim == 3:
            # shape (n_samples, n_features, n_classes) — take class 1
            return sv[0, :, 1].flatten().astype(float)
        elif sv.ndim == 2:
            # shape (n_samples, n_features)
            return sv[0].flatten().astype(float)
        else:
            return sv.flatten().astype(float)

    # Case 3: raw numpy array
    arr = np.array(shap_values)
    if arr.ndim == 3:
        return arr[0, :, 1].flatten().astype(float)
    elif arr.ndim == 2:
        return arr[0].flatten().astype(float)
    else:
        return arr.flatten().astype(float)

# ── Main prediction + explanation function ────────────────────────────────────
def predict_and_explain(feature_dict: dict) -> dict:
    """
    Takes a flat dict of feature values.
    Returns prediction label, confidence, and top SHAP explanations.
    """
    pipeline = load_model()

    # Build single-row dataframe
    row = pd.DataFrame([{col: feature_dict.get(col, 0) for col in FEATURE_COLS}])

    # Prediction
    pred_encoded = pipeline.predict(row)[0]
    pred_proba   = pipeline.predict_proba(row)[0]
    pred_label   = LABEL_MAP_REVERSE[int(pred_encoded)]
    confidence   = round(float(max(pred_proba)), 4)

    # Scale row for SHAP
    rf_model   = pipeline.named_steps["model"]
    scaler     = pipeline.named_steps["scaler"]
    row_scaled = scaler.transform(row)

    # SHAP explanation
    explainer   = shap.TreeExplainer(rf_model)
    shap_values = explainer.shap_values(row_scaled)

    # Extract clean 1D float array for scam class
    shap_array = extract_shap_array(shap_values, row_scaled)

    # Validate length matches features
    if len(shap_array) != len(FEATURE_COLS):
        raise ValueError(
            f"SHAP array length {len(shap_array)} "
            f"does not match features {len(FEATURE_COLS)}"
        )

    # Sort by absolute importance
    shap_pairs = sorted(
        [(feat, float(val)) for feat, val in zip(FEATURE_COLS, shap_array)],
        key=lambda x: abs(x[1]),
        reverse=True
    )

    total_shap = sum(abs(v) for _, v in shap_pairs) + 1e-9

    # Build top 6 feature explanations
    top_features = []
    for feature_name, shap_val in shap_pairs[:6]:
        actual_value = feature_dict.get(feature_name, 0)
        direction    = "toward_scam" if shap_val > 0 else "toward_safe"

        top_features.append({
            "feature"        : feature_name,
            "value"          : actual_value,
            "shap_value"     : round(shap_val, 4),
            "direction"      : direction,
            "importance_pct" : round(abs(shap_val) / total_shap * 100, 1)
        })

    return {
        "prediction"       : pred_label,
        "confidence"       : confidence,
        "scam_probability" : round(float(pred_proba[1]), 4),
        "safe_probability" : round(float(pred_proba[0]), 4),
        "top_features"     : top_features
    }