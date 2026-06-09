"""
train_ai_voice_model.py - Train the AI voice detection model
Trains a 3-class classifier:
- Class 0: Human voice
- Class 1: AI-Generated (ElevenLabs, Google TTS, etc.)
- Class 2: Deepfake/Synthetic (Vocoder-based)
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import os
from pathlib import Path
import argparse
from datetime import datetime

try:
    from .ai_voice_detector import AIVoiceClassifier
    from .ai_voice_dataset_builder import AIVoiceDatasetBuilder
except ImportError:
    from ai_voice_detector import AIVoiceClassifier
    from ai_voice_dataset_builder import AIVoiceDatasetBuilder


class AIVoiceTrainer:
    """Train AI voice detection model"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.config.setdefault("num_features", 13)
        self.config.setdefault("seq_len", 200)
        self.config.setdefault("batch_size", 32)
        self.config.setdefault("epochs", 30)
        self.config.setdefault("learning_rate", 0.001)
        self.config.setdefault("weight_decay", 1e-4)
        self.config.setdefault("device", "cuda" if torch.cuda.is_available() else "cpu")
        
        self.device = torch.device(self.config["device"])
        self.model = None
        self.best_acc = 0.0
        self.training_history = []

    def prepare_dataset(self, dataset_dir: str = None) -> tuple:
        """
        Prepare training dataset.
        Either loads from disk or generates synthetic data.
        """
        builder = AIVoiceDatasetBuilder({"num_features": self.config["num_features"],
                                         "seq_len": self.config["seq_len"]})
        
        if dataset_dir and os.path.isdir(dataset_dir):
            print(f"[Trainer] Loading dataset from {dataset_dir}...")
            builder.load_dataset(dataset_dir)
        else:
            print("[Trainer] Generating synthetic dataset...")
            # Generate balanced synthetic data
            samples_per_class = 200
            builder.generate_synthetic_samples(samples_per_class, "human")
            builder.generate_synthetic_samples(samples_per_class, "ai-generated")
            builder.generate_synthetic_samples(samples_per_class, "deepfake")
        
        # Print stats
        stats = builder.get_dataset_stats()
        print(f"[Trainer] Dataset prepared:")
        print(f"  Total samples: {stats['total_samples']}")
        print(f"  Distribution: {stats['distribution']}")
        
        # Split into train/val
        dataset = builder.get_torch_dataset()
        if dataset is None:
            raise RuntimeError("Failed to create PyTorch dataset")
        
        total_size = len(dataset)
        train_size = int(0.8 * total_size)
        val_size = total_size - train_size
        
        train_dataset, val_dataset = torch.utils.data.random_split(
            dataset, [train_size, val_size]
        )
        
        train_loader = DataLoader(
            train_dataset, 
            batch_size=self.config["batch_size"],
            shuffle=True,
            num_workers=0
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=self.config["batch_size"],
            shuffle=False,
            num_workers=0
        )
        
        return train_loader, val_loader

    def train(self, train_loader: DataLoader, val_loader: DataLoader, save_path: str = None):
        """
        Train the model.
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            save_path: Path to save best model
        """
        # Initialize model
        self.model = AIVoiceClassifier(
            num_features=self.config["num_features"],
            seq_len=self.config["seq_len"]
        )
        self.model.to(self.device)
        
        # Loss and optimizer
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(
            self.model.parameters(),
            lr=self.config["learning_rate"],
            weight_decay=self.config["weight_decay"]
        )
        
        # Learning rate scheduler
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode='max',
            factor=0.5,
            patience=5,
            verbose=True
        )
        
        if save_path is None:
            save_path = os.path.join(
                os.path.dirname(__file__),
                "ai_voice_model.pth"
            )
        
        print("\n" + "="*70)
        print("Training AI Voice Detection Model")
        print("="*70)
        print(f"Device: {self.device}")
        print(f"Model: 3-class classifier (Human, AI-Generated, Deepfake)")
        print(f"Epochs: {self.config['epochs']}")
        print(f"Batch size: {self.config['batch_size']}")
        print(f"Learning rate: {self.config['learning_rate']}")
        print("="*70 + "\n")
        
        print(f"{'Epoch':<8}{'Train Loss':<15}{'Val Loss':<15}{'Val Acc':<12}")
        print("-" * 70)
        
        best_acc = 0.0
        patience_counter = 0
        max_patience = 10
        
        for epoch in range(1, self.config["epochs"] + 1):
            # Training phase
            self.model.train()
            train_loss = 0.0
            
            for x, y in train_loader:
                x = x.to(self.device)
                y = y.to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(x)
                loss = criterion(outputs, y)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
            
            train_loss /= len(train_loader)
            
            # Validation phase
            self.model.eval()
            val_loss = 0.0
            correct = 0
            total = 0
            
            with torch.no_grad():
                for x, y in val_loader:
                    x = x.to(self.device)
                    y = y.to(self.device)
                    
                    outputs = self.model(x)
                    loss = criterion(outputs, y)
                    val_loss += loss.item()
                    
                    _, predicted = torch.max(outputs.data, 1)
                    correct += (predicted == y).sum().item()
                    total += y.size(0)
            
            val_loss /= len(val_loader)
            val_acc = correct / total
            
            print(f"{epoch:<8}{train_loss:<15.4f}{val_loss:<15.4f}{val_acc:<12.4f}")
            
            self.training_history.append({
                "epoch": epoch,
                "train_loss": train_loss,
                "val_loss": val_loss,
                "val_acc": val_acc
            })
            
            # Save best model
            if val_acc > best_acc:
                best_acc = val_acc
                patience_counter = 0
                
                checkpoint = {
                    "epoch": epoch,
                    "model_state": self.model.state_dict(),
                    "best_acc": best_acc,
                    "config": self.config,
                    "training_history": self.training_history
                }
                
                torch.save(checkpoint, save_path)
                print(f"  -> Best model saved (Acc: {best_acc:.4f})")
            else:
                patience_counter += 1
                if patience_counter >= max_patience:
                    print(f"\nEarly stopping at epoch {epoch}")
                    break
            
            # Learning rate scheduling
            scheduler.step(val_acc)
        
        print("\n" + "="*70)
        print(f"Training complete. Best validation accuracy: {best_acc:.4f}")
        print(f"Model saved to: {save_path}")
        print("="*70 + "\n")
        
        self.best_acc = best_acc
        return best_acc


def main():
    parser = argparse.ArgumentParser(
        description="Train AI Voice Detection Model"
    )
    parser.add_argument(
        "--dataset-dir",
        type=str,
        default=None,
        help="Path to dataset directory (optional, generates synthetic if not provided)"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=30,
        help="Number of training epochs"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size"
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=0.001,
        help="Learning rate"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda" if torch.cuda.is_available() else "cpu",
        help="Device to use (cuda or cpu)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output path for model (default: ai_voice_model.pth)"
    )
    
    args = parser.parse_args()
    
    # Create trainer
    config = {
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "device": args.device
    }
    
    trainer = AIVoiceTrainer(config)
    
    # Prepare dataset
    train_loader, val_loader = trainer.prepare_dataset(args.dataset_dir)
    
    # Train
    trainer.train(train_loader, val_loader, args.output)


if __name__ == "__main__":
    main()
