# AI Voice Detection Model Training Guide

## Overview

This guide helps you train a machine learning model that can **detect and classify voices** into three categories:

1. **Human Voice** - Natural human speech
2. **AI-Generated Voice** - Synthetically generated voices (ElevenLabs, Google TTS, Amazon Polly, etc.)
3. **Deepfake/Synthetic Voice** - Vocoder-based voice conversion and deepfake audio

## Quick Start

### Step 1: Setup Directory Structure

```bash
cd backend/model
python prepare_voice_data.py --setup
```

This creates an organized folder structure in `voice_data/` for different voice types:
```
voice_data/
├── human_voices/          # Your human voice samples
├── elevenlabs/           # ElevenLabs generated voices
├── google_tts/           # Google TTS voices
├── amazon_polly/         # Amazon Polly voices
├── other_tts/            # Other TTS services
└── deepfake_synthetic/   # Deepfake samples
```

### Step 2: Add Your Voice Data

Copy your audio files to the appropriate directories:

#### For ElevenLabs voices:
```bash
# Copy your ElevenLabs audio files to:
# voice_data/elevenlabs/
# Example: ElevenLabs_2026-06-07T13_01_52_Roger.mp3
```

#### For human voices:
```bash
# Add any human voice samples to:
# voice_data/human_voices/
# Can include: interviews, recordings, podcasts, etc.
```

### Step 3: Build the Dataset

```bash
python prepare_voice_data.py --build-dataset
```

This will:
- Scan all voice data directories
- Extract audio features (MFCC) from each file
- Organize features into a training dataset
- Display dataset statistics

### Step 4: Train the Model

```bash
python prepare_voice_data.py --train-model
```

This will:
- Load the dataset
- Train a 3-class deep learning classifier
- Validate on test data
- Save the trained model as `ai_voice_model.pth`

## Detailed Workflow

### 1. Organize Your Audio Files

#### Option A: Automatic Organization
```bash
python prepare_voice_data.py --organize /path/to/audio/files --label ai --source-type elevenlabs
```

#### Option B: Manual Organization
Simply copy files to the correct directories based on their source.

### 2. Dataset Building

The dataset builder:
- Loads audio files in WAV, MP3, OGG, FLAC formats
- Extracts MFCC (Mel-Frequency Cepstral Coefficients) features
- Normalizes audio to 16 kHz sample rate
- Creates fixed-size feature vectors (13 features × 200 frames)
- Balances classes for better training

Example output:
```
Dataset Statistics:
  Total samples: 600
  Distribution:
    Human            200 (33.3%)
    AI-Generated     200 (33.3%)
    Deepfake/Synthetic 200 (33.3%)
  
  Total duration: 1843.5 seconds
  Average duration: 3.07 seconds
```

### 3. Model Architecture

The model uses a **3-layer Convolutional Neural Network (CNN)**:

```
Input (13 features × 200 frames)
  ↓
Conv1D(32 filters) → BatchNorm → ReLU → MaxPool
  ↓
Conv1D(64 filters) → BatchNorm → ReLU → MaxPool
  ↓
Conv1D(128 filters) → BatchNorm → ReLU → MaxPool
  ↓
Global Average Pooling
  ↓
Dense(64) → ReLU → Dropout → Dense(32) → ReLU → Dropout
  ↓
Output (3 classes)
```

### 4. Training Configuration

Default settings (customizable):
- **Epochs:** 30
- **Batch size:** 32
- **Learning rate:** 0.001
- **Loss function:** CrossEntropyLoss
- **Optimizer:** Adam with weight decay
- **Early stopping:** patience=10 epochs

## Using the Trained Model

### In Python Code

```python
from backend.model.ai_voice_detector import AIVoiceDetector

# Initialize detector
detector = AIVoiceDetector()

# Predict from audio bytes
prediction, probabilities = detector.predict_pcm(pcm_bytes)

print(f"Prediction: {prediction}")
print(f"Probabilities:")
print(f"  Human: {probabilities['Human']:.2%}")
print(f"  AI-Generated: {probabilities['AI-Generated']:.2%}")
print(f"  Deepfake/Synthetic: {probabilities['Deepfake/Synthetic']:.2%}")
```

### In Your Android App

Integrate the model into your call monitoring service:

```kotlin
// In CallScreeningServiceImpl.kt
val audioBytes = getAudioFromCall()
val prediction = aiVoiceDetector.predictPcm(audioBytes)

if (prediction.label == "AI-Generated" || prediction.label == "Deepfake/Synthetic") {
    // Alert user - potential scam
    showFraudAlert("AI-generated voice detected!")
}
```

## Advanced Configuration

### Train with Custom Parameters

```bash
python train_ai_voice_model.py \
  --dataset-dir voice_dataset \
  --epochs 50 \
  --batch-size 64 \
  --learning-rate 0.0005 \
  --device cuda
```

### Train from Specific Audio Directory

```bash
python prepare_voice_data.py \
  --organize /path/to/my/audio \
  --label ai \
  --source-type elevenlabs \
  --build-dataset \
  --train-model
```

## Data Requirements

### Minimum Dataset
- 50+ samples per class (150 total)
- At least 30 seconds of audio per class

### Recommended Dataset
- 200+ samples per class (600 total)
- At least 10 minutes of audio per class
- Diverse speaker demographics
- Various audio qualities and background noise levels

### Data Characteristics

**Human voices should include:**
- Natural speech patterns
- Varied intonation and inflection
- Background conversation
- Different emotional tones

**AI-Generated voices should include:**
- ElevenLabs samples (various languages/accents)
- Google TTS, Amazon Polly
- Other commercial TTS systems
- Different generation settings

**Deepfake/Synthetic samples should include:**
- Voice cloning results
- Vocoder-based synthesis
- Known deepfake samples

## Troubleshooting

### Out of Memory Error
- Reduce `batch_size` to 16 or 8
- Use smaller `seq_len` (180 instead of 200)
- Use CPU instead of GPU

### Poor Model Accuracy
- Add more training data (especially balanced classes)
- Increase `epochs` to 50-100
- Reduce `learning_rate` to 0.0001
- Check for audio quality issues

### Audio File Not Loaded
- Verify file format (WAV, MP3, OGG, FLAC supported)
- Check audio sample rate (will be resampled to 16 kHz)
- Ensure mono audio or stereo will be converted to mono

## Integration with Existing Deepfake Detector

The new AI voice detector **complements** your existing deepfake detector:

```python
from deepfake_classifier import DeepfakeInference
from ai_voice_detector import AIVoiceDetector

# Run both classifiers
deepfake_score = deepfake_detector.predict_pcm(audio_bytes)
voice_type, probabilities = ai_detector.predict_pcm(audio_bytes)

# Combined verdict
is_suspicious = (
    (deepfake_score > 0.7) or 
    (probabilities['AI-Generated'] > 0.6) or
    (probabilities['Deepfake/Synthetic'] > 0.6)
)
```

## Files Created

- `ai_voice_detector.py` - Main inference class
- `ai_voice_dataset_builder.py` - Dataset preparation utility
- `train_ai_voice_model.py` - Training script
- `prepare_voice_data.py` - Data organization and workflow utility
- `ai_voice_model.pth` - Trained model weights (after training)

## Next Steps

1. ✅ Setup directories: `python prepare_voice_data.py --setup`
2. 📁 Add your voice data to appropriate folders
3. 🔧 Build dataset: `python prepare_voice_data.py --build-dataset`
4. 🚀 Train model: `python prepare_voice_data.py --train-model`
5. 📊 Evaluate accuracy and adjust as needed
6. 🔌 Integrate into your Android app

## References

- MFCC Feature Extraction: https://en.wikipedia.org/wiki/Mel-frequency_cepstrum
- PyTorch Conv1D: https://pytorch.org/docs/stable/generated/torch.nn.Conv1d.html
- Audio Processing: https://librosa.org/doc/latest/
