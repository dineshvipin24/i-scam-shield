# phase1-prototype/audio_processor.py
import os

class AudioProcessor:
    def __init__(self):
        self.whisper_available = False
        self.librosa_available = False
        
        try:
            import whisper
            self.model = whisper.load_model("tiny")
            self.whisper_available = True
        except ImportError:
            print("[Dependency Notice] Whisper is not installed on this local Python environment. Using fallback mock transcription.")
            
        try:
            import librosa
            self.librosa_available = True
        except ImportError:
            print("[Dependency Notice] Librosa is not installed. Using fallback acoustic metrics.")

    def transcribe(self, file_path: str) -> str:
        """Transcribes audio file to string text."""
        if not os.path.exists(file_path):
            return "Mock: Please share the OTP code sent to your phone to verify your security access."
            
        if self.whisper_available:
            import whisper
            try:
                result = self.model.transcribe(file_path)
                return result.get("text", "")
            except Exception as e:
                return f"Error during whisper transcription: {e}"
        else:
            return "Fallback: Urgent bank notice, your card is blocked. Tell me the OTP immediately to fix."

    def extract_acoustic_fingerprint(self, file_path: str) -> dict:
        """Extracts low-level audio properties (MFCCs, spectral centroid)."""
        if not self.librosa_available or not os.path.exists(file_path):
            # Fallback metrics
            return {
                "mfcc_mean_1": -250.0,
                "mfcc_mean_2": 120.0,
                "spectral_centroid": 1500.0,
                "zero_crossing_rate": 0.08,
                "status": "Using mock acoustic properties"
            }
            
        import librosa
        import numpy as np
        
        try:
            y, sr = librosa.load(file_path, duration=15)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            zcr = librosa.feature.zero_crossing_rate(y=y)
            
            return {
                "mfcc_mean_1": float(np.mean(mfccs[0])),
                "mfcc_mean_2": float(np.mean(mfccs[1])),
                "spectral_centroid": float(np.mean(centroid)),
                "zero_crossing_rate": float(np.mean(zcr)),
                "status": "Extraction successful"
            }
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    processor = AudioProcessor()
    print("Acoustic Fingerprint:", processor.extract_acoustic_fingerprint("non_existent_file.wav"))
    print("Transcript Result:", processor.transcribe("non_existent_file.wav"))
