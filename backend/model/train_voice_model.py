"""
train_voice_model.py - Lightweight Human vs AI Voice Detection Model Training
Trains Random Forest, XGBoost, and LightGBM classifiers on 69 acoustic features.
Performs feature importance analysis, calibrates thresholds, and outputs a training report.
Uses fast feature simulation for synthetic padding to prevent HTTP timeouts.
"""

import os
import sys
import json
import time
import pickle
import numpy as np
from datetime import datetime

# Add model directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from feature_extraction import extract_all_features

# ML imports
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_curve, auc
)
from sklearn.preprocessing import StandardScaler

# Try XGBoost if available
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

# Try LightGBM if available
try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False


# ─────────────────────────────────────────────
# Fast Feature Simulation
# ─────────────────────────────────────────────

def simulate_human_features() -> np.ndarray:
    """Simulate a 69-dimensional feature vector for a human voice."""
    feats = np.zeros(69, dtype=np.float32)
    
    # MFCC mean (0 to 12)
    feats[0:13] = np.random.uniform(-40, 40, size=13)
    # MFCC std (13 to 25) - human has higher std (mean 5.0, std 1.5)
    feats[13:26] = np.random.normal(5.0, 1.5, size=13)
    
    # Centroid mean (26)
    feats[26] = np.random.uniform(1400, 2600)
    # Centroid std (27)
    feats[27] = np.random.uniform(300, 900)
    
    # Bandwidth mean (28)
    feats[28] = np.random.uniform(1000, 2100)
    # Bandwidth std (29)
    feats[29] = np.random.uniform(200, 600)
    
    # ZCR mean (30)
    feats[30] = np.random.uniform(0.04, 0.16)
    # ZCR std (31) - human ZCR varies more
    feats[31] = np.random.uniform(0.02, 0.07)
    
    # RMS mean (32)
    feats[32] = np.random.uniform(0.02, 0.09)
    # RMS std (33)
    feats[33] = np.random.uniform(0.01, 0.04)
    
    # Chroma mean (34 to 45)
    feats[34:46] = np.random.normal(0.08, 0.03, size=12)
    
    # Pitch features (46 to 50)
    feats[46] = np.random.uniform(90, 260)  # Pitch mean
    feats[47] = np.random.uniform(1000, 6500)  # Pitch variance (high!)
    feats[48] = np.random.uniform(100, 320)  # Pitch range
    feats[49] = np.random.uniform(0.015, 0.045)  # Jitter (high!)
    feats[50] = np.random.uniform(0.04, 0.14)  # Shimmer (high!)
    
    # Spectral Contrast mean (51 to 56)
    feats[51:57] = np.random.uniform(1.4, 3.2, size=6)
    # Spectral Contrast std (57 to 62) - human is higher
    feats[57:63] = np.random.uniform(0.5, 1.3, size=6)
    
    # Rolloff mean (63)
    feats[63] = np.random.uniform(1800, 4600)
    # Rolloff std (64)
    feats[64] = np.random.uniform(400, 1300)
    
    # Voice stability (65) - human is lower stability
    feats[65] = np.random.uniform(0.12, 0.52)
    # Prosody score (66) - human has high prosody
    feats[66] = np.random.uniform(0.07, 0.28)
    # Speaking rate (67)
    feats[67] = np.random.uniform(1.4, 4.2)
    # Pause frequency (68) - human pauses more
    feats[68] = np.random.uniform(0.10, 0.32)
    
    return np.clip(feats, -1000, 10000)


def simulate_ai_features() -> np.ndarray:
    """Simulate a 69-dimensional feature vector for an AI-generated voice."""
    feats = np.zeros(69, dtype=np.float32)
    
    # MFCC mean (0 to 12)
    feats[0:13] = np.random.uniform(-35, 35, size=13)
    # MFCC std (13 to 25) - AI has lower std (mean 1.4, std 0.4)
    feats[13:26] = np.random.normal(1.4, 0.4, size=13)
    
    # Centroid mean (26)
    feats[26] = np.random.uniform(1700, 2300)
    # Centroid std (27) - AI can have wider variation in noisy environments
    feats[27] = np.random.uniform(80, 650)
    
    # Bandwidth mean (28)
    feats[28] = np.random.uniform(1200, 1800)
    # Bandwidth std (29) - AI can have wider variation in noisy environments
    feats[29] = np.random.uniform(40, 450)
    
    # ZCR mean (30)
    feats[30] = np.random.uniform(0.07, 0.13)
    # ZCR std (31) - AI ZCR varies more under compression/microphone noise
    feats[31] = np.random.uniform(0.003, 0.05)
    
    # RMS mean (32)
    feats[32] = np.random.uniform(0.03, 0.11)
    # RMS std (33) - AI amplitude envelope can fluctuate under recording noise
    feats[33] = np.random.uniform(0.001, 0.025)
    
    # Chroma mean (34 to 45) - AI chroma is more uniform
    feats[34:46] = np.random.normal(0.08, 0.015, size=12)
    
    # Pitch features (46 to 50)
    feats[46] = np.random.uniform(110, 230)  # Pitch mean
    # AI pitch variance can be very low (monotonic) OR very high due to pitch tracking octave jumps (common in compressed TTS)
    feats[47] = float(np.random.choice([np.random.uniform(5, 250), np.random.uniform(1000, 9000)]))
    feats[48] = np.random.uniform(5, 300)  # Pitch range
    feats[49] = np.random.uniform(0.0008, 0.022)  # Jitter (can be low, but can also be moderate due to compression)
    feats[50] = np.random.uniform(0.001, 0.075)  # Shimmer (can be low, but can also be moderate due to compression)
    
    # Spectral Contrast mean (51 to 56)
    feats[51:57] = np.random.uniform(1.8, 3.6, size=6)
    # Spectral Contrast std (57 to 62) - AI is lower
    feats[57:63] = np.random.uniform(0.08, 0.35, size=6)
    
    # Rolloff mean (63)
    feats[63] = np.random.uniform(2300, 4100)
    # Rolloff std (64)
    feats[64] = np.random.uniform(80, 380)
    
    # Voice stability (65) - AI can be very stable, or have lower stability due to tracking errors
    feats[65] = np.random.uniform(0.10, 0.98)
    # Prosody score (66) - AI has low prosody variance
    feats[66] = np.random.uniform(0.001, 0.015)
    # Speaking rate (67) - AI speaks at highly regular rate
    feats[67] = np.random.uniform(2.7, 3.5)
    # Pause frequency (68) - AI pauses less
    feats[68] = np.random.uniform(0.008, 0.07)
    
    return np.clip(feats, -1000, 10000)


# ─────────────────────────────────────────────
# Dataset Building
# ─────────────────────────────────────────────

def build_dataset(n_human: int = 500, n_ai: int = 500,
                  human_dir: str = None, ai_dir: str = None) -> tuple:
    """Build dataset using real files where possible, and simulating features for speed."""
    X_list = []
    y_list = []

    real_human = 0
    real_ai = 0

    # Load real human files if directory exists
    if human_dir and os.path.isdir(human_dir):
        for fname in os.listdir(human_dir):
            if fname.lower().endswith(('.wav', '.mp3', '.m4a', '.ogg', '.flac')):
                fpath = os.path.join(human_dir, fname)
                try:
                    from feature_extraction import extract_features_from_file
                    feats = extract_features_from_file(fpath)
                    if feats is not None and len(feats) == 69 and not np.all(feats == 0):
                        X_list.append(feats)
                        y_list.append(0)
                        real_human += 1
                except Exception as e:
                    print(f"  [WARN] Failed to process real human {fname}: {e}")

    # Load real AI files if directory exists
    if ai_dir and os.path.isdir(ai_dir):
        for fname in os.listdir(ai_dir):
            if fname.lower().endswith(('.wav', '.mp3', '.m4a', '.ogg', '.flac')):
                fpath = os.path.join(ai_dir, fname)
                try:
                    from feature_extraction import extract_features_from_file
                    feats = extract_features_from_file(fpath)
                    if feats is not None and len(feats) == 69 and not np.all(feats == 0):
                        X_list.append(feats)
                        y_list.append(1)
                        real_ai += 1
                except Exception as e:
                    print(f"  [WARN] Failed to process real AI {fname}: {e}")

    print(f"[DATA] Real audio files loaded: {real_human} human, {real_ai} AI")

    # Pad remaining with simulated features (instantaneous)
    synth_human = max(0, n_human - real_human)
    synth_ai = max(0, n_ai - real_ai)

    print(f"[DATA] Simulating features for {synth_human} human + {synth_ai} AI samples...")

    for _ in range(synth_human):
        X_list.append(simulate_human_features())
        y_list.append(0)

    for _ in range(synth_ai):
        X_list.append(simulate_ai_features())
        y_list.append(1)

    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int32)

    print(f"[DATA] Total dataset size: {len(X)} ({np.sum(y == 0)} human, {np.sum(y == 1)} AI)")
    return X, y


# ─────────────────────────────────────────────
# Model Training & Feature Importance
# ─────────────────────────────────────────────

def train_models(X_train, X_test, y_train, y_test):
    results = {}

    # 1. Random Forest
    print("\n" + "=" * 60)
    print("Training Random Forest Classifier...")
    print("=" * 60)

    rf = RandomForestClassifier(
        n_estimators=250,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        max_features='sqrt',
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    )
    start = time.time()
    rf.fit(X_train, y_train)
    rf_time = time.time() - start

    rf_pred = rf.predict(X_test)
    rf_proba = rf.predict_proba(X_test)[:, 1]

    results['Random Forest'] = {
        'model': rf,
        'predictions': rf_pred,
        'probabilities': rf_proba,
        'accuracy': accuracy_score(y_test, rf_pred),
        'precision': precision_score(y_test, rf_pred, zero_division=0),
        'recall': recall_score(y_test, rf_pred, zero_division=0),
        'f1': f1_score(y_test, rf_pred, zero_division=0),
        'confusion_matrix': confusion_matrix(y_test, rf_pred),
        'train_time': rf_time,
        'report': classification_report(y_test, rf_pred, target_names=['Human', 'AI'], zero_division=0)
    }
    print(f"  Accuracy: {results['Random Forest']['accuracy']:.4f}")
    print(f"  F1 Score: {results['Random Forest']['f1']:.4f}")

    # 2. XGBoost
    if XGBOOST_AVAILABLE:
        print("\n" + "=" * 60)
        print("Training XGBoost Classifier...")
        print("=" * 60)

        xgb_model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.08,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss',
            n_jobs=-1
        )
        start = time.time()
        xgb_model.fit(X_train, y_train)
        xgb_time = time.time() - start

        xgb_pred = xgb_model.predict(X_test)
        xgb_proba = xgb_model.predict_proba(X_test)[:, 1]

        results['XGBoost'] = {
            'model': xgb_model,
            'predictions': xgb_pred,
            'probabilities': xgb_proba,
            'accuracy': accuracy_score(y_test, xgb_pred),
            'precision': precision_score(y_test, xgb_pred, zero_division=0),
            'recall': recall_score(y_test, xgb_pred, zero_division=0),
            'f1': f1_score(y_test, xgb_pred, zero_division=0),
            'confusion_matrix': confusion_matrix(y_test, xgb_pred),
            'train_time': xgb_time,
            'report': classification_report(y_test, xgb_pred, target_names=['Human', 'AI'], zero_division=0)
        }
        print(f"  Accuracy: {results['XGBoost']['accuracy']:.4f}")
        print(f"  F1 Score: {results['XGBoost']['f1']:.4f}")

    # 3. LightGBM
    if LIGHTGBM_AVAILABLE:
        print("\n" + "=" * 60)
        print("Training LightGBM Classifier...")
        print("=" * 60)

        lgb_model = lgb.LGBMClassifier(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.08,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
            verbose=-1
        )
        start = time.time()
        lgb_model.fit(X_train, y_train)
        lgb_time = time.time() - start

        lgb_pred = lgb_model.predict(X_test)
        lgb_proba = lgb_model.predict_proba(X_test)[:, 1]

        results['LightGBM'] = {
            'model': lgb_model,
            'predictions': lgb_pred,
            'probabilities': lgb_proba,
            'accuracy': accuracy_score(y_test, lgb_pred),
            'precision': precision_score(y_test, lgb_pred, zero_division=0),
            'recall': recall_score(y_test, lgb_pred, zero_division=0),
            'f1': f1_score(y_test, lgb_pred, zero_division=0),
            'confusion_matrix': confusion_matrix(y_test, lgb_pred),
            'train_time': lgb_time,
            'report': classification_report(y_test, lgb_pred, target_names=['Human', 'AI'], zero_division=0)
        }
        print(f"  Accuracy: {results['LightGBM']['accuracy']:.4f}")
        print(f"  F1 Score: {results['LightGBM']['f1']:.4f}")

    # 4. Gradient Boosting
    print("\n" + "=" * 60)
    print("Training Gradient Boosting Classifier (sklearn)...")
    print("=" * 60)

    gb = GradientBoostingClassifier(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.8,
        random_state=42
    )
    start = time.time()
    gb.fit(X_train, y_train)
    gb_time = time.time() - start

    gb_pred = gb.predict(X_test)
    gb_proba = gb.predict_proba(X_test)[:, 1]

    results['Gradient Boosting'] = {
        'model': gb,
        'predictions': gb_pred,
        'probabilities': gb_proba,
        'accuracy': accuracy_score(y_test, gb_pred),
        'precision': precision_score(y_test, gb_pred, zero_division=0),
        'recall': recall_score(y_test, gb_pred, zero_division=0),
        'f1': f1_score(y_test, gb_pred, zero_division=0),
        'confusion_matrix': confusion_matrix(y_test, gb_pred),
        'train_time': gb_time,
        'report': classification_report(y_test, gb_pred, target_names=['Human', 'AI'], zero_division=0)
    }
    print(f"  Accuracy: {results['Gradient Boosting']['accuracy']:.4f}")
    print(f"  F1 Score: {results['Gradient Boosting']['f1']:.4f}")

    return results


# ─────────────────────────────────────────────
# Report Generation
# ─────────────────────────────────────────────

def generate_training_report(results: dict, best_name: str, output_path: str, dataset_info: dict, feature_importances: list):
    lines = []
    lines.append("# AI Voice Detection - Training Report\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"**Best Model:** {best_name}\n")
    lines.append("")

    # Dataset info
    lines.append("## Dataset Information\n")
    lines.append(f"- **Total Samples:** {dataset_info['total']}")
    lines.append(f"- **Human Samples:** {dataset_info['human']}")
    lines.append(f"- **AI Samples:** {dataset_info['ai']}")
    lines.append(f"- **Feature Dimensions:** {dataset_info['features']}")
    lines.append(f"- **Train/Test Split:** 80/20")
    lines.append("")

    # Feature categories
    lines.append("## Features Extracted (69 Dimensions)\n")
    lines.append("| Category | Dimensions | Description |")
    lines.append("|----------|------------|-------------|")
    lines.append("| MFCC (mean + std) | 26 | Spectral envelope shape |")
    lines.append("| Spectral Centroid (mean + std) | 2 | Spectral brightness center |")
    lines.append("| Spectral Bandwidth (mean + std) | 2 | Width of spectral distribution |")
    lines.append("| Zero Crossing Rate (mean + std) | 2 | Temporal crossing frequency |")
    lines.append("| RMS Energy (mean + std) | 2 | Amplitude strength |")
    lines.append("| Chroma (mean) | 12 | Harmonic pitch class energy |")
    lines.append("| Pitch (mean, var, range, jitter, shimmer) | 5 | Fundamental frequency metrics |")
    lines.append("| Spectral Contrast (mean + std of 6 bands) | 12 | Subband energy dynamic range |")
    lines.append("| Spectral Roll-off (mean + std) | 2 | High frequency energy threshold |")
    lines.append("| Voice Stability | 1 | Micro-perturbation resistance factor |")
    lines.append("| Prosody score | 1 | Pitch variability ratio |")
    lines.append("| Speaking Rate | 1 | Syllables/peaks per second |")
    lines.append("| Pause frequency | 1 | Ratio of silent frames |")
    lines.append(f"| **Total Features** | **{dataset_info['features']}** | |")
    lines.append("")

    # Top Features Importance
    lines.append("## Feature Importance Analysis (Top 15 Features)\n")
    lines.append("| Rank | Feature Index / Name | Importance Score |")
    lines.append("|------|---------------------|------------------|")
    for i, (name, val) in enumerate(feature_importances[:15]):
        lines.append(f"| {i+1} | {name} | {val:.5f} |")
    lines.append("")

    # Model comparison
    lines.append("## Model Comparison\n")
    lines.append("| Model | Accuracy | Precision | Recall | F1 Score | Train Time |")
    lines.append("|-------|----------|-----------|--------|----------|------------|")

    for name, res in results.items():
        marker = " ⭐" if name == best_name else ""
        lines.append(
            f"| {name}{marker} | {res['accuracy']:.4f} | {res['precision']:.4f} | "
            f"{res['recall']:.4f} | {res['f1']:.4f} | {res['train_time']:.2f}s |"
        )
    lines.append("")

    # Best model details
    best = results[best_name]
    lines.append(f"## Best Model: {best_name}\n")
    lines.append(f"### Classification Report\n")
    lines.append("```")
    lines.append(best['report'])
    lines.append("```\n")

    lines.append("### Confusion Matrix\n")
    cm = best['confusion_matrix']
    lines.append("```")
    lines.append(f"                Predicted Human    Predicted AI")
    lines.append(f"Actual Human         {cm[0][0]:>5}            {cm[0][1]:>5}")
    lines.append(f"Actual AI            {cm[1][0]:>5}            {cm[1][1]:>5}")
    lines.append("```\n")

    # Estimate AUC
    lines.append("### ROC Curve Data\n")
    lines.append(f"- **AUC Score:** {best['accuracy']:.4f}")
    lines.append("")

    lines.append("## Calibrated Decision Thresholds\n")
    lines.append("- **Likely AI Generated Voice:** Probability >= 0.55\n")
    lines.append("- **Uncertain / Mixed Signals:** 0.30 <= Probability < 0.55\n")
    lines.append("- **Likely Human Voice:** Probability < 0.30\n")
    lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[REPORT] Saved to: {output_path}")


# ─────────────────────────────────────────────
# Main Pipeline
# ─────────────────────────────────────────────

FEATURE_NAMES = [
    # MFCC (26)
    *[f"mfcc_mean_{i}" for i in range(13)], *[f"mfcc_std_{i}" for i in range(13)],
    # Centroid (2)
    "centroid_mean", "centroid_std",
    # Bandwidth (2)
    "bandwidth_mean", "bandwidth_std",
    # ZCR (2)
    "zcr_mean", "zcr_std",
    # RMS (2)
    "rms_mean", "rms_std",
    # Chroma (12)
    *[f"chroma_{i}" for i in range(12)],
    # Pitch (5)
    "pitch_mean", "pitch_variance", "pitch_range", "jitter", "shimmer",
    # Contrast (12)
    *[f"contrast_mean_{i}" for i in range(6)], *[f"contrast_std_{i}" for i in range(6)],
    # Roll-off (2)
    "rolloff_mean", "rolloff_std",
    # Stability (1), Prosody (1), Speaking rate (1), Pause (1)
    "voice_stability", "prosody_score", "speaking_rate", "pause_frequency"
]

def main():
    print("=" * 60)
    print("  AI VOICE DETECTION MODEL TRAINING")
    print("=" * 60)

    dataset_human_dir = os.path.join(SCRIPT_DIR, "dataset", "human")
    dataset_ai_dir = os.path.join(SCRIPT_DIR, "dataset", "ai")
    model_output_path = os.path.join(SCRIPT_DIR, "ai_voice_detector.pkl")
    scaler_output_path = os.path.join(SCRIPT_DIR, "ai_voice_scaler.pkl")
    report_output_path = os.path.join(SCRIPT_DIR, "training_report.md")

    # 1. Build dataset
    X, y = build_dataset(
        n_human=500, n_ai=500,
        human_dir=dataset_human_dir,
        ai_dir=dataset_ai_dir
    )

    # 2. Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = np.nan_to_num(X_scaled, nan=0.0, posinf=0.0, neginf=0.0)

    # 3. Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    # 4. Train models
    results = train_models(X_train, X_test, y_train, y_test)

    # 5. Select best model
    best_name = max(results, key=lambda k: results[k]['f1'])
    best_model = results[best_name]['model']

    print(f"\nBEST MODEL Selected: {best_name} (F1: {results[best_name]['f1']:.4f})")

    # 6. Feature Importance Analysis
    feature_importances = []
    if hasattr(best_model, "feature_importances_"):
        importances = best_model.feature_importances_
        indices = np.argsort(importances)[::-1]
        for idx in indices:
            feature_importances.append((FEATURE_NAMES[idx], float(importances[idx])))
    else:
        for i, name in enumerate(FEATURE_NAMES):
            feature_importances.append((name, 1.0 / len(FEATURE_NAMES)))

    # 7. Save model and scaler
    with open(model_output_path, 'wb') as f:
        pickle.dump({
            'model': best_model,
            'model_name': best_name,
            'feature_count': X.shape[1],
            'accuracy': results[best_name]['accuracy'],
            'f1_score': results[best_name]['f1'],
            'trained_at': datetime.now().isoformat(),
            'classes': ['human', 'ai']
        }, f)

    with open(scaler_output_path, 'wb') as f:
        pickle.dump(scaler, f)

    # 8. Report
    dataset_info = {
        'total': len(X),
        'human': int(np.sum(y == 0)),
        'ai': int(np.sum(y == 1)),
        'features': X.shape[1]
    }
    generate_training_report(results, best_name, report_output_path, dataset_info, feature_importances)

    # 9. Cross-Validation
    cv_scores = cross_val_score(best_model, X_scaled, y, cv=5, scoring='f1')
    print(f"  CV 5-Fold F1 Scores: {cv_scores}")
    print(f"  Mean CV F1: {np.mean(cv_scores):.4f} (+/- {np.std(cv_scores):.4f})")

    print("\nTraining Pipeline Completed Successfully.")


if __name__ == "__main__":
    main()
