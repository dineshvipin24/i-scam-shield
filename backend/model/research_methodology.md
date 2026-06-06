# Research Methodology: Voice Deepfake & AI Speech Detection

This document outlines the theoretical design, signal processing pipeline, model architecture, dataset selection, and evaluation criteria for the **AI Voice Detection Module** integrated into the **Camp Protect (AI Scam Shield)** platform.

---

## 1. Architectural Pipeline

The system employs a hybrid approach combining **neural feature representation** (using a 1-Dimensional Convolutional Neural Network) and **acoustic feature variance heuristics**.

```
                           +------------------------+
                           |  Audio Signal (Input)  |
                           +-----------+------------+
                                       |
                                       v
                           +-----------+------------+
                           |  Short-Time Framing   |
                           +-----------+------------+
                                       |
                  +--------------------+--------------------+
                  |                                         |
                  v                                         v
     +------------+------------+               +------------+------------+
     |   MFCC Feature Extraction|               | Acoustic Feature Mining |
     +------------+------------+               +------------+------------+
                  |                                         |
                  | [13 x Seq_Len]                          | - Pitch Variance
                  v                                         | - Voice Stability
     +------------+------------+                            | - Jitter & Shimmer
     | 1D-CNN Deepfake Engine  |                            | - Pause Frequency
     +------------+------------+                            | - Zero Crossing Rate
                  |                                         |
                  v [AI Probability]                        v [Heuristic Weight]
     +------------+-----------------------------------------+------------+
     |                   Combined Voice Scoring Engine                    |
     +----------------------------------+---------------------------------+
                                        |
                                        v
                            +-----------+------------+
                            |     AI Voice Score     |
                            |       (0 - 100)        |
                            +------------------------+
```

---

## 2. Audio Feature Extraction Formulas

### A. Mel-Frequency Cepstral Coefficients (MFCC)
MFCCs model the human auditory system's response by mapping frequencies to the Mel scale:
$$m = 2595 \log_{10}\left(1 + \frac{f}{700}\right)$$
We apply Discrete Cosine Transform (DCT) to the log-energy output of the Mel filterbank to obtain 13 decorrelated cepstral coefficients per frame.

### B. Pitch (Fundamental Frequency $F_0$) & Pitch Variance
We calculate $F_0$ using the short-term autocorrelation function $R_k(t)$ of the speech frame $s(n)$:
$$R_k(t) = \sum_{n=0}^{N-1-k} s(n) s(n+k)$$
We search for the maximum peak of $R_k(t)$ in the human pitch range (lag index $k$ corresponding to $60\text{ Hz} \le F_0 \le 350\text{ Hz}$).
*   **Pitch Variance**: The variance of the estimated $F_0$ across voiced frames. Highly monotone, artificially synthesized voices show extremely low pitch variance compared to human prosody.

### C. Jitter (Frequency Instability)
Jitter represents cycles-to-cycle perturbations in pitch periods ($T_i = 1/F_{0,i}$):
$$\text{Jitter (Absolute)} = \frac{1}{N-1} \sum_{i=1}^{N-1} |T_i - T_{i+1}|$$
Natural human speech exhibits micro-vibrations (jitter $> 0.5\%$), whereas synthesized voice models generated from linear text-to-speech vocoders have perfectly constant pitch periods (jitter $\to 0\%$).

### D. Shimmer (Amplitude Instability)
Shimmer represents cycle-to-cycle variation in the peak-to-peak amplitude $A_i$:
$$\text{Shimmer} = \frac{\frac{1}{N-1} \sum_{i=1}^{N-1} |A_i - A_{i+1}|}{\frac{1}{N} \sum_{i=1}^{N} A_i}$$
Synthetic vocoders produce uniform waveforms lacking organic amplitude decay.

### E. Voice Stability
Calculated as the inverse function of pitch variance, jitter, and shimmer:
$$\text{Stability} = \frac{1}{1 + \alpha \cdot \text{Jitter} + \beta \cdot \text{Shimmer} + \gamma \cdot \text{Var}(F_0)}$$

### F. Spectral Entropy
Measures the randomness/complexity of the power spectrum $P(\omega)$:
$$H = -\sum_{i=1}^{K} p_i \log_2(p_i), \quad \text{where } p_i = \frac{P(\omega_i)}{\sum_j P(\omega_j)}$$
AI voice generators tend to leave high-frequency artifacts that shift the spectral entropy fingerprint compared to microphone-captured human voice.

---

## 3. Dataset Recommendations

To train and evaluate the model to production grade, we recommend benchmarking on the following public databases:

1.  **ASVspoof 2019 / 2021 (Logical Access)**:
    *   The standard benchmark dataset containing genuine human speech and synthetic speech generated by 17 different Text-to-Speech (TTS) and Voice Conversion (VC) algorithms.
2.  **WaveFake Dataset**:
    *   A multi-lingual dataset containing deepfake audio synthesized using advanced neural architectures like MelGAN, WaveGlow, and Parallel WaveGAN.
3.  **LJSpeech Dataset**:
    *   13,100 short audio clips of a single speaker reading passages from non-fiction books (used to build clean baseline human models).

---

## 4. Evaluation Metrics & Confusion Matrix

To evaluate the classification performance, we define the following confusion matrix:

| Actual \ Predicted | Predicted Human | Predicted AI / Deepfake |
| :--- | :--- | :--- |
| **Actual Human** | **True Negative (TN)** | **False Positive (FP)** (False Alarm) |
| **Actual AI** | **False Negative (FN)** (Missed Detection) | **True Positive (TP)** |

### Formulas

*   **Precision (Positive Predictive Value)**:
    $$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}$$
    *Ensures that a voice flagged as AI is indeed synthetic.*

*   **Recall (Sensitivity / Detection Rate)**:
    $$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$$
    *Ensures that all synthetic deepfake calls are captured.*

*   **F1 Score**:
    $$\text{F1} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$
    *The harmonic mean of precision and recall.*

*   **Equal Error Rate (EER)**:
    The threshold point where the False Acceptance Rate (FAR) equals the False Rejection Rate (FRR). A lower EER indicates superior robustness.
