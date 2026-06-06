# phase1-prototype/fraud_detector.py
import os
import csv

class FraudDetector:
    def __init__(self):
        self.sklearn_available = False
        self.vectorizer = None
        self.classifier = None
        self.categories_model = None
        self.dataset_file = "phase1-prototype/dataset.csv"
        
        # Threat dictionary for keyword/phrase scanning
        self.keywords = ["otp", "cvv", "pin", "aadhaar", "pan", "anydesk", "teamviewer", "blocked", "lottery", "arrest", "kyc"]
        self.patterns = [
            "share your otp", "verify your account", "install anydesk", 
            "confirm your bank", "scan the qr", "enter your pin"
        ]

        try:
            import sklearn
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
            self.sklearn_available = True
        except ImportError:
            print("[Dependency Notice] scikit-learn is not installed. Using fallback rule-based classifier.")

        # Train models if dataset exists
        self.train_models()

    def train_models(self):
        if not self.sklearn_available:
            return
            
        if not os.path.exists(self.dataset_file):
            print(f"Dataset file {self.dataset_file} not found. Run dataset_builder.py first.")
            return

        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        import numpy as np

        texts = []
        labels = []
        categories = []

        with open(self.dataset_file, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # Skip header
            for row in reader:
                if len(row) >= 3:
                    texts.append(row[0])
                    categories.append(row[1])
                    labels.append(int(row[2]))

        if not texts:
            return

        # Vectorization
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        X = self.vectorizer.fit_transform(texts)
        
        # Scam vs Safe Classifier
        self.classifier = LogisticRegression()
        self.classifier.fit(X, labels)

        # Category Classifier
        self.categories_model = LogisticRegression()
        self.categories_model.fit(X, categories)
        
        print("Models trained successfully on local dataset.")

    def evaluate_text(self, text: str) -> dict:
        """Evaluates text transcript for scam risk assessment."""
        lowered = text.toLowerCase() if hasattr(text, 'toLowerCase') else text.lower()
        matched_keywords = [k for k in self.keywords if k in lowered]
        matched_patterns = [p for p in self.patterns if p in lowered]

        # 1. Classification & Probability
        if self.sklearn_available and self.classifier is not None:
            X_vec = self.vectorizer.transform([text])
            prob = float(self.classifier.predict_proba(X_vec)[0][1])
            predicted_cat = str(self.categories_model.predict(X_vec)[0])
            confidence = prob if prob > 0.5 else (1.0 - prob)
        else:
            # Rule-based fallback classification
            base_risk = 0.0
            if len(matched_keywords) > 0:
                base_risk += 0.35
            if len(matched_patterns) > 0:
                base_risk += 0.45
            
            prob = min(base_risk + (len(matched_keywords) * 0.1), 1.0)
            predicted_cat = "Safe Call"
            if prob >= 0.7:
                predicted_cat = "OTP Scam" if "otp" in lowered else "Banking Scam"
            elif prob >= 0.35:
                predicted_cat = "Suspicious Call"
            confidence = prob

        # 2. Score conversion
        risk_score = int(prob * 100)
        
        if risk_score >= 61:
            risk_level = "HIGH"
        elif risk_score >= 31:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
            predicted_cat = "Safe Call"

        # 3. Create Evidence Summary Report
        evidence = f"Call transcript evaluated. Threat level: {risk_level}. "
        if risk_level != "LOW":
            evidence += f"Identified {len(matched_keywords)} keyword warnings: {matched_keywords}. "
            if matched_patterns:
                evidence += f"Matched scam phrase indicators: {matched_patterns}. "
            evidence += f"Scam signature category matches '{predicted_cat}' profile."
        else:
            evidence += "No prominent threat indicators detected."

        return {
            "fraud_probability": round(prob, 2),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "detected_keywords": matched_keywords,
            "detected_patterns": matched_patterns,
            "fraud_category": predicted_cat,
            "confidence_score": round(confidence, 2),
            "evidence_report": evidence
        }

if __name__ == "__main__":
    # Test execution
    detector = FraudDetector()
    sample = "Please verify your account now by reading the 6-digit OTP code sent to your mobile number."
    print("Evaluation Result:", detector.evaluate_text(sample))
