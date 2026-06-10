"""
voice_detector.py - AI Voice Detection Module
Extracts acoustic features and classifies voice as Human, AI Generated, or Uncertain.
"""

import os
import io
import wave
import numpy as np
try:
    from scipy.fftpack import dct
except ImportError:
    dct = None

# Try importing av for advanced container formats decoding
try:
    import av
    AV_AVAILABLE = True
except ImportError:
    AV_AVAILABLE = False


def decode_audio_to_pcm(file_bytes: bytes) -> bytes:
    """
    Decode audio of any container format (WAV, MP3, M4A, etc.) to 16kHz, 16-bit mono PCM.
    Uses multiple fallback strategies to ensure MP3/M4A files are decoded.
    """
    if not file_bytes:
        return b""

    # Strategy 1: PyAV (handles all formats if installed)
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
            if len(pcm_data) > 0:
                print(f"[Audio Decode] PyAV success: {len(pcm_data)} bytes PCM")
                return bytes(pcm_data)
            else:
                raise ValueError("PyAV returned empty audio")
        except Exception as e:
            print(f"[Audio Decode] PyAV failed: {e}. Trying next decoder...")

    # Strategy 2: soundfile (handles WAV, FLAC, OGG; limited MP3 support)
    try:
        import soundfile as sf
        audio_io = io.BytesIO(file_bytes)
        data, samplerate = sf.read(audio_io, dtype='int16')
        if len(data.shape) > 1:
            data = data.mean(axis=1).astype(np.int16)
        if samplerate != 16000:
            duration = len(data) / samplerate
            new_len = int(duration * 16000)
            data = np.interp(
                np.linspace(0, len(data) - 1, new_len),
                np.arange(len(data)), data
            ).astype(np.int16)
        if len(data) > 0:
            print(f"[Audio Decode] soundfile success: {len(data)*2} bytes PCM")
            return data.tobytes()
    except Exception as e:
        print(f"[Audio Decode] soundfile failed: {e}. Trying next decoder...")

    # Strategy 3: ffmpeg subprocess (universal decoder)
    try:
        import subprocess
        import sys
        import tempfile

        # Write input to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.audio') as tmp_in:
            tmp_in.write(file_bytes)
            tmp_in_path = tmp_in.name

        tmp_out_path = tmp_in_path + '.wav'

        try:
            # Try ffmpeg
            result = subprocess.run(
                ['ffmpeg', '-y', '-i', tmp_in_path,
                 '-ar', '16000', '-ac', '1', '-f', 's16le', '-acodec', 'pcm_s16le',
                 tmp_out_path],
                capture_output=True, timeout=30
            )
            if result.returncode == 0 and os.path.exists(tmp_out_path):
                with open(tmp_out_path, 'rb') as f:
                    pcm_data = f.read()
                if len(pcm_data) > 0:
                    print(f"[Audio Decode] ffmpeg success: {len(pcm_data)} bytes PCM")
                    return pcm_data
        except FileNotFoundError:
            print("[Audio Decode] ffmpeg not found. Trying next decoder...")
        except Exception as e:
            print(f"[Audio Decode] ffmpeg error: {e}")
        finally:
            for p in [tmp_in_path, tmp_out_path]:
                try:
                    if os.path.exists(p):
                        os.remove(p)
                except:
                    pass
    except Exception as e:
        print(f"[Audio Decode] ffmpeg strategy failed: {e}")

    # Strategy 4: pydub (if installed, handles MP3 natively)
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(io.BytesIO(file_bytes))
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        pcm_data = audio.raw_data
        if len(pcm_data) > 0:
            print(f"[Audio Decode] pydub success: {len(pcm_data)} bytes PCM")
            return pcm_data
    except Exception as e:
        print(f"[Audio Decode] pydub failed: {e}. Trying wave fallback...")

    # Strategy 5: Standard wave library (WAV only)
    try:
        with wave.open(io.BytesIO(file_bytes), 'rb') as wav:
            params = wav.getparams()
            raw = wav.readframes(params.nframes)
            
            if params.framerate == 16000 and params.sampwidth == 2 and params.nchannels == 1:
                return raw
                
            signal = np.frombuffer(raw, dtype=np.int16)
            if params.nchannels > 1:
                signal = signal.reshape(-1, params.nchannels).mean(axis=1).astype(np.int16)
                
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
        print(f"[Audio Decode] Wave decoder failed: {ex}")

    # Strategy 6: Raw byte interpretation as last resort
    # If file starts with RIFF header, try to parse manually
    if file_bytes[:4] == b'RIFF':
        try:
            # Skip WAV header (typically 44 bytes) and treat rest as PCM
            pcm_data = file_bytes[44:]
            if len(pcm_data) > 1000:
                print(f"[Audio Decode] Raw RIFF fallback: {len(pcm_data)} bytes")
                return pcm_data
        except:
            pass

    print("[Audio Decode] ALL DECODERS FAILED. Returning empty audio.")
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
        # Priority chain: ML Model (pkl) → PyTorch → Heuristic
        self.ml_predictor = None
        self.ml_loaded = False
        self.pytorch_loaded = False
        self.pytorch_detector = None

        # 1. Try loading trained ML model (Random Forest / XGBoost / LightGBM)
        try:
            from model.predict_voice import VoicePredictor
            self.ml_predictor = VoicePredictor()
            if self.ml_predictor.model_loaded:
                self.ml_loaded = True
                print(f"[AIVoiceDetector] ✅ ML model loaded: {self.ml_predictor.model_name}")
        except Exception as e:
            print(f"[AIVoiceDetector] ML model not available: {e}")
            self.ml_predictor = None

        # 2. Try PyTorch engine as secondary classifier
        if self._check_safe("torch"):
            try:
                from model.deepfake_classifier import DeepfakeInference
                self.pytorch_detector = DeepfakeInference()
                if hasattr(self.pytorch_detector, 'model_loaded') and self.pytorch_detector.model_loaded:
                    self.pytorch_loaded = True
            except Exception as e:
                print(f"[AIVoiceDetector] PyTorch model initialization bypassed: {e}")
                self.pytorch_detector = None
        else:
            print("[AIVoiceDetector] PyTorch is unavailable or unstable on this system. Bypassing PyTorch detector.")

        # Log detection strategy
        if self.ml_loaded:
            print("[AIVoiceDetector] Strategy: ML Model (primary) → Heuristic (fallback)")
        elif self.pytorch_loaded:
            print("[AIVoiceDetector] Strategy: PyTorch (primary) → Heuristic (fallback)")
        else:
            print("[AIVoiceDetector] Strategy: Heuristic only (no trained models available)")

    def _check_safe(self, module_name: str) -> bool:
        import subprocess
        import sys
        try:
            res = subprocess.run(
                [sys.executable, "-c", f"import {module_name}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
            return res.returncode == 0
        except Exception:
            return False

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

        # === Classification Priority Chain ===

        # 1. Try ML Model (trained sklearn/xgboost)
        if self.ml_loaded and self.ml_predictor is not None:
            try:
                ml_result = self.ml_predictor.predict_bytes(file_bytes)
                ai_prob_raw = ml_result["ai_probability"]
                ai_score = round(ai_prob_raw * 100.0, 1)
                classification = ml_result["prediction"]

                if "AI" in classification:
                    classification = "Likely AI Generated"
                elif "Human" in classification:
                    classification = "Likely Human"
                else:
                    classification = "Uncertain"

                confidence = ml_result["confidence"]
                print(f"[AIVoiceDetector] ML prediction: {classification} "
                      f"(AI={ai_score}%, conf={confidence}%)")
            except Exception as e:
                print(f"[AIVoiceDetector Warn] ML model failed: {e}. Falling back...")
                ai_score, classification, confidence = self._fallback_classify(
                    file_bytes, pcm_bytes, signal, features
                )
        else:
            ai_score, classification, confidence = self._fallback_classify(
                file_bytes, pcm_bytes, signal, features
            )

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

        # Add model info to reasoning
        if self.ml_loaded:
            reasons.append(f"[Analysis by {self.ml_predictor.model_name} ML classifier]")
        elif self.pytorch_loaded:
            reasons.append("[Analysis by PyTorch neural network]")
        else:
            reasons.append("[Analysis by acoustic heuristic engine]")

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

    def _fallback_classify(self, file_bytes, pcm_bytes, signal, features):
        """Fallback classification chain: PyTorch → Heuristic"""
        if self.pytorch_loaded:
            try:
                raw_score = self.pytorch_detector.predict_pcm(pcm_bytes)
                ai_score = round(raw_score * 100.0, 1)

                if ai_score >= 61:
                    classification = "Likely AI Generated"
                    confidence = round(50.0 + (ai_score - 60) * 1.2, 1)
                elif ai_score >= 31:
                    classification = "Uncertain"
                    confidence = round(50.0 + (50 - abs(ai_score - 45)) * 0.4, 1)
                else:
                    classification = "Likely Human"
                    confidence = round(50.0 + (30 - ai_score) * 1.5, 1)

                return ai_score, classification, confidence
            except Exception as e:
                print(f"[AIVoiceDetector Warn] PyTorch run failed: {e}. Using heuristic.")

        return classify_voice_from_features(features)
