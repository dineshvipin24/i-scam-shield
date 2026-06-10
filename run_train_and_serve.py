"""
run_train_and_serve.py - One-shot script to train the model and start the server.
Run from the project root: python run_train_and_serve.py
"""
import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(ROOT, "backend")
MODEL_DIR = os.path.join(BACKEND, "model")

def main():
    # Step 1: Try to install optional dependencies (non-fatal if fails)
    print("=" * 60)
    print("  CAMP PROTECT - AI VOICE DETECTION SETUP")
    print("=" * 60)
    
    print("\n[1/3] Installing ML dependencies...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "xgboost", "lightgbm", "joblib", "--quiet"],
            timeout=120, check=False
        )
    except Exception as e:
        print(f"  [WARN] Optional packages install issue: {e}")
    
    # Step 2: Train the model
    print("\n[2/3] Training AI Voice Detection model...")
    sys.path.insert(0, MODEL_DIR)
    os.chdir(MODEL_DIR)
    
    try:
        from train_voice_model import main as train_main
        train_main()
    except Exception as e:
        print(f"  [ERROR] Training failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Start the server
    print("\n[3/3] Starting backend server...")
    os.chdir(BACKEND)
    print("  Server starting at http://localhost:8000")
    print("  Press Ctrl+C to stop.")
    
    subprocess.run([
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", "0.0.0.0", "--port", "8000", "--reload"
    ])

if __name__ == "__main__":
    main()
