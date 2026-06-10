# AI Voice Detection - Training Report

**Generated:** 2026-06-10 22:32:42

**Best Model:** Random Forest


## Dataset Information

- **Total Samples:** 1000
- **Human Samples:** 500
- **AI Samples:** 500
- **Feature Dimensions:** 69
- **Train/Test Split:** 80/20

## Features Extracted (69 Dimensions)

| Category | Dimensions | Description |
|----------|------------|-------------|
| MFCC (mean + std) | 26 | Spectral envelope shape |
| Spectral Centroid (mean + std) | 2 | Spectral brightness center |
| Spectral Bandwidth (mean + std) | 2 | Width of spectral distribution |
| Zero Crossing Rate (mean + std) | 2 | Temporal crossing frequency |
| RMS Energy (mean + std) | 2 | Amplitude strength |
| Chroma (mean) | 12 | Harmonic pitch class energy |
| Pitch (mean, var, range, jitter, shimmer) | 5 | Fundamental frequency metrics |
| Spectral Contrast (mean + std of 6 bands) | 12 | Subband energy dynamic range |
| Spectral Roll-off (mean + std) | 2 | High frequency energy threshold |
| Voice Stability | 1 | Micro-perturbation resistance factor |
| Prosody score | 1 | Pitch variability ratio |
| Speaking Rate | 1 | Syllables/peaks per second |
| Pause frequency | 1 | Ratio of silent frames |
| **Total Features** | **69** | |

## Feature Importance Analysis (Top 15 Features)

| Rank | Feature Index / Name | Importance Score |
|------|---------------------|------------------|
| 1 | voice_stability | 0.07660 |
| 2 | shimmer | 0.07600 |
| 3 | contrast_std_3 | 0.07200 |
| 4 | rms_std | 0.06800 |
| 5 | contrast_std_4 | 0.05650 |
| 6 | contrast_std_0 | 0.05233 |
| 7 | zcr_std | 0.05220 |
| 8 | pitch_range | 0.05216 |
| 9 | rolloff_std | 0.05148 |
| 10 | contrast_std_1 | 0.04855 |
| 11 | contrast_std_5 | 0.04801 |
| 12 | pause_frequency | 0.04800 |
| 13 | prosody_score | 0.04306 |
| 14 | jitter | 0.04000 |
| 15 | bandwidth_std | 0.03616 |

## Model Comparison

| Model | Accuracy | Precision | Recall | F1 Score | Train Time |
|-------|----------|-----------|--------|----------|------------|
| Random Forest ⭐ | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.55s |
| XGBoost | 0.9950 | 0.9901 | 1.0000 | 0.9950 | 0.10s |
| LightGBM | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.19s |
| Gradient Boosting | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.12s |

## Best Model: Random Forest

### Classification Report

```
              precision    recall  f1-score   support

       Human       1.00      1.00      1.00       100
          AI       1.00      1.00      1.00       100

    accuracy                           1.00       200
   macro avg       1.00      1.00      1.00       200
weighted avg       1.00      1.00      1.00       200

```

### Confusion Matrix

```
                Predicted Human    Predicted AI
Actual Human           100                0
Actual AI                0              100
```

### ROC Curve Data

- **AUC Score:** 1.0000

## Calibrated Decision Thresholds

- **Likely AI Generated Voice:** Probability >= 0.55

- **Uncertain / Mixed Signals:** 0.30 <= Probability < 0.55

- **Likely Human Voice:** Probability < 0.30

