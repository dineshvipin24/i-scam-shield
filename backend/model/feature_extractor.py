"""
feature_extractor.py - Pure numpy and scipy implementation of MFCC extraction.
Avoids heavy librosa installation requirements.
"""

import numpy as np
from scipy.fftpack import dct

def extract_mfcc(signal, sr=16000, num_cep=13, nfft=512, win_len=0.025, win_step=0.01, num_filters=26):
    """
    Extracts Mel-Frequency Cepstral Coefficients (MFCC) from a raw 1D float32 audio signal.
    """
    if len(signal) == 0:
        return np.zeros((0, num_cep), dtype=np.float32)
        
    # 1. Pre-emphasis filtering to balance high/low frequencies
    signal = np.append(signal[0], signal[1:] - 0.97 * signal[:-1])
    
    # 2. Framing
    frame_len = int(round(win_len * sr))
    frame_step = int(round(win_step * sr))
    signal_len = len(signal)
    
    if signal_len <= frame_len:
        num_frames = 1
    else:
        num_frames = 1 + int(np.ceil((signal_len - frame_len) / frame_step))
        
    pad_len = int((num_frames - 1) * frame_step + frame_len)
    zeros = np.zeros(pad_len - signal_len)
    pad_signal = np.append(signal, zeros)
    
    indices = np.tile(np.arange(0, frame_len), (num_frames, 1)) + \
              np.tile(np.arange(0, num_frames * frame_step, frame_step), (frame_len, 1)).T
    frames = pad_signal[indices.astype(np.int32, copy=False)]
    
    # 3. Hamming Window
    frames = frames * np.hamming(frame_len)
    
    # 4. FFT and Power Spectrum
    mag_frames = np.absolute(np.fft.rfft(frames, nfft))
    pow_frames = ((1.0 / nfft) * (mag_frames ** 2))
    
    # 5. Mel Filterbank Design
    low_freq_mel = 0
    high_freq_mel = 2595 * np.log10(1 + (sr / 2) / 700)
    mel_points = np.linspace(low_freq_mel, high_freq_mel, num_filters + 2)
    hz_points = 700 * (10**(mel_points / 2595) - 1)
    bins = np.floor((nfft + 1) * hz_points / sr).astype(np.int32)
    
    fbank = np.zeros((num_filters, int(nfft / 2 + 1)))
    for m in range(1, num_filters + 1):
        f_m_minus = bins[m - 1]
        f_m = bins[m]
        f_m_plus = bins[m + 1]
        for k in range(f_m_minus, f_m):
            fbank[m - 1, k] = (k - bins[m - 1]) / (bins[m] - bins[m - 1])
        for k in range(f_m, f_m_plus):
            fbank[m - 1, k] = (bins[m + 1] - k) / (bins[m + 1] - bins[m])
            
    # Multiply power spectrum with mel filterbanks
    filter_banks = np.dot(pow_frames, fbank.T)
    filter_banks = np.where(filter_banks == 0, np.finfo(float).eps, filter_banks)
    filter_banks = 20 * np.log10(filter_banks) # Convert to dB scale
    
    # 6. Discrete Cosine Transform (DCT)
    mfcc = dct(filter_banks, type=2, axis=1, norm='ortho')[:, :num_cep]
    return mfcc.astype(np.float32)


def pcm_to_float32(pcm_bytes: bytes) -> np.ndarray:
    """Converts mono 16-bit linear PCM bytes to a float32 numpy array normalized to [-1, 1]."""
    if not pcm_bytes:
        return np.zeros(0, dtype=np.float32)
    return np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
