"""
train_deepfake.py - Generates simulated speech features (Real vs Synthetic/Deepfake)
and trains the Conv1D PyTorch Classifier.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import os
from sklearn.model_selection import train_test_split
try:
    from .deepfake_classifier import DeepfakeAudioClassifier
except ImportError:
    from deepfake_classifier import DeepfakeAudioClassifier

# Configuration
CONFIG = {
    "num_features": 13,
    "seq_len": 200,
    "batch_size": 16,
    "epochs": 15,
    "learning_rate": 0.002,
    "model_path": os.path.join(os.path.dirname(os.path.abspath(__file__)), "deepfake_model.pth"),
}

# 1. Dataset Simulator
class SimulatedVoiceDataset(Dataset):
    def __init__(self, size=200):
        self.samples = []
        
        # Class 0: Real Voices (Dynamic voice rhythms, high vocal variance)
        for _ in range(size // 2):
            # Base features
            feat = np.random.normal(0, 0.8, (CONFIG["num_features"], CONFIG["seq_len"]))
            # Add dynamic speech contours (sine waves representing vocal intonations)
            t = np.linspace(0, 4 * np.pi, CONFIG["seq_len"])
            for f in range(CONFIG["num_features"]):
                feat[f] += np.sin(t * (1 + f * 0.2)) * 1.2
            self.samples.append((torch.tensor(feat, dtype=torch.float), torch.tensor(0.0, dtype=torch.float)))
            
        # Class 1: Synthetic/Deepfake Voices (Flatter speech contours, vocoder harmonic patterns)
        for _ in range(size // 2):
            # Base features (lower variance/robotic)
            feat = np.random.normal(0, 0.4, (CONFIG["num_features"], CONFIG["seq_len"]))
            # Add flat/static tone contours (representing robotic carrier frequencies)
            t = np.linspace(0, 8 * np.pi, CONFIG["seq_len"])
            for f in range(CONFIG["num_features"]):
                feat[f] += np.sin(t * 0.5) * 0.4 # very low frequency, flat variation
            self.samples.append((torch.tensor(feat, dtype=torch.float), torch.tensor(1.0, dtype=torch.float)))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


# 2. Main Training Pipeline
def train_model(size=1200):
    print(f"[Trainer] Initializing deepfake model training pipeline (samples={size})...")
    
    # Create dataset
    dataset = SimulatedVoiceDataset(size=size)
    
    # Split
    train_idx, val_idx = train_test_split(list(range(len(dataset))), test_size=0.2, random_state=42)
    train_ds = [dataset[i] for i in train_idx]
    val_ds = [dataset[i] for i in val_idx]
    
    train_loader = DataLoader(train_ds, batch_size=CONFIG["batch_size"], shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=CONFIG["batch_size"])
    
    # Model
    model = DeepfakeAudioClassifier(num_features=CONFIG["num_features"], seq_len=CONFIG["seq_len"])
    
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=CONFIG["learning_rate"], weight_decay=1e-4)
    
    print("\nTraining CNN classifier...")
    print(f"{'Epoch':<8}{'Train Loss':<15}{'Val Loss':<12}{'Val Acc'}")
    print("-" * 50)
    
    best_acc = 0.0
    
    for epoch in range(1, CONFIG["epochs"] + 1):
        # Train
        model.train()
        train_loss = 0.0
        for x, y in train_loader:
            optimizer.zero_grad()
            outputs = model(x)
            loss = criterion(outputs, y)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            
        train_loss /= len(train_loader)
        
        # Evaluate
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        with torch.no_grad():
            for x, y in val_loader:
                outputs = model(x)
                loss = criterion(outputs, y)
                val_loss += loss.item()
                preds = (outputs > 0.5).float()
                correct += (preds == y).sum().item()
                total += y.size(0)
                
        val_loss /= len(val_loader)
        val_acc = correct / total
        
        print(f"{epoch:<8}{train_loss:<15.4f}{val_loss:<12.4f}{val_acc:.2%}")
        
        # Save best
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save({
                "model_state": model.state_dict(),
                "best_acc": best_acc,
                "config": CONFIG
            }, CONFIG["model_path"])
            
    print(f"\n[Trainer] Training completed. Best validation accuracy: {best_acc:.2%}")
    print(f"[Trainer] Model saved successfully to: {CONFIG['model_path']}")

if __name__ == "__main__":
    train_model()
