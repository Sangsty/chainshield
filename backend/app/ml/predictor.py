from app.ml.feature_builder import build_features
from app.ml.explainer import predict_and_explain

def run_ml_prediction(inspect_response: dict) -> dict:
    """
    Full ML pipeline:
    1. Extract features from inspect response
    2. Run prediction + SHAP explanation
    3. Return structured ML block
    """
    try:
        features = build_features(inspect_response)
        result   = predict_and_explain(features)

        return {
            "status"           : "success",
            "prediction"       : result["prediction"],
            "confidence"       : result["confidence"],
            "scam_probability" : result["scam_probability"],
            "safe_probability" : result["safe_probability"],
            "top_features"     : result["top_features"],
            "model_used"       : "Random Forest (v1)"
        }

    except Exception as e:
        return {
            "status" : "error",
            "message": str(e)
        }