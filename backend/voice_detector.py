"""
voice_detector.py - AI Voice Detection Module
Extracts acoustic features and classifies voice as Human, AI Generated, or Uncertain.
"""

import os
import io
import wave
import numpy as np
from scipy.fftpack import dct

# Try importing av for advanced container formats decoding
try:
    import av
    AV_AVAILABLE = True
except ImportError:
    AV_AVAILABLE = False


def decode_audio_to_pcm(file_bytes: bytes) -> bytes:
    """
    Decode audio of any container format (WAV, MP3, M4A, etc.) to 16kHz, 16-bit mono PCM.
    """
    if not file_bytes:
        return b""
        
    if AV_AVAILABLE:
        try:
            input_file = io.BytesIO(file_bytes)
            container = av.open(input_file)
            audio_stream = next((s for s in container.streams if s.type == 'audio'), None)
            
            if not audio_stream:
                raise ValueError("No audio stream found in container")
                
            resampler = av.AudioResampler(
                format='s16',
                layout='mono',
                rate=16000
            )
            
            pcm_data = bytearray()
            for frame in container.decode(audio_stream):
                resampled_frames = resampler.resample(frame)
                for rf in resampled_frames:
                    pcm_data.extend(rf.planes[0].to_ndarray().tobytes())
            return bytes(pcm_data)
        except Exception as e:
            print(f"[Audio Decoding Warning] PyAV failed: {e}. Falling back to wave parser...")
            
    # Fallback to standard wave library if it is a WAV file
    try:
        with wave.open(io.BytesIO(file_bytes), 'rb') as wav:
            params = wav.getparams()
            raw = wav.readframes(params.nframes)
            
            # If already 16kHz 16-bit mono
            if params.framerate == 16000 and params.sampwidth == 2 and params.nchannels == 1:
                return raw
                
            # If different sample rate/channels, convert it simply
            signal = np.frombuffer(raw, dtype=np.int16)
            if params.nchannels > 1:
                # Average channels
                signal = signal.reshape(-1, params.nchannels).mean(axis=1).astype(np.int16)
                
            # Resample if needed using basic linear interpolation
            if params.framerate != 16000:
                duration = len(signal) / params.framerate
                new_len = int(duration * 16000)
                signal = np.interp(
                    np.linspace(0, len(signal) - 1, new_len),
                    np.arange(len(signal)),
                    signal
                ).astype(np.int16)
                
            return signal.tobytes()
    except Exception as ex:
        print(f"[Audio Decoding Error] Fallback wave decoder failed: {ex}")
        return b""


def extract_acoustic_features(signal: np.ndarray, sr: int = 16000) -> dict:
    """
    Extract pitch variance, jitter, shimmer, speaking rate, and other voice features.
    """
    if len(signal) == 0:
        return {
            "pitch_variance": 0.0,
            "speaking_rate": 0.0,
            "pause_frequency": 0.0,
            "energy_variation": 0.0,
            "spectral_entropy": 0.0,
            "jitter": 0.0,
            "shimmer": 0.0,
            "voice_stability": 0.0,
            "breathing_detected": 0.0,
            "prosody_score": 0.0,
            "mfcc_variance": 0.0
        }
        
    # Frame-based calculations (25ms window, 10ms step)
    frame_len = int(0.025 * sr)
    frame_step = int(0.010 * sr)
    
    if len(signal) < frame_len:
        signal = np.pad(signal, (0, frame_len - len(signal)), mode='constant')
        
    num_frames = 1 + (len(signal) - frame_len) // frame_step
    frames = []
    for i in range(num_frames):
        start = i * frame_step
        frames.append(signal[start:start+frame_len])
    frames = np.array(frames)
    
    # 1. Energy
    energies = np.sum(frames ** 2, axis=1)
    energy_variation = float(np.var(energies)) if len(energies) > 1 else 0.0
    
    # 2. Pitch estimation via Autocorrelation (F0)
    # Humans speak generally between 60Hz and 350Hz
    min_lag = int(sr / 350)
    max_lag = int(sr / 60)
    
    pitches = []
    periods = []
    amplitudes = []
    
    for f in frames:
        corr = np.correlate(f, f, mode='full')
        corr = corr[len(corr)//2:]
        
        if len(corr) > max_lag:
            lag_region = corr[min_lag:max_lag]
            if len(lag_region) > 0 and np.max(lag_region) > 0.05 * corr[0]:
                peak_lag = np.argmax(lag_region) + min_lag
                f0 = sr / peak_lag
                pitches.append(f0)
                periods.append(peak_lag)
                amplitudes.append(float(np.max(f) - np.min(f)))
            else:
                pitches.append(0.0)
                periods.append(0.0)
                amplitudes.append(0.0)
        else:
            pitches.append(0.0)
            periods.append(0.0)
            amplitudes.append(0.0)
            
    pitches = np.array(pitches)
    valid_pitches = pitches[pitches > 0]
    pitch_variance = float(np.var(valid_pitches)) if len(valid_pitches) > 1 else 0.0
    
    # 3. Jitter
    valid_periods = [p for p in periods if p > 0]
    if len(valid_periods) > 1:
        diff_periods = np.abs(np.diff(valid_periods))
        mean_period = np.mean(valid_periods)
        jitter = float(np.mean(diff_periods) / mean_period) if mean_period > 0 else 0.0
    else:
        jitter = 0.0
        
    # 4. Shimmer
    valid_amps = [a for a in amplitudes if a > 0]
    if len(valid_amps) > 1:
        diff_amps = np.abs(np.diff(valid_amps))
        mean_amp = np.mean(valid_amps)
        shimmer = float(np.mean(diff_amps) / mean_amp) if mean_amp > 0 else 0.0
    else:
        shimmer = 0.0
        
    # 5. Speaking rate and Pause frequency
    mean_energy = np.mean(energies)
    silence_threshold = 0.05 * mean_energy if mean_energy > 0 else 0.0001
    silent_frames = energies < silence_threshold
    pause_frequency = float(np.mean(silent_frames))
    
    energy_peaks = 0
    in_peak = False
    for i, e in enumerate(energies):
        if e > mean_energy and not silent_frames[i]:
            if not in_peak:
                energy_peaks += 1
                in_peak = True
        else:
            in_peak = False
            
    duration_s = len(signal) / sr
    speaking_rate = float(energy_peaks / duration_s) if duration_s > 0 else 0.0
    
    # 6. Spectral Entropy
    nfft = 512
    entropies = []
    for f in frames:
        fft_vals = np.fft.rfft(f, nfft)
        pow_vals = np.abs(fft_vals)**2
        sum_pow = np.sum(pow_vals)
        if sum_pow > 0:
            p = pow_vals / sum_pow
            p = np.where(p == 0, np.finfo(float).eps, p)
            entropy = -np.sum(p * np.log2(p))
            entropies.append(entropy)
        else:
            entropies.append(0.0)
    spectral_entropy = float(np.mean(entropies))
    
    # 7. Voice Stability
    stability = 1.0 / (1.0 + jitter * 6.0 + shimmer * 3.0 + (pitch_variance / 2000.0))
    voice_stability = float(np.clip(stability, 0.0, 1.0))
    
    # 8. Breathing detection (ZCR in silences)
    zcrs = []
    for i, f in enumerate(frames):
        if silent_frames[i]:
            zcr = np.mean(np.abs(np.diff(np.sign(f)))) / 2
            zcrs.append(zcr)
    breathing_detected = float(np.mean(zcrs)) if len(zcrs) > 0 else 0.0
    
    # 9. Prosody patterns
    prosody_score = float(np.std(valid_pitches) / (np.mean(valid_pitches) + 1e-5)) if len(valid_pitches) > 0 else 0.0
    
    # 10. MFCC features variance
    try:
        from model.feature_extractor import extract_mfcc
        mfccs = extract_mfcc(signal, sr=sr)
        mfcc_variance = float(np.var(mfccs)) if mfccs.size > 0 else 0.0
    except Exception:
        mfcc_variance = 0.0
        
    return {
        "pitch_variance": round(pitch_variance, 2),
        "speaking_rate": round(speaking_rate, 2),
        "pause_frequency": round(pause_frequency, 2),
        "energy_variation": round(energy_variation, 4),
        "spectral_entropy": round(spectral_entropy, 2),
        "jitter": round(jitter, 4),
        "shimmer": round(shimmer, 4),
        "voice_stability": round(voice_stability, 2),
        "breathing_detected": round(breathing_detected, 3),
        "prosody_score": round(prosody_score, 2),
        "mfcc_variance": round(mfcc_variance, 2)
    }


def classify_voice_from_features(features: dict) -> tuple[float, str, float]:
    """
    Heuristic scoring using audio features to classify voice:
    Returns (ai_voice_score, classification, confidence)
    """
    score = 0.0
    
    # 1. Monotone voice detection (Low Pitch Variance)
    if features["pitch_variance"] < 120:
        score += 35
    elif features["pitch_variance"] < 300:
        score += 15
        
    # 2. Perfect pitch period regularity (Very low jitter & shimmer)
    if features["jitter"] < 0.006:
        score += 20
    elif features["jitter"] < 0.012:
        score += 10
        
    # 3. Voice stability (smooth artificial interpolation)
    if features["voice_stability"] > 0.85:
        score += 25
    elif features["voice_stability"] > 0.70:
        score += 10
        
    # 4. Absence of breathing indicators in silent frames
    if features["breathing_detected"] < 0.015:
        score += 20
    elif features["breathing_detected"] < 0.035:
        score += 10
        
    # Cap score at 100
    ai_score = float(np.clip(score, 0.0, 100.0))
    
    # Classify voice and confidence score
    if ai_score >= 61:
        classification = "Likely AI Generated"
        confidence = float(np.clip(50 + (ai_score - 60) * 1.25, 55.0, 97.0))
    elif ai_score >= 31:
        classification = "Uncertain"
        confidence = float(50.0 + (50 - abs(ai_score - 45)) * 0.4)
    else:
        classification = "Likely Human"
        confidence = float(np.clip(50 + (30 - ai_score) * 1.5, 55.0, 98.0))
        
    return round(ai_score, 1), classification, round(confidence, 1)


class AIVoiceDetector:
    def __init__(self):
        # We try to load PyTorch engine if available
        self.pytorch_loaded = False
        try:
            from model.deepfake_classifier import DeepfakeInference
            self.pytorch_detector = DeepfakeInference()
            if hasattr(self.pytorch_detector, 'model_loaded') and self.pytorch_detector.model_loaded:
                self.pytorch_loaded = True
        except Exception as e:
            print(f"[AIVoiceDetector] PyTorch model initialization bypassed: {e}")
            self.pytorch_detector = None

    def analyze_audio_bytes(self, file_bytes: bytes) -> dict:
        """
        Accepts any audio file format bytes, decodes it, extracts features,
        and computes AI Voice Detection report.
        """
        pcm_bytes = decode_audio_to_pcm(file_bytes)
        if not pcm_bytes:
            # Fallback for empty or corrupt audio
            return {
                "ai_voice_score": 0.0,
                "risk_level": "Likely Human",
                "voice_classification": "Likely Human",
                "confidence_score": 90.0,
                "human_voice_probability": 100.0,
                "ai_voice_probability": 0.0,
                "features": extract_acoustic_features(np.zeros(0)),
                "reasoning": "Could not extract audio features. Defaulting to safe human classification."
            }

        signal = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        features = extract_acoustic_features(signal, sr=16000)

        # 1. Run classifier
        if self.pytorch_loaded:
            try:
                raw_score = self.pytorch_detector.predict_pcm(pcm_bytes)
                ai_score = round(raw_score * 100.0, 1)
                
                # Classify based on score
                if ai_score >= 61:
                    classification = "Likely AI Generated"
                    confidence = round(50.0 + (ai_score - 60) * 1.2, 1)
                elif ai_score >= 31:
                    classification = "Uncertain"
                    confidence = round(50.0 + (50 - abs(ai_score - 45)) * 0.4, 1)
                else:
                    classification = "Likely Human"
                    confidence = round(50.0 + (30 - ai_score) * 1.5, 1)
            except Exception as e:
                print(f"[AIVoiceDetector Warn] PyTorch run failed: {e}. Falling back to features.")
                ai_score, classification, confidence = classify_voice_from_features(features)
        else:
            ai_score, classification, confidence = classify_voice_from_features(features)

        # Calculate probabilities
        ai_prob = ai_score
        human_prob = round(100.0 - ai_prob, 1)

        # Generate reasoning based on features
        reasons = []
        if features["pitch_variance"] < 150:
            reasons.append("Flat pitch variance indicating monotone/synthetic expression.")
        else:
            reasons.append("Natural pitch variations matching human speech patterns.")

        if features["voice_stability"] > 0.8:
            reasons.append("Extremely high voice stability matching digital signal smoothing.")
        else:
            reasons.append("Dynamic voice amplitude fluctuations matching natural respiration.")

        if features["breathing_detected"] < 0.01:
            reasons.append("Absence of natural breathing/respiration noise signatures.")
        else:
            reasons.append("Natural breathing/sighing pauses detected between phrases.")

        reasoning = " ".join(reasons)

        return {
            "ai_voice_score": ai_score,
            "risk_level": "Likely AI Generated" if ai_score >= 61 else ("Uncertain" if ai_score >= 31 else "Likely Human"),
            "voice_classification": classification,
            "confidence_score": confidence,
            "human_voice_probability": human_prob,
            "ai_voice_probability": ai_prob,
            "features": features,
            "reasoning": reasoning
        }
