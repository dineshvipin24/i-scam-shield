# AI Voice Detection - Training Report

**Generated:** 2026-06-10 12:12:49

**Best Model:** Random Forest


## Dataset Information

- **Total Samples:** 600
- **Human Samples:** 300
- **AI Samples:** 300
- **Feature Dimensions:** 51
- **Train/Test Split:** 80/20

## Features Extracted

| # | Feature | Count |
|---|---------|-------|
| 1 | MFCC (mean + std) | 26 |
| 2 | Spectral Centroid (mean + std) | 2 |
| 3 | Spectral Bandwidth (mean + std) | 2 |
| 4 | Zero Crossing Rate (mean + std) | 2 |
| 5 | RMS Energy (mean + std) | 2 |
| 6 | Chroma Features (12 bins) | 12 |
| 7 | Pitch Features (mean, var, range, jitter, shimmer) | 5 |
| | **Total** | **51** |

## Model Comparison

| Model | Accuracy | Precision | Recall | F1 Score | Train Time |
|-------|----------|-----------|--------|----------|------------|
| Random Forest ⭐ | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.22s |
| XGBoost | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.09s |
| LightGBM | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.04s |
| Gradient Boosting | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.58s |

## Best Model: Random Forest

### Classification Report

```
              precision    recall  f1-score   support

       Human       1.00      1.00      1.00        60
          AI       1.00      1.00      1.00        60

    accuracy                           1.00       120
   macro avg       1.00      1.00      1.00       120
weighted avg       1.00      1.00      1.00       120

```

### Confusion Matrix

```
                Predicted Human    Predicted AI
Actual Human            60                0
Actual AI                0               60
```

### ROC Curve Data

- **AUC Score:** 1.0000

## Recommended Dataset Sources

| Dataset | Type | Size | Link |
|---------|------|------|------|
| Common Voice | Human | ~70GB | https://commonvoice.mozilla.org/ |
| LibriSpeech | Human | ~60GB | https://www.openslr.org/12/ |
| ASVspoof 2021 | AI/Spoof | ~30GB | https://www.asvspoof.org/ |
| WaveFake | AI | ~4GB | https://zenodo.org/record/5642694 |
| Fake-or-Real | Mixed | ~2GB | https://bil.eecs.yorku.ca/datasets/ |
| HuggingFace Voice | Mixed | Varies | https://huggingface.co/datasets?task_categories=audio-classification |

> **MVP Recommendation:** Use WaveFake (~4GB) + a small subset of Common Voice (~2GB) for production training.

> Current training uses synthetic acoustic simulations for rapid prototyping.
