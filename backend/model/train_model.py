"""
AI Scam Call Detector - PyTorch LSTM Model Training Script
Architecture: Embedding → BiLSTM → Attention → Dense → Sigmoid
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
import json
import os
import re
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, f1_score

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
CONFIG = {
    "max_vocab_size": 5000,
    "max_seq_len": 64,
    "embed_dim": 128,
    "hidden_dim": 128,
    "num_layers": 2,
    "dropout": 0.4,
    "batch_size": 32,
    "epochs": 30,
    "learning_rate": 0.001,
    "model_path": "scam_model.pth",
    "vocab_path": "vocab.json",
    "seed": 42,
}

torch.manual_seed(CONFIG["seed"])
np.random.seed(CONFIG["seed"])

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[INFO] Using device: {device}")


# ─────────────────────────────────────────────
# Text Preprocessing
# ─────────────────────────────────────────────
SCAM_KEYWORDS = [
    "otp", "account", "pin", "bank", "blocked", "urgent", "police", "arrest",
    "freeze", "kyc", "aadhaar", "pan", "transfer", "upi", "paytm", "phonePe",
    "prize", "lottery", "won", "claim", "fee", "processing", "refund",
    "verify", "verification", "immediately", "now", "last", "warning",
    "crime", "cbi", "rbi", "trai", "sbi", "court", "legal", "action",
    "turant", "abhi", "band", "share", "suspicious", "debit", "credit",
    "rupees", "lakh", "crore", "virus", "hack", "compromise", "warrant",
    "double", "guaranteed", "investment", "return", "percent", "fake"
]

def preprocess_text(text):
    """Lowercase, remove punctuation, normalize spaces."""
    text = str(text).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def boost_keywords(text):
    """
    Repeat scam-related keywords to help the model learn them faster.
    (A form of domain-specific data augmentation)
    """
    tokens = text.split()
    boosted = []
    for token in tokens:
        boosted.append(token)
        if token in SCAM_KEYWORDS:
            boosted.append(token)  # repeat keyword once
    return " ".join(boosted)


# ─────────────────────────────────────────────
# Vocabulary Builder
# ─────────────────────────────────────────────
class Vocabulary:
    def __init__(self, max_size=5000):
        self.max_size = max_size
        self.word2idx = {"<PAD>": 0, "<UNK>": 1}
        self.idx2word = {0: "<PAD>", 1: "<UNK>"}

    def build(self, texts):
        counter = Counter()
        for text in texts:
            counter.update(text.split())
        most_common = counter.most_common(self.max_size - 2)
        for idx, (word, _) in enumerate(most_common, start=2):
            self.word2idx[word] = idx
            self.idx2word[idx] = word
        print(f"[INFO] Vocabulary size: {len(self.word2idx)}")

    def encode(self, text, max_len):
        tokens = text.split()[:max_len]
        ids = [self.word2idx.get(t, 1) for t in tokens]
        # Pad to max_len
        ids += [0] * (max_len - len(ids))
        return ids

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.word2idx, f, ensure_ascii=False, indent=2)
        print(f"[INFO] Vocabulary saved to {path}")

    @classmethod
    def load(cls, path):
        vocab = cls()
        with open(path, "r", encoding="utf-8") as f:
            vocab.word2idx = json.load(f)
        vocab.idx2word = {v: k for k, v in vocab.word2idx.items()}
        return vocab


# ─────────────────────────────────────────────
# Dataset
# ─────────────────────────────────────────────
class ScamDataset(Dataset):
    def __init__(self, texts, labels, vocab, max_len):
        self.samples = []
        for text, label in zip(texts, labels):
            ids = vocab.encode(text, max_len)
            self.samples.append((torch.tensor(ids, dtype=torch.long),
                                  torch.tensor(float(label), dtype=torch.float)))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


# ─────────────────────────────────────────────
# Model: Attention BiLSTM
# ─────────────────────────────────────────────
class AttentionLayer(nn.Module):
    """Soft attention over LSTM hidden states."""
    def __init__(self, hidden_dim):
        super().__init__()
        self.attn = nn.Linear(hidden_dim * 2, 1)

    def forward(self, lstm_out):
        # lstm_out: (batch, seq_len, hidden*2)
        scores = self.attn(lstm_out).squeeze(-1)          # (batch, seq_len)
        weights = torch.softmax(scores, dim=1).unsqueeze(-1)  # (batch, seq_len, 1)
        context = (lstm_out * weights).sum(dim=1)          # (batch, hidden*2)
        return context, weights.squeeze(-1)


class ScamDetectorLSTM(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_layers, dropout):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embed_dim, hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0
        )
        self.attention = AttentionLayer(hidden_dim)
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(hidden_dim * 2, 64)
        self.fc2 = nn.Linear(64, 1)
        self.relu = nn.ReLU()

    def forward(self, x):
        # x: (batch, seq_len)
        embedded = self.dropout(self.embedding(x))         # (batch, seq, embed)
        lstm_out, _ = self.lstm(embedded)                   # (batch, seq, hidden*2)
        context, attn_weights = self.attention(lstm_out)    # (batch, hidden*2)
        out = self.dropout(self.relu(self.fc1(context)))
        out = torch.sigmoid(self.fc2(out)).squeeze(-1)      # (batch,)
        return out


# ─────────────────────────────────────────────
# Data Augmentation
# ─────────────────────────────────────────────
def augment_data(texts, labels):
    """Simple augmentation: shuffle words in some samples."""
    aug_texts, aug_labels = list(texts), list(labels)
    for text, label in zip(texts, labels):
        if label == 1:  # augment scam samples more
            words = text.split()
            if len(words) > 3:
                np.random.shuffle(words)
                aug_texts.append(" ".join(words))
                aug_labels.append(label)
    return aug_texts, aug_labels


# ─────────────────────────────────────────────
# Training Loop
# ─────────────────────────────────────────────
def train_epoch(model, loader, optimizer, criterion):
    model.train()
    total_loss, correct, total = 0, 0, 0
    for inputs, labels in loader:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        total_loss += loss.item()
        preds = (outputs > 0.5).float()
        correct += (preds == labels).sum().item()
        total += labels.size(0)
    return total_loss / len(loader), correct / total


def evaluate(model, loader, criterion):
    model.eval()
    total_loss, all_preds, all_labels = 0, [], []
    with torch.no_grad():
        for inputs, labels in loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            total_loss += loss.item()
            preds = (outputs > 0.5).float()
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    f1 = f1_score(all_labels, all_preds, zero_division=0)
    acc = sum(p == l for p, l in zip(all_preds, all_labels)) / len(all_labels)
    return total_loss / len(loader), acc, f1


# ─────────────────────────────────────────────
# Main Training Pipeline
# ─────────────────────────────────────────────
def main():
    # ── Load Dataset ──────────────────────────
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "scam_dataset.csv")
    df = pd.read_csv(csv_path)
    print(f"[INFO] Dataset loaded: {len(df)} samples")
    print(f"[INFO] Class distribution:\n{df['label'].value_counts()}")

    # ── Preprocess ────────────────────────────
    df["processed"] = df["text"].apply(preprocess_text).apply(boost_keywords)

    # ── Augment ───────────────────────────────
    texts_aug, labels_aug = augment_data(
        df["processed"].tolist(), df["label"].tolist()
    )
    print(f"[INFO] After augmentation: {len(texts_aug)} samples")

    # ── Split ─────────────────────────────────
    X_train, X_val, y_train, y_val = train_test_split(
        texts_aug, labels_aug,
        test_size=0.2, random_state=CONFIG["seed"], stratify=labels_aug
    )

    # ── Vocabulary ────────────────────────────
    vocab = Vocabulary(max_size=CONFIG["max_vocab_size"])
    vocab.build(X_train)
    vocab_path = os.path.join(script_dir, CONFIG["vocab_path"])
    vocab.save(vocab_path)

    # ── DataLoaders ───────────────────────────
    train_ds = ScamDataset(X_train, y_train, vocab, CONFIG["max_seq_len"])
    val_ds   = ScamDataset(X_val,   y_val,   vocab, CONFIG["max_seq_len"])
    train_loader = DataLoader(train_ds, batch_size=CONFIG["batch_size"], shuffle=True)
    val_loader   = DataLoader(val_ds,   batch_size=CONFIG["batch_size"])

    # ── Model ─────────────────────────────────
    model = ScamDetectorLSTM(
        vocab_size  = len(vocab.word2idx),
        embed_dim   = CONFIG["embed_dim"],
        hidden_dim  = CONFIG["hidden_dim"],
        num_layers  = CONFIG["num_layers"],
        dropout     = CONFIG["dropout"],
    ).to(device)

    # Compute class weights to handle imbalance
    n_scam = labels_aug.count(1)
    n_safe = labels_aug.count(0)
    pos_weight = torch.tensor([n_safe / n_scam], dtype=torch.float).to(device)
    criterion = nn.BCELoss(weight=None)  # BCELoss after sigmoid
    optimizer = optim.Adam(model.parameters(), lr=CONFIG["learning_rate"],
                           weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="max", factor=0.5, patience=3, verbose=True
    )

    # ── Training ──────────────────────────────
    best_f1 = 0.0
    model_path = os.path.join(script_dir, CONFIG["model_path"])

    print(f"\n{'='*60}")
    print(f"{'Epoch':<8}{'Train Loss':<14}{'Train Acc':<14}{'Val Loss':<12}{'Val Acc':<12}{'Val F1'}")
    print("="*60)

    for epoch in range(1, CONFIG["epochs"] + 1):
        train_loss, train_acc = train_epoch(model, train_loader, optimizer, criterion)
        val_loss, val_acc, val_f1 = evaluate(model, val_loader, criterion)
        scheduler.step(val_f1)

        print(f"{epoch:<8}{train_loss:<14.4f}{train_acc:<14.4f}{val_loss:<12.4f}{val_acc:<12.4f}{val_f1:.4f}")

        if val_f1 > best_f1:
            best_f1 = val_f1
            torch.save({
                "model_state": model.state_dict(),
                "config": CONFIG,
                "vocab_size": len(vocab.word2idx),
                "best_f1": best_f1,
            }, model_path)
            print(f"  ✅ Best model saved (F1={best_f1:.4f})")

    # ── Final Evaluation ──────────────────────
    print(f"\n[INFO] Best Validation F1: {best_f1:.4f}")
    print(f"[INFO] Model saved to: {model_path}")

    # Load best model for final report
    checkpoint = torch.load(model_path, map_location=device)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    all_preds, all_labels, all_scores = [], [], []
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs = inputs.to(device)
            scores = model(inputs).cpu().numpy()
            preds = (scores > 0.5).astype(int)
            all_scores.extend(scores)
            all_preds.extend(preds)
            all_labels.extend(labels.numpy())

    print("\n[CLASSIFICATION REPORT]")
    print(classification_report(all_labels, all_preds,
                                 target_names=["Safe", "Scam"]))
    print("[CONFUSION MATRIX]")
    print(confusion_matrix(all_labels, all_preds))


if __name__ == "__main__":
    main()
