"""
feature_extraction.py - Enhanced Audio Feature Extraction for AI Voice Detection
Extracts: MFCC, Spectral Centroid, Spectral Bandwidth, Zero Crossing Rate,
           RMS Energy, Chroma Features, Pitch Features, Spectral Contrast,
           Spectral Roll-off, Voice Stability, Prosody, Speaking Rate, Pause Analysis.

Designed to work on 8GB RAM laptops without heavy dependencies.
Uses numpy + scipy only (no librosa required).
"""

import numpy as np
import io
import wave
import os

try:
    from scipy.fftpack import dct
    from scipy.signal import lfilter
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# Try importing av for advanced container formats decoding
try:
    import av
    AV_AVAILABLE = True
except ImportError:
    AV_AVAILABLE = False


# ─────────────────────────────────────────────
# Audio Decoding
# ─────────────────────────────────────────────

def decode_audio_to_pcm(file_bytes: bytes, target_sr: int = 16000) -> tuple:
    """
    Decode audio of any format to mono float32 signal at target_sr.
    Returns: (signal_float32, sample_rate)
    """
    if not file_bytes:
        return np.zeros(0, dtype=np.float32), target_sr

    pcm_bytes = _decode_raw_pcm(file_bytes, target_sr)
    if not pcm_bytes:
        return np.zeros(0, dtype=np.float32), target_sr

    signal = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    return signal, target_sr


def _decode_raw_pcm(file_bytes: bytes, target_sr: int = 16000) -> bytes:
    """Decode audio bytes to 16-bit mono PCM at target_sr. Supports MP3, M4A, WAV, etc."""
    # Strategy 1: PyAV
    if AV_AVAILABLE:
        try:
            input_file = io.BytesIO(file_bytes)
            container = av.open(input_file)
            audio_stream = next((s for s in container.streams if s.type == 'audio'), None)
            if audio_stream:
                resampler = av.AudioResampler(format='s16', layout='mono', rate=target_sr)
                pcm_data = bytearray()
                for frame in container.decode(audio_stream):
                    resampled_frames = resampler.resample(frame)
                    for rf in resampled_frames:
                        pcm_data.extend(rf.planes[0].to_ndarray().tobytes())
                if len(pcm_data) > 0:
                    return bytes(pcm_data)
        except Exception as e:
            print(f"[Feature Extraction] PyAV failed: {e}. Trying next...")

    # Strategy 2: soundfile
    try:
        import soundfile as sf
        data, samplerate = sf.read(io.BytesIO(file_bytes), dtype='int16')
        if len(data.shape) > 1:
            data = data.mean(axis=1).astype(np.int16)
        if samplerate != target_sr:
            duration = len(data) / samplerate
            new_len = int(duration * target_sr)
            data = np.interp(
                np.linspace(0, len(data) - 1, new_len),
                np.arange(len(data)), data
            ).astype(np.int16)
        if len(data) > 0:
            return data.tobytes()
    except Exception as e:
        print(f"[Feature Extraction] soundfile failed: {e}. Trying next...")

    # Strategy 3: ffmpeg subprocess
    try:
        import subprocess
        import sys
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.audio') as tmp_in:
            tmp_in.write(file_bytes)
            tmp_in_path = tmp_in.name
        tmp_out_path = tmp_in_path + '.raw'
        try:
            result = subprocess.run(
                ['ffmpeg', '-y', '-i', tmp_in_path,
                 '-ar', str(target_sr), '-ac', '1', '-f', 's16le', '-acodec', 'pcm_s16le',
                 tmp_out_path],
                capture_output=True, timeout=30
            )
            if result.returncode == 0 and os.path.exists(tmp_out_path):
                with open(tmp_out_path, 'rb') as f:
                    pcm_data = f.read()
                if len(pcm_data) > 0:
                    return pcm_data
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"[Feature Extraction] ffmpeg error: {e}")
        finally:
            for p in [tmp_in_path, tmp_out_path]:
                try:
                    if os.path.exists(p): os.remove(p)
                except: pass
    except Exception:
        pass

    # Strategy 4: pydub
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(io.BytesIO(file_bytes))
        audio = audio.set_frame_rate(target_sr).set_channels(1).set_sample_width(2)
        if len(audio.raw_data) > 0:
            return audio.raw_data
    except Exception as e:
        print(f"[Feature Extraction] pydub failed: {e}")

    # Strategy 5: Standard wave library (WAV only)
    try:
        with wave.open(io.BytesIO(file_bytes), 'rb') as wav:
            params = wav.getparams()
            raw = wav.readframes(params.nframes)
            signal = np.frombuffer(raw, dtype=np.int16)

            if params.nchannels > 1:
                signal = signal.reshape(-1, params.nchannels).mean(axis=1).astype(np.int16)

            if params.framerate != target_sr:
                duration = len(signal) / params.framerate
                new_len = int(duration * target_sr)
                signal = np.interp(
                    np.linspace(0, len(signal) - 1, new_len),
                    np.arange(len(signal)), signal
                ).astype(np.int16)

            return signal.tobytes()
    except Exception as ex:
        print(f"[Feature Extraction] Wave decode failed: {ex}")
        return b""


# ─────────────────────────────────────────────
# Core Feature Extraction Functions
# ─────────────────────────────────────────────

def extract_mfcc(signal: np.ndarray, sr: int = 16000, num_cep: int = 13,
                 nfft: int = 512, win_len: float = 0.025, win_step: float = 0.01,
                 num_filters: int = 26) -> np.ndarray:
    """
    Extract MFCC features from audio signal.
    Returns: (num_frames, num_cep) array
    """
    if not SCIPY_AVAILABLE:
        return np.zeros((1, num_cep), dtype=np.float32)

    if len(signal) == 0:
        return np.zeros((1, num_cep), dtype=np.float32)

    # Pre-emphasis
    signal = np.append(signal[0], signal[1:] - 0.97 * signal[:-1])

    # Framing
    frame_len = int(round(win_len * sr))
    frame_step_samples = int(round(win_step * sr))
    signal_len = len(signal)

    if signal_len <= frame_len:
        num_frames = 1
    else:
        num_frames = 1 + int(np.ceil((signal_len - frame_len) / frame_step_samples))

    pad_len = int((num_frames - 1) * frame_step_samples + frame_len)
    pad_signal = np.append(signal, np.zeros(pad_len - signal_len))

    indices = (np.tile(np.arange(0, frame_len), (num_frames, 1)) +
               np.tile(np.arange(0, num_frames * frame_step_samples, frame_step_samples),
                       (frame_len, 1)).T)
    frames = pad_signal[indices.astype(np.int32)]

    # Hamming window
    frames = frames * np.hamming(frame_len)

    # FFT and power spectrum
    mag_frames = np.absolute(np.fft.rfft(frames, nfft))
    pow_frames = (1.0 / nfft) * (mag_frames ** 2)

    # Mel filterbank
    low_freq_mel = 0
    high_freq_mel = 2595 * np.log10(1 + (sr / 2) / 700)
    mel_points = np.linspace(low_freq_mel, high_freq_mel, num_filters + 2)
    hz_points = 700 * (10 ** (mel_points / 2595) - 1)
    bins = np.floor((nfft + 1) * hz_points / sr).astype(np.int32)

    fbank = np.zeros((num_filters, int(nfft / 2 + 1)))
    for m in range(1, num_filters + 1):
        f_m_minus = bins[m - 1]
        f_m = bins[m]
        f_m_plus = bins[m + 1]
        for k in range(f_m_minus, f_m):
            if bins[m] != bins[m - 1]:
                fbank[m - 1, k] = (k - bins[m - 1]) / (bins[m] - bins[m - 1])
        for k in range(f_m, f_m_plus):
            if bins[m + 1] != bins[m]:
                fbank[m - 1, k] = (bins[m + 1] - k) / (bins[m + 1] - bins[m])

    filter_banks = np.dot(pow_frames, fbank.T)
    filter_banks = np.where(filter_banks == 0, np.finfo(float).eps, filter_banks)
    filter_banks = 20 * np.log10(filter_banks)

    # DCT
    mfcc = dct(filter_banks, type=2, axis=1, norm='ortho')[:, :num_cep]
    return mfcc.astype(np.float32)


def extract_spectral_centroid(signal: np.ndarray, sr: int = 16000,
                               nfft: int = 512, hop: int = 160) -> np.ndarray:
    """Compute spectral centroid for each frame."""
    if len(signal) < nfft:
        return np.array([0.0])

    num_frames = 1 + (len(signal) - nfft) // hop
    centroids = np.zeros(num_frames)
    freqs = np.fft.rfftfreq(nfft, d=1.0 / sr)

    for i in range(num_frames):
        frame = signal[i * hop: i * hop + nfft]
        frame = frame * np.hamming(nfft)
        magnitude = np.abs(np.fft.rfft(frame))
        total_mag = np.sum(magnitude)
        if total_mag > 0:
            centroids[i] = np.sum(freqs * magnitude) / total_mag
        else:
            centroids[i] = 0.0

    return centroids


def extract_spectral_bandwidth(signal: np.ndarray, sr: int = 16000,
                                nfft: int = 512, hop: int = 160) -> np.ndarray:
    """Compute spectral bandwidth for each frame."""
    if len(signal) < nfft:
        return np.array([0.0])

    centroids = extract_spectral_centroid(signal, sr, nfft, hop)
    num_frames = len(centroids)
    bandwidths = np.zeros(num_frames)
    freqs = np.fft.rfftfreq(nfft, d=1.0 / sr)

    for i in range(num_frames):
        frame = signal[i * hop: i * hop + nfft]
        frame = frame * np.hamming(nfft)
        magnitude = np.abs(np.fft.rfft(frame))
        total_mag = np.sum(magnitude)
        if total_mag > 0:
            deviation = freqs - centroids[i]
            bandwidths[i] = np.sqrt(np.sum(magnitude * (deviation ** 2)) / total_mag)

    return bandwidths


def extract_zero_crossing_rate(signal: np.ndarray, frame_len: int = 400,
                                hop: int = 160) -> np.ndarray:
    """Compute zero crossing rate per frame."""
    if len(signal) < frame_len:
        if len(signal) > 1:
            zcr_val = np.mean(np.abs(np.diff(np.sign(signal)))) / 2
            return np.array([zcr_val])
        return np.array([0.0])

    num_frames = 1 + (len(signal) - frame_len) // hop
    zcr = np.zeros(num_frames)

    for i in range(num_frames):
        frame = signal[i * hop: i * hop + frame_len]
        zcr[i] = np.mean(np.abs(np.diff(np.sign(frame)))) / 2

    return zcr


def extract_rms_energy(signal: np.ndarray, frame_len: int = 400,
                        hop: int = 160) -> np.ndarray:
    """Compute RMS energy per frame."""
    if len(signal) < frame_len:
        return np.array([np.sqrt(np.mean(signal ** 2))])

    num_frames = 1 + (len(signal) - frame_len) // hop
    rms = np.zeros(num_frames)

    for i in range(num_frames):
        frame = signal[i * hop: i * hop + frame_len]
        rms[i] = np.sqrt(np.mean(frame ** 2))

    return rms


def extract_chroma_features(signal: np.ndarray, sr: int = 16000,
                             nfft: int = 512, hop: int = 160,
                             n_chroma: int = 12) -> np.ndarray:
    """Compute chroma features (12-bin pitch class energy distribution)."""
    if len(signal) < nfft:
        return np.zeros((1, n_chroma), dtype=np.float32)

    num_frames = 1 + (len(signal) - nfft) // hop
    chroma = np.zeros((num_frames, n_chroma), dtype=np.float32)

    freqs = np.fft.rfftfreq(nfft, d=1.0 / sr)
    nonzero_freqs = freqs.copy()
    nonzero_freqs[0] = 1e-6
    chroma_map = np.round(12 * np.log2(nonzero_freqs / 440.0)) % 12
    chroma_map = chroma_map.astype(int)

    for i in range(num_frames):
        frame = signal[i * hop: i * hop + nfft]
        frame = frame * np.hamming(nfft)
        magnitude = np.abs(np.fft.rfft(frame)) ** 2

        for c in range(n_chroma):
            mask = chroma_map == c
            chroma[i, c] = np.sum(magnitude[mask])

        total = np.sum(chroma[i])
        if total > 0:
            chroma[i] /= total

    return chroma


def extract_pitch_features(signal: np.ndarray, sr: int = 16000) -> dict:
    """Extract pitch-related features: F0, pitch variance, jitter, shimmer."""
    frame_len = int(0.025 * sr)
    frame_step = int(0.010 * sr)

    if len(signal) < frame_len:
        return {
            "pitch_mean": 0.0,
            "pitch_variance": 0.0,
            "pitch_range": 0.0,
            "jitter": 0.0,
            "shimmer": 0.0,
        }

    num_frames = 1 + (len(signal) - frame_len) // frame_step
    min_lag = int(sr / 350)
    max_lag = int(sr / 60)

    pitches = []
    periods = []
    amplitudes = []

    for i in range(num_frames):
        start = i * frame_step
        frame = signal[start:start + frame_len]

        corr = np.correlate(frame, frame, mode='full')
        corr = corr[len(corr) // 2:]

        if len(corr) > max_lag:
            lag_region = corr[min_lag:max_lag]
            if len(lag_region) > 0 and np.max(lag_region) > 0.05 * corr[0]:
                peak_lag = np.argmax(lag_region) + min_lag
                f0 = sr / peak_lag
                pitches.append(f0)
                periods.append(peak_lag)
                amplitudes.append(float(np.max(frame) - np.min(frame)))

    valid_pitches = np.array(pitches) if pitches else np.array([0.0])

    if len(periods) > 1:
        diff_periods = np.abs(np.diff(periods))
        mean_period = np.mean(periods)
        jitter = float(np.mean(diff_periods) / mean_period) if mean_period > 0 else 0.0
    else:
        jitter = 0.0

    if len(amplitudes) > 1:
        diff_amps = np.abs(np.diff(amplitudes))
        mean_amp = np.mean(amplitudes)
        shimmer = float(np.mean(diff_amps) / mean_amp) if mean_amp > 0 else 0.0
    else:
        shimmer = 0.0

    return {
        "pitch_mean": float(np.mean(valid_pitches)) if len(valid_pitches) > 0 else 0.0,
        "pitch_variance": float(np.var(valid_pitches)) if len(valid_pitches) > 1 else 0.0,
        "pitch_range": float(np.ptp(valid_pitches)) if len(valid_pitches) > 1 else 0.0,
        "jitter": jitter,
        "shimmer": shimmer,
    }


def extract_spectral_contrast(signal: np.ndarray, sr: int = 16000,
                              nfft: int = 512, hop: int = 160,
                              n_bands: int = 6) -> np.ndarray:
    """Compute spectral contrast (difference between peaks and valleys in bands)."""
    if len(signal) < nfft:
        return np.zeros((1, n_bands), dtype=np.float32)

    num_frames = 1 + (len(signal) - nfft) // hop
    freqs = np.fft.rfftfreq(nfft, d=1.0 / sr)
    band_limits = np.logspace(np.log10(100), np.log10(sr / 2), n_bands + 1)
    
    contrast = np.zeros((num_frames, n_bands))
    for i in range(num_frames):
        frame = signal[i * hop: i * hop + nfft]
        frame = frame * np.hamming(nfft)
        magnitude = np.abs(np.fft.rfft(frame))
        
        for b in range(n_bands):
            mask = (freqs >= band_limits[b]) & (freqs < band_limits[b+1])
            if np.sum(mask) > 0:
                vals = magnitude[mask]
                peak = np.percentile(vals, 95)
                valley = np.percentile(vals, 5)
                contrast[i, b] = np.log10(peak + 1e-8) - np.log10(valley + 1e-8)
            else:
                contrast[i, b] = 0.0
    return contrast


def extract_spectral_rolloff(signal: np.ndarray, sr: int = 16000,
                              nfft: int = 512, hop: int = 160,
                              roll_percent: float = 0.85) -> np.ndarray:
    """Compute spectral roll-off frequency below which 85% of power lies."""
    if len(signal) < nfft:
        return np.array([0.0])

    num_frames = 1 + (len(signal) - nfft) // hop
    rolloffs = np.zeros(num_frames)
    freqs = np.fft.rfftfreq(nfft, d=1.0 / sr)

    for i in range(num_frames):
        frame = signal[i * hop: i * hop + nfft]
        frame = frame * np.hamming(nfft)
        magnitude = np.abs(np.fft.rfft(frame))
        total_energy = np.sum(magnitude)
        if total_energy > 0:
            cum_energy = np.cumsum(magnitude)
            threshold = roll_percent * total_energy
            idx = np.where(cum_energy >= threshold)[0]
            if len(idx) > 0:
                rolloffs[i] = freqs[idx[0]]
            else:
                rolloffs[i] = 0.0
        else:
            rolloffs[i] = 0.0
    return rolloffs


# ─────────────────────────────────────────────
# Combined Feature Vector Extraction
# ─────────────────────────────────────────────

def extract_all_features(signal: np.ndarray, sr: int = 16000) -> np.ndarray:
    """
    Extract a complete feature vector from an audio signal.
    Returns a 1D numpy array of fixed length (69 features) suitable for ML model input.
    """
    if len(signal) == 0:
        return np.zeros(69, dtype=np.float32)

    features = []

    # 1. MFCC (13 coefficients): mean + std = 26 features
    mfcc = extract_mfcc(signal, sr)
    features.extend(np.mean(mfcc, axis=0))
    features.extend(np.std(mfcc, axis=0))

    # 2. Spectral Centroid: mean + std = 2 features
    centroid = extract_spectral_centroid(signal, sr)
    features.append(float(np.mean(centroid)))
    features.append(float(np.std(centroid)))

    # 3. Spectral Bandwidth: mean + std = 2 features
    bandwidth = extract_spectral_bandwidth(signal, sr)
    features.append(float(np.mean(bandwidth)))
    features.append(float(np.std(bandwidth)))

    # 4. Zero Crossing Rate: mean + std = 2 features
    zcr = extract_zero_crossing_rate(signal)
    features.append(float(np.mean(zcr)))
    features.append(float(np.std(zcr)))

    # 5. RMS Energy: mean + std = 2 features
    rms = extract_rms_energy(signal)
    features.append(float(np.mean(rms)))
    features.append(float(np.std(rms)))

    # 6. Chroma: mean of 12 bins = 12 features
    chroma = extract_chroma_features(signal, sr)
    features.extend(np.mean(chroma, axis=0))

    # 7. Pitch: 5 features
    pitch = extract_pitch_features(signal, sr)
    features.append(pitch["pitch_mean"])
    features.append(pitch["pitch_variance"])
    features.append(pitch["pitch_range"])
    features.append(pitch["jitter"])
    features.append(pitch["shimmer"])

    # 8. Spectral Contrast (6 bands): mean + std = 12 features
    contrast = extract_spectral_contrast(signal, sr)
    features.extend(np.mean(contrast, axis=0))
    features.extend(np.std(contrast, axis=0))

    # 9. Spectral Roll-off: mean + std = 2 features
    rolloff = extract_spectral_rolloff(signal, sr)
    features.append(float(np.mean(rolloff)))
    features.append(float(np.std(rolloff)))

    # 10. Voice Stability = 1 feature
    stability = 1.0 / (1.0 + pitch["jitter"] * 6.0 + pitch["shimmer"] * 3.0 + (pitch["pitch_variance"] / 2000.0))
    voice_stability = float(np.clip(stability, 0.0, 1.0))
    features.append(voice_stability)

    # 11. Prosody score = 1 feature
    prosody_score = float(pitch["pitch_variance"] / (pitch["pitch_mean"] ** 2 + 1e-5))
    features.append(prosody_score)

    # 12 & 13. Speaking Rate & Pause Analysis = 2 features
    frame_len = 400
    hop = 160
    num_frames = max(1, 1 + (len(signal) - frame_len) // hop)
    energies = np.zeros(num_frames)
    if len(signal) >= frame_len:
        for i in range(num_frames):
            frame = signal[i * hop: i * hop + frame_len]
            energies[i] = np.sum(frame ** 2)
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
    
    features.append(speaking_rate)
    features.append(pause_frequency)

    # Total feature count = 26 + 2 + 2 + 2 + 2 + 12 + 5 + 12 + 2 + 1 + 1 + 1 + 1 = 69 features
    return np.nan_to_num(np.array(features, dtype=np.float32), nan=0.0, posinf=0.0, neginf=0.0)


def extract_features_from_file(file_path: str) -> np.ndarray:
    """Extract features from an audio file on disk."""
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    signal, sr = decode_audio_to_pcm(file_bytes)
    return extract_all_features(signal, sr)


def extract_features_from_bytes(file_bytes: bytes) -> np.ndarray:
    """Extract features from audio file bytes."""
    signal, sr = decode_audio_to_pcm(file_bytes)
    return extract_all_features(signal, sr)


if __name__ == "__main__":
    sr = 16000
    duration = 2.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    test_signal = 0.5 * np.sin(2 * np.pi * 440 * t).astype(np.float32)
    feats = extract_all_features(test_signal, sr)
    print(f"Test feature vector shape: {feats.shape} (Expected: (69,))")
