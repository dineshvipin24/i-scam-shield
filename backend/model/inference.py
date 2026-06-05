"""
Inference module: loads trained scam_model.pth and scores new text.
Used by the FastAPI backend in real-time during call processing.
"""

import torch
import torch.nn as nn
import json
import re
import os
from typing import Tuple

# ─────────────────────────────────────────────
# Mirror of model architecture (must match train_model.py)
# ─────────────────────────────────────────────

class AttentionLayer(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.attn = nn.Linear(hidden_dim * 2, 1)

    def forward(self, lstm_out):
        scores = self.attn(lstm_out).squeeze(-1)
        weights = torch.softmax(scores, dim=1).unsqueeze(-1)
        context = (lstm_out * weights).sum(dim=1)
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
        embedded = self.dropout(self.embedding(x))
        lstm_out, _ = self.lstm(embedded)
        context, attn_weights = self.attention(lstm_out)
        out = self.dropout(self.relu(self.fc1(context)))
        out = torch.sigmoid(self.fc2(out)).squeeze(-1)
        return out


# ─────────────────────────────────────────────
# Inference Engine
# ─────────────────────────────────────────────

RISK_THRESHOLDS = {
    "safe":        (0.0,  0.40),
    "suspicious":  (0.41, 0.70),
    "fraud":       (0.71, 1.00),
}

def get_risk_label(score: float) -> str:
    if score <= 0.40:
        return "safe"
    elif score <= 0.70:
        return "suspicious"
    else:
        return "fraud"


class ScamInferenceEngine:
    """
    Singleton inference engine. Load once, reuse across all WebSocket connections.
    Usage:
        engine = ScamInferenceEngine()
        score, label = engine.predict("Your OTP is being verified please wait")
    """

    _instance = None

    def __new__(cls, model_dir: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_dir: str = None):
        if self._initialized:
            return
        if model_dir is None:
            model_dir = os.path.dirname(os.path.abspath(__file__))

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.max_seq_len = 64

        # Load vocabulary
        vocab_path = os.path.join(model_dir, "vocab.json")
        with open(vocab_path, "r", encoding="utf-8") as f:
            self.word2idx = json.load(f)

        # Load checkpoint
        model_path = os.path.join(model_dir, "scam_model.pth")
        checkpoint = torch.load(model_path, map_location=self.device)
        config = checkpoint.get("config", {})

        self.model = ScamDetectorLSTM(
            vocab_size  = checkpoint.get("vocab_size", len(self.word2idx)),
            embed_dim   = config.get("embed_dim", 128),
            hidden_dim  = config.get("hidden_dim", 128),
            num_layers  = config.get("num_layers", 2),
            dropout     = config.get("dropout", 0.4),
        ).to(self.device)

        self.model.load_state_dict(checkpoint["model_state"])
        self.model.eval()
        self._initialized = True
        print(f"[ScamEngine] Model loaded from {model_path} on {self.device}")
        print(f"[ScamEngine] Best training F1: {checkpoint.get('best_f1', 'N/A')}")

    def _preprocess(self, text: str) -> torch.Tensor:
        text = str(text).lower()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        tokens = text.split()[:self.max_seq_len]
        ids = [self.word2idx.get(t, 1) for t in tokens]
        ids += [0] * (self.max_seq_len - len(ids))
        return torch.tensor([ids], dtype=torch.long).to(self.device)

    @torch.no_grad()
    def predict(self, text: str) -> Tuple[float, str]:
        """
        Returns:
            score (float): 0.0 → 1.0 scam probability
            label (str):   'safe' | 'suspicious' | 'fraud'
        """
        if not text or not text.strip():
            return 0.0, "safe"
        tensor = self._preprocess(text)
        score = float(self.model(tensor).item())
        label = get_risk_label(score)
        return round(score, 4), label

    def predict_rolling(self, transcript_window: str) -> Tuple[float, str]:
        """
        Score a rolling window of transcript text.
        The backend should concatenate the last ~30 seconds of transcript.
        """
        return self.predict(transcript_window)


# ─────────────────────────────────────────────
# CLI Testing
# ─────────────────────────────────────────────
if __name__ == "__main__":
    engine = ScamInferenceEngine()

    test_cases = [
        ("Aapka OTP share karo abhi account band ho jayega", 1),
        ("Hey how are you doing today", 0),
        ("Your UPI PIN is required to verify the transaction immediately", 1),
        ("Kal movie dekhne chaloge", 0),
        ("Sir aap arrested honge agar abhi payment nahi ki CBI case darj hoga", 1),
        ("Good morning what time is the meeting", 0),
        ("Aapko 50 lakh prize mila hai processing fee bharo", 1),
        ("Please send the document on email", 0),
    ]

    print(f"\n{'Text':<60} {'Score':<8} {'Label':<12} {'Correct?'}")
    print("-" * 95)
    correct = 0
    for text, true_label in test_cases:
        score, label = engine.predict(text)
        predicted = 1 if label in ("suspicious", "fraud") else 0
        ok = "✅" if predicted == true_label else "❌"
        if predicted == true_label:
            correct += 1
        print(f"{text[:58]:<60} {score:<8.4f} {label:<12} {ok}")

    print(f"\nAccuracy on test cases: {correct}/{len(test_cases)}")
