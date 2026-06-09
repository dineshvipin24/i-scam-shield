"""
ai_voice_dataset_builder.py - Build training datasets for voice detection
Supports:
- Human voice data
- AI-Generated voice data (ElevenLabs, Google TTS, Amazon Polly, etc.)
- Deepfake/Synthetic voice data
"""

import numpy as np
import os
from pathlib import Path
from typing import List, Tuple, Dict
import json
from dataclasses import dataclass, asdict

try:
    from .feature_extractor import extract_mfcc, pcm_to_float32
except ImportError:
    from feature_extractor import extract_mfcc, pcm_to_float32


@dataclass
class VoiceSample:
    """Represents a single voice sample for training"""
    features: np.ndarray  # Shape: (13, 200) - MFCC features
    label: int  # 0=Human, 1=AI-Generated, 2=Deepfake
    source: str  # e.g., "ElevenLabs", "GoogleTTS", "human"
    duration: float  # Duration in seconds
    metadata: Dict = None  # Optional metadata


class AIVoiceDatasetBuilder:
    """
    Builds training datasets for AI voice detection.
    """
    
    LABEL_MAP = {
        "human": 0,
        "ai": 1,
        "ai-generated": 1,
        "elevenlabs": 1,
        "google_tts": 1,
        "amazon_polly": 1,
        "deepfake": 2,
        "synthetic": 2,
        "vocoder": 2
    }
    
    def __init__(self, config: Dict = None):
        """Initialize dataset builder with optional config"""
        self.config = config or {}
        self.config.setdefault("num_features", 13)
        self.config.setdefault("seq_len", 200)
        self.config.setdefault("sample_rate", 16000)
        
        self.samples: List[VoiceSample] = []
        self.metadata_log = []

    def add_audio_file(
        self, 
        file_path: str, 
        label: str,
        source: str = "unknown",
        metadata: Dict = None
    ) -> bool:
        """
        Add an audio file to the dataset.
        
        Args:
            file_path: Path to audio file (WAV, MP3, etc.)
            label: "human", "ai", "deepfake"
            source: Source identifier (e.g., "ElevenLabs", "human_recorded")
            metadata: Optional metadata dict
            
        Returns:
            True if successfully added, False otherwise
        """
        try:
            import soundfile as sf
        except ImportError:
            print("[Dataset Builder] soundfile required: pip install soundfile")
            return False
        
        try:
            # Load audio
            signal, sr = sf.read(file_path)
            
            # Resample if needed
            if sr != self.config["sample_rate"]:
                try:
                    from scipy import signal as scipy_signal
                    num_samples = int(len(signal) * self.config["sample_rate"] / sr)
                    signal = scipy_signal.resample(signal, num_samples)
                except ImportError:
                    print("[Dataset Builder] scipy required for resampling: pip install scipy")
                    return False
            
            # Handle stereo -> mono
            if len(signal.shape) > 1:
                signal = np.mean(signal, axis=1)
            
            # Normalize
            signal = signal / (np.max(np.abs(signal)) + 1e-8)
            
            # Extract MFCC
            mfcc = extract_mfcc(
                signal, 
                sr=self.config["sample_rate"],
                num_cep=self.config["num_features"]
            )
            
            # Format to shape (num_features, seq_len)
            if mfcc.shape[0] < self.config["seq_len"]:
                pad_width = self.config["seq_len"] - mfcc.shape[0]
                mfcc = np.pad(mfcc, ((0, pad_width), (0, 0)), mode="constant")
            else:
                mfcc = mfcc[:self.config["seq_len"]]
            
            # Get label
            label_key = label.lower().strip()
            numeric_label = self.LABEL_MAP.get(label_key, 0)
            
            # Duration
            duration = len(signal) / self.config["sample_rate"]
            
            # Create sample
            sample = VoiceSample(
                features=mfcc,
                label=numeric_label,
                source=source,
                duration=duration,
                metadata=metadata or {}
            )
            
            self.samples.append(sample)
            
            # Log
            self.metadata_log.append({
                "file": file_path,
                "label": label,
                "source": source,
                "duration": duration,
                "added": True
            })
            
            return True
            
        except Exception as e:
            print(f"[Dataset Builder] Error loading {file_path}: {e}")
            self.metadata_log.append({
                "file": file_path,
                "error": str(e),
                "added": False
            })
            return False

    def add_directory(
        self,
        directory: str,
        label: str,
        source: str = "unknown",
        recursive: bool = True,
        extensions: List[str] = None
    ) -> int:
        """
        Add all audio files from a directory.
        
        Args:
            directory: Directory path
            label: Label for all files in directory
            source: Source identifier
            recursive: Search subdirectories
            extensions: File extensions to search (default: .wav, .mp3, .ogg)
            
        Returns:
            Number of files added
        """
        if extensions is None:
            extensions = [".wav", ".mp3", ".ogg", ".flac"]
        
        if not os.path.isdir(directory):
            print(f"[Dataset Builder] Directory not found: {directory}")
            return 0
        
        path_obj = Path(directory)
        pattern = "**/*" if recursive else "*"
        
        files = []
        for ext in extensions:
            files.extend(path_obj.glob(f"{pattern}{ext}"))
            files.extend(path_obj.glob(f"{pattern}{ext.upper()}"))
        
        count = 0
        for file_path in files:
            if self.add_audio_file(str(file_path), label, source):
                count += 1
        
        print(f"[Dataset Builder] Added {count} files from {directory}")
        return count

    def generate_synthetic_samples(
        self,
        num_samples: int = 100,
        voice_type: str = "human"
    ) -> int:
        """
        Generate synthetic training samples for a voice type.
        Useful for data augmentation.
        
        Args:
            num_samples: Number of samples to generate
            voice_type: "human", "ai-generated", or "deepfake"
            
        Returns:
            Number of samples generated
        """
        label = self.LABEL_MAP.get(voice_type.lower(), 0)
        
        for i in range(num_samples):
            if voice_type.lower() in ["human"]:
                # Human voice characteristics
                features = self._generate_human_features()
                source = "synthetic_human"
            elif voice_type.lower() in ["ai", "ai-generated"]:
                # AI-generated voice characteristics
                features = self._generate_ai_features()
                source = "synthetic_ai"
            else:  # deepfake
                # Deepfake/vocoder characteristics
                features = self._generate_deepfake_features()
                source = "synthetic_deepfake"
            
            sample = VoiceSample(
                features=features,
                label=label,
                source=source,
                duration=np.random.uniform(2, 5),
                metadata={"synthetic": True}
            )
            self.samples.append(sample)
        
        return num_samples

    def _generate_human_features(self) -> np.ndarray:
        """Generate synthetic MFCC features for human voice"""
        seq_len = self.config["seq_len"]
        num_features = self.config["num_features"]
        
        # Base features with natural variation
        feat = np.random.normal(0, 0.8, (num_features, seq_len))
        
        # Add dynamic speech contours (variable pitch, natural intonation)
        t = np.linspace(0, 4 * np.pi, seq_len)
        for f in range(num_features):
            # Random frequency modulation
            freq = 1 + f * 0.2 + np.random.uniform(-0.3, 0.3)
            feat[f] += np.sin(t * freq) * np.random.uniform(0.8, 1.5)
            # Add some noise for natural irregularities
            feat[f] += np.random.normal(0, 0.2, seq_len)
        
        return feat.astype(np.float32)

    def _generate_ai_features(self) -> np.ndarray:
        """Generate synthetic MFCC features for AI-generated voice"""
        seq_len = self.config["seq_len"]
        num_features = self.config["num_features"]
        
        # AI voices have more stable, controlled characteristics
        feat = np.random.normal(0, 0.5, (num_features, seq_len))
        
        # Smoother, more regular patterns
        t = np.linspace(0, 6 * np.pi, seq_len)
        for f in range(num_features):
            # Very regular, predictable patterns
            feat[f] += np.sin(t * (0.8 + f * 0.15)) * 0.6
            # Add subtle harmonics (characteristic of TTS)
            feat[f] += np.sin(t * (1.6 + f * 0.3)) * 0.3
            # Less noise - more controlled
            feat[f] += np.random.normal(0, 0.05, seq_len)
        
        return feat.astype(np.float32)

    def _generate_deepfake_features(self) -> np.ndarray:
        """Generate synthetic MFCC features for deepfake/synthetic voice"""
        seq_len = self.config["seq_len"]
        num_features = self.config["num_features"]
        
        # Deepfake voices have vocoder artifacts
        feat = np.random.normal(0, 0.3, (num_features, seq_len))
        
        # Very flat, monotone characteristics
        t = np.linspace(0, 8 * np.pi, seq_len)
        for f in range(num_features):
            # Very low frequency, flat modulation (vocoder carrier)
            feat[f] += np.sin(t * 0.4) * 0.3
            # Harmonic series (vocoder pattern)
            feat[f] += np.sin(t * (0.8 + f * 0.25)) * 0.2
            # Minimal noise
            feat[f] += np.random.normal(0, 0.02, seq_len)
        
        return feat.astype(np.float32)

    def get_dataset_stats(self) -> Dict:
        """Get statistics about the dataset"""
        if not self.samples:
            return {}
        
        labels = [s.label for s in self.samples]
        sources = [s.source for s in self.samples]
        
        label_names = {0: "Human", 1: "AI-Generated", 2: "Deepfake"}
        
        stats = {
            "total_samples": len(self.samples),
            "distribution": {
                label_names[i]: sum(1 for l in labels if l == i)
                for i in [0, 1, 2]
            },
            "sources": dict(sorted(
                {s: sum(1 for src in sources if src == s) for s in set(sources)}.items()
            )),
            "total_duration_seconds": sum(s.duration for s in self.samples),
            "avg_duration_seconds": np.mean([s.duration for s in self.samples])
        }
        
        return stats

    def save_dataset(self, output_dir: str) -> bool:
        """
        Save dataset to disk (features + metadata).
        
        Args:
            output_dir: Output directory path
            
        Returns:
            True if successful
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Save features and labels
            features = np.array([s.features for s in self.samples])
            labels = np.array([s.label for s in self.samples])
            
            np.save(os.path.join(output_dir, "features.npy"), features)
            np.save(os.path.join(output_dir, "labels.npy"), labels)
            
            # Save metadata
            metadata = {
                "samples": [
                    {
                        "label": s.label,
                        "source": s.source,
                        "duration": s.duration,
                        "metadata": s.metadata
                    }
                    for s in self.samples
                ],
                "config": self.config,
                "stats": self.get_dataset_stats(),
                "log": self.metadata_log
            }
            
            with open(os.path.join(output_dir, "metadata.json"), "w") as f:
                json.dump(metadata, f, indent=2)
            
            print(f"[Dataset Builder] Dataset saved to {output_dir}")
            print(f"[Dataset Builder] Stats: {metadata['stats']}")
            
            return True
            
        except Exception as e:
            print(f"[Dataset Builder] Error saving dataset: {e}")
            return False

    def load_dataset(self, input_dir: str) -> bool:
        """
        Load dataset from disk.
        
        Args:
            input_dir: Directory containing saved dataset
            
        Returns:
            True if successful
        """
        try:
            features = np.load(os.path.join(input_dir, "features.npy"))
            labels = np.load(os.path.join(input_dir, "labels.npy"))
            
            with open(os.path.join(input_dir, "metadata.json"), "r") as f:
                metadata = json.load(f)
            
            self.samples = []
            for i, feat in enumerate(features):
                meta = metadata["samples"][i]
                sample = VoiceSample(
                    features=feat,
                    label=meta["label"],
                    source=meta["source"],
                    duration=meta["duration"],
                    metadata=meta.get("metadata", {})
                )
                self.samples.append(sample)
            
            self.config = metadata.get("config", self.config)
            
            print(f"[Dataset Builder] Loaded {len(self.samples)} samples from {input_dir}")
            print(f"[Dataset Builder] Stats: {self.get_dataset_stats()}")
            
            return True
            
        except Exception as e:
            print(f"[Dataset Builder] Error loading dataset: {e}")
            return False

    def get_torch_dataset(self):
        """
        Get PyTorch Dataset object for training.
        """
        try:
            import torch
            from torch.utils.data import Dataset
            
            class TorchVoiceDataset(Dataset):
                def __init__(self, samples: List[VoiceSample]):
                    self.samples = samples
                
                def __len__(self):
                    return len(self.samples)
                
                def __getitem__(self, idx):
                    sample = self.samples[idx]
                    features = torch.tensor(sample.features, dtype=torch.float32)
                    label = torch.tensor(sample.label, dtype=torch.long)
                    return features, label
            
            return TorchVoiceDataset(self.samples)
            
        except ImportError:
            print("[Dataset Builder] PyTorch required: pip install torch")
            return None
