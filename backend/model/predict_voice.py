"""
predict_voice.py - AI Voice Detection Prediction Module

Loads the trained model (ai_voice_detector.pkl) and predicts whether
an audio file contains Human or AI-Generated voice.

Usage:
  python predict_voice.py <audio_file_path>
  
  Or import and use programmatically:
    from predict_voice import VoicePredictor
    predictor = VoicePredictor()
    result = predictor.predict_file("sample.wav")
    result = predictor.predict_bytes(audio_bytes)

Output format:
{
    "human_probability": 0.12,
    "ai_probability": 0.88,
    "prediction": "Likely AI Generated Voice",
    "confidence": 88.0,
    "model_name": "Random Forest",
    "features_used": 51
}
"""

import os
import sys
import json
import pickle
import numpy as np

# Add model directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from feature_extraction import extract_all_features, decode_audio_to_pcm


class VoicePredictor:
    """
    Lightweight Human vs AI Voice predictor.
    Loads a trained sklearn/xgboost model and predicts on audio input.
    """

    def __init__(self, model_path: str = None, scaler_path: str = None):
        """
        Initialize the predictor by loading the trained model and scaler.
        Falls back to heuristic if model files are not found.
        """
        if model_path is None:
            model_path = os.path.join(SCRIPT_DIR, "ai_voice_detector.pkl")
        if scaler_path is None:
            scaler_path = os.path.join(SCRIPT_DIR, "ai_voice_scaler.pkl")

        self.model = None
        self.scaler = None
        self.model_name = "Heuristic"
        self.feature_count = 51
        self.model_loaded = False

        # Try loading trained model
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)

                self.model = model_data['model']
                self.model_name = model_data.get('model_name', 'Unknown')
                self.feature_count = model_data.get('feature_count', 51)
                self.model_loaded = True
                print(f"[VoicePredictor] Loaded {self.model_name} model "
                      f"(F1: {model_data.get('f1_score', 'N/A')}, "
                      f"Acc: {model_data.get('accuracy', 'N/A')})")
            except Exception as e:
                print(f"[VoicePredictor] Failed to load model: {e}")

        # Try loading scaler
        if os.path.exists(scaler_path):
            try:
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
            except Exception as e:
                print(f"[VoicePredictor] Failed to load scaler: {e}")

        if not self.model_loaded:
            print("[VoicePredictor] Model not loaded. Using heuristic fallback.")

    def predict_signal(self, signal: np.ndarray, sr: int = 16000) -> dict:
        """
        Predict from a float32 audio signal array.
        """
        # Extract features
        features = extract_all_features(signal, sr)

        if self.model_loaded and self.model is not None:
            return self._predict_ml(features)
        else:
            return self._predict_heuristic(features)

    def predict_bytes(self, audio_bytes: bytes) -> dict:
        """
        Predict from raw audio file bytes (any format).
        """
        signal, sr = decode_audio_to_pcm(audio_bytes)
        if len(signal) == 0:
            return {
                "human_probability": 1.0,
                "ai_probability": 0.0,
                "prediction": "Unable to decode audio",
                "confidence": 0.0,
                "model_name": self.model_name,
                "features_used": self.feature_count,
            }
        return self.predict_signal(signal, sr)

    def predict_file(self, file_path: str) -> dict:
        """
        Predict from an audio file path.
        """
        if not os.path.exists(file_path):
            return {
                "human_probability": 0.0,
                "ai_probability": 0.0,
                "prediction": f"File not found: {file_path}",
                "confidence": 0.0,
                "model_name": self.model_name,
                "features_used": self.feature_count,
            }

        with open(file_path, 'rb') as f:
            audio_bytes = f.read()

        return self.predict_bytes(audio_bytes)

    def _predict_ml(self, features: np.ndarray) -> dict:
        """
        Use the trained ML model for prediction.
        """
        # Reshape for sklearn
        X = features.reshape(1, -1)

        # Handle feature count mismatch
        if X.shape[1] != self.feature_count:
            if X.shape[1] < self.feature_count:
                # Pad with zeros
                pad = np.zeros((1, self.feature_count - X.shape[1]))
                X = np.hstack([X, pad])
            else:
                # Truncate
                X = X[:, :self.feature_count]

        # Replace NaN/Inf
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

        # Scale
        if self.scaler is not None:
            X = self.scaler.transform(X)
            X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

        # Predict
        try:
            proba = self.model.predict_proba(X)[0]
            human_prob = float(proba[0])
            ai_prob = float(proba[1])

            if ai_prob >= 0.65:
                prediction = "Likely AI Generated Voice"
            elif ai_prob >= 0.35:
                prediction = "Uncertain - Mixed Signals"
            else:
                prediction = "Likely Human Voice"

            confidence = float(max(human_prob, ai_prob) * 100)

            return {
                "human_probability": round(human_prob, 4),
                "ai_probability": round(ai_prob, 4),
                "prediction": prediction,
                "confidence": round(confidence, 1),
                "model_name": self.model_name,
                "features_used": self.feature_count,
            }
        except Exception as e:
            print(f"[VoicePredictor] ML prediction failed: {e}")
            return self._predict_heuristic(features)

    def _predict_heuristic(self, features: np.ndarray) -> dict:
        """
        Heuristic fallback when ML model is not available.
        Uses simple threshold-based analysis on key features.
        """
        # Feature indices based on extract_all_features order:
        # [0-12] MFCC mean, [13-25] MFCC std,
        # [26-27] Spectral Centroid mean/std,
        # [28-29] Spectral Bandwidth mean/std,
        # [30-31] ZCR mean/std,
        # [32-33] RMS mean/std,
        # [34-45] Chroma mean,
        # [46] pitch_mean, [47] pitch_var, [48] pitch_range,
        # [49] jitter, [50] shimmer

        score = 0.0

        if len(features) >= 51:
            mfcc_std_mean = np.mean(features[13:26])
            pitch_var = features[47]
            jitter = features[49]
            shimmer = features[50]
            zcr_std = features[31]

            # Low MFCC variance -> synthetic
            if mfcc_std_mean < 2.0:
                score += 25

            # Low pitch variance -> monotone (AI-like)
            if pitch_var < 100:
                score += 25
            elif pitch_var < 300:
                score += 10

            # Low jitter -> too perfect (AI-like)
            if jitter < 0.006:
                score += 20
            elif jitter < 0.012:
                score += 10

            # Low shimmer -> too stable (AI-like)
            if shimmer < 0.03:
                score += 15
            elif shimmer < 0.06:
                score += 5

            # Low ZCR variation -> clean signal
            if zcr_std < 0.01:
                score += 15

        ai_prob = min(score / 100.0, 1.0)
        human_prob = 1.0 - ai_prob

        if ai_prob >= 0.65:
            prediction = "Likely AI Generated Voice"
        elif ai_prob >= 0.35:
            prediction = "Uncertain - Mixed Signals"
        else:
            prediction = "Likely Human Voice"

        return {
            "human_probability": round(human_prob, 4),
            "ai_probability": round(ai_prob, 4),
            "prediction": prediction,
            "confidence": round(max(human_prob, ai_prob) * 100, 1),
            "model_name": "Heuristic Fallback",
            "features_used": self.feature_count,
        }


# ─────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    predictor = VoicePredictor()

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        result = predictor.predict_file(file_path)
    else:
        # Demo with synthetic signal
        sr = 16000
        t = np.linspace(0, 3.0, int(sr * 3.0), endpoint=False)
        # Generate a simple tone (should be classified as AI-like)
        demo_signal = 0.5 * np.sin(2 * np.pi * 200 * t).astype(np.float32)
        result = predictor.predict_signal(demo_signal, sr)
        print("\n[Demo] Predicting on synthetic pure tone (expected: AI-like)")

    print("\n" + json.dumps(result, indent=2))
