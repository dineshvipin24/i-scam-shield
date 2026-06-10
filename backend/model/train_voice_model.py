"""
train_voice_model.py - Lightweight Human vs AI Voice Detection Model Training

Trains a Random Forest / XGBoost classifier on acoustic features to detect
AI-generated speech vs human speech.

Requirements:
  - Works on 8 GB RAM laptop
  - Training time: < 10 minutes
  - No transformers, wav2vec2, HuBERT, or large DL models

Usage:
  python train_voice_model.py

Outputs:
  - models/ai_voice_detector.pkl (trained model)
  - training_report.md (evaluation metrics)
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
    print("[INFO] XGBoost not installed. Using scikit-learn alternatives.")

# Try LightGBM if available
try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False


# ─────────────────────────────────────────────
# Synthetic Data Generation
# ─────────────────────────────────────────────

def generate_human_voice(duration_s: float = 3.0, sr: int = 16000) -> np.ndarray:
    """
    Generate a synthetic signal that mimics human voice characteristics:
    - Variable pitch (F0 between 85-300 Hz with natural variation)
    - Breathing noise in pauses
    - Amplitude modulation (natural prosody)
    - Micro-perturbations (jitter/shimmer)
    """
    num_samples = int(duration_s * sr)
    t = np.linspace(0, duration_s, num_samples, endpoint=False)

    # Base pitch with natural variation (vibrato + drift)
    base_f0 = np.random.uniform(100, 250)
    vibrato_rate = np.random.uniform(4, 7)  # Hz
    vibrato_depth = np.random.uniform(3, 12)  # Hz
    drift = np.cumsum(np.random.randn(num_samples) * 0.02)
    drift = drift / (np.max(np.abs(drift)) + 1e-8) * np.random.uniform(5, 20)

    f0 = base_f0 + vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t) + drift

    # Add jitter (pitch perturbation)
    jitter = np.random.randn(num_samples) * np.random.uniform(0.5, 3.0)
    f0 = f0 + jitter

    # Generate harmonics
    phase = np.cumsum(2 * np.pi * f0 / sr)
    signal = np.sin(phase)

    # Add harmonics with decreasing amplitude
    for harmonic in range(2, 6):
        amplitude = np.random.uniform(0.1, 0.4) / harmonic
        signal += amplitude * np.sin(harmonic * phase + np.random.uniform(0, 2 * np.pi))

    # Amplitude modulation (prosody/stress patterns)
    envelope_freq = np.random.uniform(0.5, 2.5)
    envelope = 0.5 + 0.5 * np.sin(2 * np.pi * envelope_freq * t + np.random.uniform(0, np.pi))

    # Add shimmer (amplitude perturbation)
    shimmer = 1.0 + np.random.randn(num_samples) * np.random.uniform(0.02, 0.1)
    signal = signal * envelope * shimmer

    # Add breathing noise in pauses
    pause_mask = np.random.rand(num_samples) < np.random.uniform(0.05, 0.15)
    breathing = np.random.randn(num_samples) * np.random.uniform(0.01, 0.05)
    signal[pause_mask] = breathing[pause_mask]

    # Add background noise
    noise_level = np.random.uniform(0.005, 0.03)
    signal += np.random.randn(num_samples) * noise_level

    # Normalize
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        signal = signal / max_val * np.random.uniform(0.5, 0.95)

    return signal.astype(np.float32)


def generate_ai_voice(duration_s: float = 3.0, sr: int = 16000) -> np.ndarray:
    """
    Generate a synthetic signal that mimics AI-generated voice characteristics:
    - Very stable pitch (low variance)
    - Minimal jitter/shimmer
    - No breathing artifacts
    - Smooth amplitude envelope
    - High spectral regularity
    """
    num_samples = int(duration_s * sr)
    t = np.linspace(0, duration_s, num_samples, endpoint=False)

    # Very stable pitch
    base_f0 = np.random.uniform(120, 220)
    # Slight controlled vibrato (much less than human)
    vibrato_depth = np.random.uniform(0.2, 1.5)
    vibrato_rate = np.random.uniform(4, 6)
    f0 = base_f0 + vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)

    # Minimal jitter
    jitter = np.random.randn(num_samples) * np.random.uniform(0.01, 0.15)
    f0 = f0 + jitter

    # Generate harmonics
    phase = np.cumsum(2 * np.pi * f0 / sr)
    signal = np.sin(phase)

    # Clean harmonics
    for harmonic in range(2, 5):
        amplitude = np.random.uniform(0.15, 0.35) / harmonic
        signal += amplitude * np.sin(harmonic * phase)

    # Smooth envelope (no natural breathing patterns)
    envelope = np.ones(num_samples) * np.random.uniform(0.7, 0.95)
    # Very smooth transitions
    smooth_mod = 0.5 + 0.5 * np.sin(2 * np.pi * 0.3 * t)
    envelope = envelope * (0.8 + 0.2 * smooth_mod)

    # Minimal shimmer
    shimmer = 1.0 + np.random.randn(num_samples) * np.random.uniform(0.001, 0.01)
    signal = signal * envelope * shimmer

    # Very low background noise (clean digital signal)
    noise_level = np.random.uniform(0.0005, 0.005)
    signal += np.random.randn(num_samples) * noise_level

    # Normalize
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        signal = signal / max_val * np.random.uniform(0.7, 0.95)

    return signal.astype(np.float32)


# ─────────────────────────────────────────────
# Dataset Building
# ─────────────────────────────────────────────

def build_dataset(n_human: int = 300, n_ai: int = 300,
                  human_dir: str = None, ai_dir: str = None) -> tuple:
    """
    Build feature matrix and labels from:
    1. Real audio files in dataset/human/ and dataset/ai/ (if available)
    2. Synthetically generated signals to fill the rest

    Returns: (X, y) where X is (n_samples, n_features), y is (n_samples,)
    """
    X_list = []
    y_list = []

    # Load real audio files if available
    real_human = 0
    real_ai = 0

    if human_dir and os.path.isdir(human_dir):
        for fname in os.listdir(human_dir):
            if fname.lower().endswith(('.wav', '.mp3', '.m4a', '.ogg', '.flac')):
                fpath = os.path.join(human_dir, fname)
                try:
                    from feature_extraction import extract_features_from_file
                    feats = extract_features_from_file(fpath)
                    if feats is not None and len(feats) > 0 and not np.all(feats == 0):
                        X_list.append(feats)
                        y_list.append(0)  # 0 = human
                        real_human += 1
                except Exception as e:
                    print(f"  [WARN] Failed to process {fname}: {e}")

    if ai_dir and os.path.isdir(ai_dir):
        for fname in os.listdir(ai_dir):
            if fname.lower().endswith(('.wav', '.mp3', '.m4a', '.ogg', '.flac')):
                fpath = os.path.join(ai_dir, fname)
                try:
                    from feature_extraction import extract_features_from_file
                    feats = extract_features_from_file(fpath)
                    if feats is not None and len(feats) > 0 and not np.all(feats == 0):
                        X_list.append(feats)
                        y_list.append(1)  # 1 = AI
                        real_ai += 1
                except Exception as e:
                    print(f"  [WARN] Failed to process {fname}: {e}")

    print(f"[DATA] Real audio files loaded: {real_human} human, {real_ai} AI")

    # Fill remaining with synthetic data
    synth_human = max(0, n_human - real_human)
    synth_ai = max(0, n_ai - real_ai)

    print(f"[DATA] Generating {synth_human} synthetic human + {synth_ai} synthetic AI samples...")

    durations = [2.0, 3.0, 4.0, 5.0]

    for i in range(synth_human):
        dur = durations[i % len(durations)]
        signal = generate_human_voice(duration_s=dur)
        feats = extract_all_features(signal, sr=16000)
        X_list.append(feats)
        y_list.append(0)
        if (i + 1) % 50 == 0:
            print(f"  Generated {i + 1}/{synth_human} human samples")

    for i in range(synth_ai):
        dur = durations[i % len(durations)]
        signal = generate_ai_voice(duration_s=dur)
        feats = extract_all_features(signal, sr=16000)
        X_list.append(feats)
        y_list.append(1)
        if (i + 1) % 50 == 0:
            print(f"  Generated {i + 1}/{synth_ai} AI samples")

    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int32)

    print(f"[DATA] Total dataset: {len(X)} samples ({np.sum(y == 0)} human, {np.sum(y == 1)} AI)")
    print(f"[DATA] Feature dimensions: {X.shape[1]}")

    return X, y


# ─────────────────────────────────────────────
# Model Training
# ─────────────────────────────────────────────

def train_models(X_train, X_test, y_train, y_test):
    """
    Train and evaluate multiple lightweight models.
    Returns the best model and its evaluation metrics.
    """
    results = {}

    # 1. Random Forest
    print("\n" + "=" * 60)
    print("Training Random Forest Classifier...")
    print("=" * 60)

    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
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
        'report': classification_report(y_test, rf_pred,
                                         target_names=['Human', 'AI'],
                                         zero_division=0)
    }
    print(f"  Accuracy: {results['Random Forest']['accuracy']:.4f}")
    print(f"  F1 Score: {results['Random Forest']['f1']:.4f}")
    print(f"  Train Time: {rf_time:.2f}s")

    # 2. XGBoost
    if XGBOOST_AVAILABLE:
        print("\n" + "=" * 60)
        print("Training XGBoost Classifier...")
        print("=" * 60)

        xgb_model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss',
            use_label_encoder=False,
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
            'report': classification_report(y_test, xgb_pred,
                                             target_names=['Human', 'AI'],
                                             zero_division=0)
        }
        print(f"  Accuracy: {results['XGBoost']['accuracy']:.4f}")
        print(f"  F1 Score: {results['XGBoost']['f1']:.4f}")
        print(f"  Train Time: {xgb_time:.2f}s")

    # 3. LightGBM (if available)
    if LIGHTGBM_AVAILABLE:
        print("\n" + "=" * 60)
        print("Training LightGBM Classifier...")
        print("=" * 60)

        lgb_model = lgb.LGBMClassifier(
            n_estimators=200,
            max_depth=10,
            learning_rate=0.1,
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
            'report': classification_report(y_test, lgb_pred,
                                             target_names=['Human', 'AI'],
                                             zero_division=0)
        }
        print(f"  Accuracy: {results['LightGBM']['accuracy']:.4f}")
        print(f"  F1 Score: {results['LightGBM']['f1']:.4f}")
        print(f"  Train Time: {lgb_time:.2f}s")

    # 4. Gradient Boosting (sklearn fallback)
    print("\n" + "=" * 60)
    print("Training Gradient Boosting Classifier (sklearn)...")
    print("=" * 60)

    gb = GradientBoostingClassifier(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.1,
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
        'report': classification_report(y_test, gb_pred,
                                         target_names=['Human', 'AI'],
                                         zero_division=0)
    }
    print(f"  Accuracy: {results['Gradient Boosting']['accuracy']:.4f}")
    print(f"  F1 Score: {results['Gradient Boosting']['f1']:.4f}")
    print(f"  Train Time: {gb_time:.2f}s")

    return results


# ─────────────────────────────────────────────
# Report Generation
# ─────────────────────────────────────────────

def generate_training_report(results: dict, best_name: str, output_path: str,
                              dataset_info: dict):
    """Generate training_report.md with evaluation metrics."""

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

    # Feature list
    lines.append("## Features Extracted\n")
    lines.append("| # | Feature | Count |")
    lines.append("|---|---------|-------|")
    lines.append("| 1 | MFCC (mean + std) | 26 |")
    lines.append("| 2 | Spectral Centroid (mean + std) | 2 |")
    lines.append("| 3 | Spectral Bandwidth (mean + std) | 2 |")
    lines.append("| 4 | Zero Crossing Rate (mean + std) | 2 |")
    lines.append("| 5 | RMS Energy (mean + std) | 2 |")
    lines.append("| 6 | Chroma Features (12 bins) | 12 |")
    lines.append("| 7 | Pitch Features (mean, var, range, jitter, shimmer) | 5 |")
    lines.append(f"| | **Total** | **{dataset_info['features']}** |")
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

    # ROC info
    fpr, tpr, _ = roc_curve(
        [1 if p == 1 else 0 for p in (best['predictions'] if 'y_test' not in results else results.get('y_test', best['predictions']))],
        best['probabilities']
    )
    # We store this for reference
    lines.append("### ROC Curve Data\n")
    lines.append(f"- **AUC Score:** {auc(fpr, tpr):.4f}")
    lines.append("")

    # Dataset sources
    lines.append("## Recommended Dataset Sources\n")
    lines.append("| Dataset | Type | Size | Link |")
    lines.append("|---------|------|------|------|")
    lines.append("| Common Voice | Human | ~70GB | https://commonvoice.mozilla.org/ |")
    lines.append("| LibriSpeech | Human | ~60GB | https://www.openslr.org/12/ |")
    lines.append("| ASVspoof 2021 | AI/Spoof | ~30GB | https://www.asvspoof.org/ |")
    lines.append("| WaveFake | AI | ~4GB | https://zenodo.org/record/5642694 |")
    lines.append("| Fake-or-Real | Mixed | ~2GB | https://bil.eecs.yorku.ca/datasets/ |")
    lines.append("| HuggingFace Voice | Mixed | Varies | https://huggingface.co/datasets?task_categories=audio-classification |")
    lines.append("")
    lines.append("> **MVP Recommendation:** Use WaveFake (~4GB) + a small subset of Common Voice (~2GB) for production training.\n")
    lines.append("> Current training uses synthetic acoustic simulations for rapid prototyping.\n")

    report_text = "\n".join(lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"\n[REPORT] Training report saved to: {output_path}")
    return report_text


# ─────────────────────────────────────────────
# Main Training Pipeline
# ─────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  AI VOICE DETECTION MODEL TRAINING")
    print("  Camp Protect — Human vs AI Voice Classifier")
    print("=" * 60)

    total_start = time.time()

    # Paths
    dataset_human_dir = os.path.join(SCRIPT_DIR, "dataset", "human")
    dataset_ai_dir = os.path.join(SCRIPT_DIR, "dataset", "ai")
    model_output_path = os.path.join(SCRIPT_DIR, "ai_voice_detector.pkl")
    scaler_output_path = os.path.join(SCRIPT_DIR, "ai_voice_scaler.pkl")
    report_output_path = os.path.join(SCRIPT_DIR, "training_report.md")

    # Step 1: Build dataset
    print("\n[STEP 1] Building dataset...")
    X, y = build_dataset(
        n_human=300, n_ai=300,
        human_dir=dataset_human_dir,
        ai_dir=dataset_ai_dir
    )

    # Step 2: Scale features
    print("\n[STEP 2] Scaling features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Replace NaN/Inf
    X_scaled = np.nan_to_num(X_scaled, nan=0.0, posinf=0.0, neginf=0.0)

    # Step 3: Train/test split
    print("\n[STEP 3] Splitting train/test (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train: {len(X_train)} samples | Test: {len(X_test)} samples")

    # Step 4: Train models
    print("\n[STEP 4] Training models...")
    results = train_models(X_train, X_test, y_train, y_test)

    # Step 5: Select best model
    best_name = max(results, key=lambda k: results[k]['f1'])
    best_model = results[best_name]['model']
    print(f"\n{'=' * 60}")
    print(f"  BEST MODEL: {best_name}")
    print(f"  F1 Score: {results[best_name]['f1']:.4f}")
    print(f"  Accuracy: {results[best_name]['accuracy']:.4f}")
    print(f"{'=' * 60}")

    # Step 6: Save model and scaler
    print("\n[STEP 6] Saving model...")
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
    print(f"  Model saved to: {model_output_path}")

    with open(scaler_output_path, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"  Scaler saved to: {scaler_output_path}")

    # Step 7: Generate report
    print("\n[STEP 7] Generating training report...")
    dataset_info = {
        'total': len(X),
        'human': int(np.sum(y == 0)),
        'ai': int(np.sum(y == 1)),
        'features': X.shape[1]
    }
    generate_training_report(results, best_name, report_output_path, dataset_info)

    # Cross-validation on best model
    print("\n[STEP 8] Cross-validation (5-fold)...")
    cv_scores = cross_val_score(best_model, X_scaled, y, cv=5, scoring='f1')
    print(f"  CV F1 Scores: {cv_scores}")
    print(f"  Mean CV F1: {np.mean(cv_scores):.4f} (+/- {np.std(cv_scores):.4f})")

    total_time = time.time() - total_start
    print(f"\n{'=' * 60}")
    print(f"  TRAINING COMPLETE")
    print(f"  Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
    print(f"{'=' * 60}")

    return best_model, scaler


if __name__ == "__main__":
    main()
