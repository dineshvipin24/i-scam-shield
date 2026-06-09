"""
prepare_voice_data.py - Utility to prepare voice data for AI voice detection model training
Helps organize and process audio files from multiple sources.

Usage:
    python prepare_voice_data.py --help
"""

import os
import sys
import argparse
from pathlib import Path
import json
import shutil
from typing import List, Dict
import numpy as np

try:
    from ai_voice_dataset_builder import AIVoiceDatasetBuilder
    from train_ai_voice_model import AIVoiceTrainer
except ImportError:
    from backend.model.ai_voice_dataset_builder import AIVoiceDatasetBuilder
    from backend.model.train_ai_voice_model import AIVoiceTrainer


class VoiceDataPreparation:
    """Utility for preparing voice training data"""
    
    AUDIO_EXTENSIONS = ['.wav', '.mp3', '.ogg', '.flac', '.m4a']
    
    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or Path(__file__).parent.parent.parent
        self.data_dir = os.path.join(self.workspace_root, "voice_data")
        self.dataset_dir = os.path.join(self.workspace_root, "voice_dataset")
        
        # Create directories
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.dataset_dir, exist_ok=True)
        
        self.subdirs = {
            "human": os.path.join(self.data_dir, "human_voices"),
            "ai": os.path.join(self.data_dir, "ai_generated"),
            "deepfake": os.path.join(self.data_dir, "deepfake_synthetic"),
            "elevenlabs": os.path.join(self.data_dir, "elevenlabs"),
            "google_tts": os.path.join(self.data_dir, "google_tts"),
            "amazon_polly": os.path.join(self.data_dir, "amazon_polly"),
            "other_tts": os.path.join(self.data_dir, "other_tts")
        }
        
        for subdir in self.subdirs.values():
            os.makedirs(subdir, exist_ok=True)

    def setup_directories(self):
        """Create organized directory structure for voice data"""
        print("\n" + "="*70)
        print("Voice Data Directory Structure")
        print("="*70)
        print(f"\nRoot: {self.data_dir}\n")
        
        for label, path in self.subdirs.items():
            print(f"  {label:20} -> {path}")
            print(f"    {' ' * 20}   (Place your audio files here)")
        
        print("\n" + "="*70)
        print("Instructions:")
        print("="*70)
        print("""
1. HUMAN VOICES (natural speech):
   - Place recorded human voice samples in: human_voices/
   - Can be conversations, speeches, recordings, etc.
   - Format: WAV, MP3, OGG, FLAC

2. AI-GENERATED VOICES (all TTS systems):
   - ElevenLabs: Place in elevenlabs/
   - Google TTS: Place in google_tts/
   - Amazon Polly: Place in amazon_polly/
   - Other TTS services: Place in other_tts/

3. DEEPFAKE/SYNTHETIC VOICES:
   - Place vocoder-based or deepfake samples in: deepfake_synthetic/

4. After organizing files, run:
   python prepare_voice_data.py --build-dataset

5. Then train the model:
   python prepare_voice_data.py --train-model
        """)
        print("="*70 + "\n")

    def organize_files(self, source_dir: str, label: str, source_type: str = None):
        """
        Move audio files from source directory to organized structure.
        
        Args:
            source_dir: Source directory with audio files
            label: "human", "ai", "deepfake", etc.
            source_type: Specific source ("elevenlabs", "google_tts", etc.)
        """
        if not os.path.isdir(source_dir):
            print(f"Error: Source directory not found: {source_dir}")
            return 0
        
        # Determine target directory
        if source_type and source_type in self.subdirs:
            target_dir = self.subdirs[source_type]
        else:
            target_dir = self.subdirs.get(label, self.subdirs["other_tts"])
        
        # Find audio files
        count = 0
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if any(file.lower().endswith(ext) for ext in self.AUDIO_EXTENSIONS):
                    src_path = os.path.join(root, file)
                    dst_path = os.path.join(target_dir, file)
                    
                    # Avoid overwriting
                    if os.path.exists(dst_path):
                        base, ext = os.path.splitext(file)
                        counter = 1
                        while os.path.exists(os.path.join(target_dir, f"{base}_{counter}{ext}")):
                            counter += 1
                        dst_path = os.path.join(target_dir, f"{base}_{counter}{ext}")
                    
                    shutil.copy2(src_path, dst_path)
                    count += 1
                    print(f"  Organized: {file}")
        
        print(f"\n[Organizer] Organized {count} files to {target_dir}\n")
        return count

    def build_dataset(self, output_dir: str = None) -> str:
        """
        Build training dataset from organized audio files.
        
        Args:
            output_dir: Output directory for dataset
            
        Returns:
            Path to saved dataset
        """
        if output_dir is None:
            output_dir = self.dataset_dir
        
        print("\n" + "="*70)
        print("Building Training Dataset")
        print("="*70 + "\n")
        
        builder = AIVoiceDatasetBuilder()
        
        # Add human voices
        human_dir = self.subdirs["human"]
        if os.path.isdir(human_dir):
            count = builder.add_directory(human_dir, "human", "human_recorded")
            print(f"[Builder] Added {count} human voice samples")
        
        # Add AI-generated voices
        ai_sources = {
            "elevenlabs": "ElevenLabs",
            "google_tts": "GoogleTTS",
            "amazon_polly": "AmazonPolly",
            "other_tts": "OtherTTS"
        }
        
        for dir_key, source_name in ai_sources.items():
            ai_dir = self.subdirs.get(dir_key)
            if ai_dir and os.path.isdir(ai_dir):
                count = builder.add_directory(ai_dir, "ai-generated", source_name)
                if count > 0:
                    print(f"[Builder] Added {count} {source_name} samples")
        
        # Add deepfake/synthetic
        deepfake_dir = self.subdirs["deepfake"]
        if os.path.isdir(deepfake_dir):
            count = builder.add_directory(deepfake_dir, "deepfake", "vocoder_deepfake")
            if count > 0:
                print(f"[Builder] Added {count} deepfake/synthetic samples")
        
        # If no real data, generate synthetic
        stats = builder.get_dataset_stats()
        if stats.get("total_samples", 0) == 0:
            print("\n[Builder] No audio files found. Generating synthetic dataset...")
            builder.generate_synthetic_samples(200, "human")
            builder.generate_synthetic_samples(200, "ai-generated")
            builder.generate_synthetic_samples(200, "deepfake")
        
        # Print statistics
        stats = builder.get_dataset_stats()
        print("\n" + "-"*70)
        print("Dataset Statistics:")
        print("-"*70)
        print(f"Total samples: {stats['total_samples']}")
        print(f"Distribution:")
        for label, count in stats['distribution'].items():
            percentage = (count / stats['total_samples'] * 100) if stats['total_samples'] > 0 else 0
            print(f"  {label:20} {count:6} ({percentage:6.1f}%)")
        print(f"\nTotal duration: {stats['total_duration_seconds']:.1f} seconds")
        print(f"Average duration: {stats['avg_duration_seconds']:.2f} seconds")
        print("-"*70 + "\n")
        
        # Save dataset
        builder.save_dataset(output_dir)
        
        return output_dir

    def train_model(self, dataset_dir: str = None, output_model: str = None):
        """
        Train the AI voice detection model.
        
        Args:
            dataset_dir: Path to dataset directory
            output_model: Path to save trained model
        """
        if dataset_dir is None:
            dataset_dir = self.dataset_dir
        
        # Configure trainer
        config = {
            "epochs": 30,
            "batch_size": 32,
            "learning_rate": 0.001,
            "device": "cuda" if torch.cuda.is_available() else "cpu"
        }
        
        trainer = AIVoiceTrainer(config)
        
        # Prepare dataset
        train_loader, val_loader = trainer.prepare_dataset(dataset_dir)
        
        # Train
        if output_model is None:
            output_model = os.path.join(
                os.path.dirname(__file__),
                "ai_voice_model.pth"
            )
        
        trainer.train(train_loader, val_loader, output_model)

    def create_example_structure(self):
        """Create example README files in data directories"""
        
        readme_content = {
            "human": """# Human Voice Samples

Place natural human voice recordings here.

Examples:
- Recorded conversations
- Speeches
- Podcasts
- News broadcasts
- Voice messages

Supported formats: WAV, MP3, OGG, FLAC
""",
            "elevenlabs": """# ElevenLabs Generated Voices

Place audio generated by ElevenLabs TTS here.

These are AI-generated voices that sound natural.
The model will learn to distinguish them from real human voices.

Supported formats: WAV, MP3, OGG, FLAC
""",
            "google_tts": """# Google TTS Generated Voices

Place audio generated by Google Text-to-Speech here.

Supported formats: WAV, MP3, OGG, FLAC
""",
            "amazon_polly": """# Amazon Polly Generated Voices

Place audio generated by Amazon Polly TTS here.

Supported formats: WAV, MP3, OGG, FLAC
""",
            "deepfake": """# Deepfake/Synthetic Voice Samples

Place deepfake or vocoder-based synthetic voice samples here.

These include:
- Voice cloning results
- Vocoder-based speech synthesis
- Deepfake voice conversion

Supported formats: WAV, MP3, OGG, FLAC
"""
        }
        
        for dir_key, content in readme_content.items():
            readme_path = os.path.join(self.subdirs.get(dir_key, ""), "README.md")
            os.makedirs(os.path.dirname(readme_path), exist_ok=True)
            with open(readme_path, "w") as f:
                f.write(content)


def main():
    parser = argparse.ArgumentParser(
        description="Prepare voice data for AI voice detection model training"
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Setup directory structure for voice data organization"
    )
    parser.add_argument(
        "--organize",
        type=str,
        help="Organize audio files from source directory"
    )
    parser.add_argument(
        "--label",
        type=str,
        choices=["human", "ai", "deepfake"],
        help="Label for organized files"
    )
    parser.add_argument(
        "--source-type",
        type=str,
        choices=["elevenlabs", "google_tts", "amazon_polly", "other_tts"],
        help="Specific source type for AI-generated voices"
    )
    parser.add_argument(
        "--build-dataset",
        action="store_true",
        help="Build training dataset from organized audio files"
    )
    parser.add_argument(
        "--train-model",
        action="store_true",
        help="Train the AI voice detection model"
    )
    parser.add_argument(
        "--dataset-dir",
        type=str,
        help="Path to dataset directory"
    )
    parser.add_argument(
        "--output-model",
        type=str,
        help="Path to save trained model"
    )
    parser.add_argument(
        "--workspace-root",
        type=str,
        help="Root workspace directory"
    )
    
    args = parser.parse_args()
    
    # Initialize preparation utility
    prep = VoiceDataPreparation(args.workspace_root)
    
    # Setup directories
    if args.setup:
        prep.setup_directories()
        prep.create_example_structure()
        return
    
    # Organize files
    if args.organize and args.label:
        print(f"\nOrganizing files from: {args.organize}")
        print(f"Label: {args.label}")
        if args.source_type:
            print(f"Source type: {args.source_type}")
        prep.organize_files(args.organize, args.label, args.source_type)
        return
    
    # Build dataset
    if args.build_dataset:
        dataset_dir = prep.build_dataset(args.dataset_dir)
        print(f"\nDataset ready at: {dataset_dir}")
        print("Next step: python prepare_voice_data.py --train-model")
        return
    
    # Train model
    if args.train_model:
        import torch
        prep.train_model(args.dataset_dir, args.output_model)
        return
    
    # Default: show help
    parser.print_help()


if __name__ == "__main__":
    main()
