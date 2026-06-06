"""
test_voice_detector.py - Unit test and validation procedure for the AI Voice Detector
"""

import numpy as np
from voice_detector import extract_acoustic_features, classify_voice_from_features, AIVoiceDetector

def test_feature_extraction():
    print("[TEST] Running feature extraction on mock signals...")
    
    # 1. Test empty signal
    empty_signal = np.zeros(0)
    empty_features = extract_acoustic_features(empty_signal)
    assert empty_features["pitch_variance"] == 0.0
    assert empty_features["voice_stability"] == 0.0
    print("  ✓ Empty signal handled correctly.")
    
    # 2. Test synthetic-like stable tone (sine wave)
    sr = 16000
    duration = 1.5 # seconds
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # 150 Hz pure tone (constant pitch and amplitude)
    sine_signal = 0.5 * np.sin(2 * np.pi * 150 * t)
    
    features = extract_acoustic_features(sine_signal, sr=sr)
    print(f"  Extracted Features for Pure Sine Tone:")
    print(f"    - Pitch Variance: {features['pitch_variance']} Hz²")
    print(f"    - Voice Stability: {features['voice_stability']}")
    print(f"    - Jitter: {features['jitter']}")
    print(f"    - Shimmer: {features['shimmer']}")
    print(f"    - Speaking Rate: {features['speaking_rate']} syll/s")
    print(f"    - Pause Frequency: {features['pause_frequency']}")
    
    # A constant sine tone has zero pitch variance and high stability
    assert features["pitch_variance"] < 10.0
    assert features["voice_stability"] > 0.8
    print("  ✓ Synthetic tone analysis matched expectation.")
    
    # 3. Test classification score
    score, classification, confidence = classify_voice_from_features(features)
    print(f"  Classification Output:")
    print(f"    - AI Score: {score}")
    print(f"    - Label: {classification}")
    print(f"    - Confidence: {confidence}%")
    
    assert score >= 60.0
    assert "AI" in classification
    print("  ✓ Classification rule verified successfully.")

def test_detector_class():
    print("[TEST] Initializing AIVoiceDetector class...")
    detector = AIVoiceDetector()
    
    # Mock wave bytes
    import struct
    # 1 second of 16kHz, 16-bit mono silence PCM
    pcm_data = struct.pack("<16000h", *[0]*16000)
    
    report = detector.analyze_audio_bytes(pcm_data)
    print("  Report Output Keys:", list(report.keys()))
    assert "ai_voice_score" in report
    assert "human_voice_probability" in report
    assert "ai_voice_probability" in report
    assert "voice_classification" in report
    assert "features" in report
    print("  ✓ Detector wrapper verified successfully.")

if __name__ == "__main__":
    print("====================================================")
    print("CAMP PROTECT - AI VOICE DETECTION MODULE TEST SUITE")
    print("====================================================")
    try:
        test_feature_extraction()
        print("")
        test_detector_class()
        print("\n[SUCCESS] All Voice Detection tests passed successfully!")
    except AssertionError as e:
        print(f"\n[FAILURE] Assertion failed: {e}")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during tests: {e}")
