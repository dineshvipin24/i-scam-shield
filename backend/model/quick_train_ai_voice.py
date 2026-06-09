"""
quick_train_ai_voice.py - Quick training script for AI voice detection

This script provides an easy way to:
1. Add voice files (including the ElevenLabs file you mentioned)
2. Generate training data
3. Train the model
4. Evaluate results

Usage:
    python quick_train_ai_voice.py
    python quick_train_ai_voice.py --elevenlabs-file path/to/elevenlabs.mp3
    python quick_train_ai_voice.py --human-voices-dir /path/to/human/voices --train
"""

import os
import sys
import argparse
from pathlib import Path
import numpy as np
import torch

try:
    from ai_voice_detector import AIVoiceDetector
    from ai_voice_dataset_builder import AIVoiceDatasetBuilder
    from train_ai_voice_model import AIVoiceTrainer
except ImportError:
    from backend.model.ai_voice_detector import AIVoiceDetector
    from backend.model.ai_voice_dataset_builder import AIVoiceDatasetBuilder
    from backend.model.train_ai_voice_model import AIVoiceTrainer


def setup_data_structure():
    """Create standard data structure for voice samples"""
    base_dir = "voice_data_training"
    dirs = {
        "human": os.path.join(base_dir, "human_voices"),
        "elevenlabs": os.path.join(base_dir, "elevenlabs_samples"),
        "synthetic": os.path.join(base_dir, "deepfake_synthetic"),
    }
    
    for dir_path in dirs.values():
        os.makedirs(dir_path, exist_ok=True)
    
    return dirs, base_dir


def add_elevenlabs_file(file_path: str, data_dirs: dict, builder: AIVoiceDatasetBuilder) -> bool:
    """Add ElevenLabs audio file to training"""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"\n📥 Adding ElevenLabs file: {os.path.basename(file_path)}")
    
    success = builder.add_audio_file(
        file_path,
        label="ai-generated",
        source="ElevenLabs",
        metadata={"elevenlabs_sample": True, "original_file": file_path}
    )
    
    if success:
        print(f"✅ Successfully added: {os.path.basename(file_path)}")
    else:
        print(f"❌ Failed to add: {os.path.basename(file_path)}")
    
    return success


def generate_training_data(builder: AIVoiceDatasetBuilder, 
                          human_samples: int = 150,
                          ai_samples: int = 150, 
                          deepfake_samples: int = 150):
    """Generate synthetic training data"""
    print("\n🔄 Generating training data...")
    
    print(f"  • Generating {human_samples} human voice samples...")
    builder.generate_synthetic_samples(human_samples, "human")
    
    print(f"  • Generating {ai_samples} AI-generated samples...")
    builder.generate_synthetic_samples(ai_samples, "ai-generated")
    
    print(f"  • Generating {deepfake_samples} deepfake samples...")
    builder.generate_synthetic_samples(deepfake_samples, "deepfake")
    
    stats = builder.get_dataset_stats()
    
    print("\n📊 Dataset Statistics:")
    print("  " + "="*50)
    print(f"  Total samples: {stats['total_samples']}")
    print(f"  Distribution:")
    for label, count in stats['distribution'].items():
        pct = (count / stats['total_samples'] * 100) if stats['total_samples'] > 0 else 0
        print(f"    • {label:20} {count:6} ({pct:6.1f}%)")
    print(f"  Total duration: {stats['total_duration_seconds']:.1f} seconds")
    print("  " + "="*50)


def train_model(builder: AIVoiceDatasetBuilder, 
               dataset_dir: str = "ai_voice_training_data",
               model_path: str = None) -> float:
    """Train the model"""
    print("\n🚀 Starting model training...")
    
    # Save dataset
    print(f"💾 Saving dataset to {dataset_dir}...")
    builder.save_dataset(dataset_dir)
    
    # Create trainer
    config = {
        "epochs": 30,
        "batch_size": 32,
        "learning_rate": 0.001,
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }
    
    print(f"🔧 Training configuration:")
    print(f"  • Device: {config['device']}")
    print(f"  • Epochs: {config['epochs']}")
    print(f"  • Batch size: {config['batch_size']}")
    print(f"  • Learning rate: {config['learning_rate']}")
    
    trainer = AIVoiceTrainer(config)
    
    # Prepare dataset
    train_loader, val_loader = trainer.prepare_dataset(dataset_dir)
    
    # Train
    if model_path is None:
        model_path = os.path.join(os.path.dirname(__file__), "ai_voice_model.pth")
    
    best_acc = trainer.train(train_loader, val_loader, model_path)
    
    print(f"\n✅ Training complete!")
    print(f"  • Model saved to: {model_path}")
    print(f"  • Best validation accuracy: {best_acc:.2%}")
    
    return best_acc


def test_model(model_path: str, test_file: str = None) -> bool:
    """Test the trained model"""
    print("\n🧪 Testing model...")
    
    detector = AIVoiceDetector(model_path)
    
    if not detector.model_loaded:
        print("❌ Model failed to load")
        return False
    
    if test_file and os.path.exists(test_file):
        print(f"📁 Testing on: {os.path.basename(test_file)}")
        
        try:
            prediction, probs = detector.predict_file(test_file)
            print(f"\n📊 Prediction Results:")
            print(f"  • Predicted: {prediction}")
            print(f"  • Confidence:")
            for label, prob in probs.items():
                confidence_bar = "█" * int(prob * 20)
                print(f"    - {label:20} {prob:6.1%}  {confidence_bar}")
            
            return True
        except Exception as e:
            print(f"❌ Error testing file: {e}")
            return False
    else:
        print("ℹ️  No test file provided. Use --test-file to evaluate on audio.")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Quick training for AI voice detection model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full training pipeline
  python quick_train_ai_voice.py --train
  
  # Add ElevenLabs file and train
  python quick_train_ai_voice.py --elevenlabs-file "path/to/elevenlabs.mp3" --train
  
  # Test existing model
  python quick_train_ai_voice.py --test-file "path/to/audio.mp3"
  
  # Custom training
  python quick_train_ai_voice.py \\
    --elevenlabs-file voice.mp3 \\
    --human-samples 200 \\
    --ai-samples 200 \\
    --train
        """
    )
    
    parser.add_argument(
        "--elevenlabs-file",
        type=str,
        help="Path to ElevenLabs audio file to include in training"
    )
    parser.add_argument(
        "--human-voices-dir",
        type=str,
        help="Directory containing human voice samples"
    )
    parser.add_argument(
        "--human-samples",
        type=int,
        default=150,
        help="Number of synthetic human voice samples to generate"
    )
    parser.add_argument(
        "--ai-samples",
        type=int,
        default=150,
        help="Number of synthetic AI-generated samples to generate"
    )
    parser.add_argument(
        "--deepfake-samples",
        type=int,
        default=150,
        help="Number of synthetic deepfake samples to generate"
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Train the model after preparing data"
    )
    parser.add_argument(
        "--test-file",
        type=str,
        help="Audio file to test the model on"
    )
    parser.add_argument(
        "--model-path",
        type=str,
        help="Path to save/load model"
    )
    parser.add_argument(
        "--dataset-dir",
        type=str,
        default="ai_voice_training_data",
        help="Directory to save dataset"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🎯 AI Voice Detection - Quick Training")
    print("="*70)
    
    # Setup
    data_dirs, base_dir = setup_data_structure()
    print(f"\n📁 Data structure created in: {base_dir}")
    
    # Initialize builder
    builder = AIVoiceDatasetBuilder()
    
    # Add ElevenLabs file if provided
    if args.elevenlabs_file:
        add_elevenlabs_file(args.elevenlabs_file, data_dirs, builder)
    
    # Add human voices if directory provided
    if args.human_voices_dir:
        print(f"\n📥 Adding human voice samples from: {args.human_voices_dir}")
        count = builder.add_directory(args.human_voices_dir, "human", "user_provided")
        print(f"✅ Added {count} human voice samples")
    
    # Generate synthetic data
    generate_training_data(
        builder,
        args.human_samples,
        args.ai_samples,
        args.deepfake_samples
    )
    
    # Train if requested
    if args.train:
        model_path = args.model_path
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), "ai_voice_model.pth")
        
        train_model(builder, args.dataset_dir, model_path)
        
        # Test if requested
        if args.test_file:
            test_model(model_path, args.test_file)
    
    # Test only mode
    elif args.test_file:
        model_path = args.model_path
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), "ai_voice_model.pth")
        
        test_model(model_path, args.test_file)
    
    else:
        print("\n" + "-"*70)
        print("📌 Next Steps:")
        print("-"*70)
        print("1. Add more voice data:")
        print(f"   • Human voices: {data_dirs['human']}")
        print(f"   • ElevenLabs: {data_dirs['elevenlabs']}")
        print(f"   • Deepfake: {data_dirs['synthetic']}")
        print("\n2. Train the model:")
        print("   python quick_train_ai_voice.py --train")
        print("\n3. Test on audio:")
        print("   python quick_train_ai_voice.py --test-file audio.mp3")
        print("-"*70 + "\n")
    
    print("\n" + "="*70)
    print("✅ Done!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
