from app.ml.feature_builder import build_features
from app.ml.explainer import predict_and_explain
from app.ml.anomaly_detector import detect_anomaly

def run_ml_prediction(inspect_response: dict) -> dict:
    try:
        features = build_features(inspect_response)

        # Random Forest prediction + SHAP
        result = predict_and_explain(features)

        # Isolation Forest anomaly detection
        anomaly = detect_anomaly(features)

        return {
            "status"           : "success",
            "prediction"       : result["prediction"],
            "confidence"       : result["confidence"],
            "scam_probability" : result["scam_probability"],
            "safe_probability" : result["safe_probability"],
            "top_features"     : result["top_features"],
            "model_used"       : "Random Forest (v1)",
            "anomaly_detection": anomaly
        }

    except Exception as e:
        return {
            "status"  : "error",
            "message" : str(e)
        }