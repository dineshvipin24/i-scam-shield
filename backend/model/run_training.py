"""
run_training.py — standalone script that trains the model AND prints all output clearly.
Run this from the backend/model directory:
    python run_training.py
"""

import subprocess
import sys
import os

print("=" * 60)
print("  AI SCAM SHIELD — Model Training")
print("=" * 60)

# Make sure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Run training
result = subprocess.run(
    [sys.executable, "train_model.py"],
    capture_output=False,
    text=True
)

if result.returncode == 0:
    print("\n✅ Training completed successfully!")
    if os.path.exists("scam_model.pth"):
        size = os.path.getsize("scam_model.pth")
        print(f"   scam_model.pth created ({size/1024:.1f} KB)")
    if os.path.exists("vocab.json"):
        print(f"   vocab.json created")
else:
    print(f"\n❌ Training failed with exit code {result.returncode}")
