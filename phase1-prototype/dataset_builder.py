# phase1-prototype/dataset_builder.py
import csv
import os

DATASET_FILE = "phase1-prototype/dataset.csv"

# Diverse text samples across all 10 required fraud categories
scam_samples = [
    # OTP Scam
    ("Hello, I am calling from your bank. We noticed an unauthorized charge. I have sent an OTP code to your number to cancel it. Please share the OTP code with me immediately.", "OTP Scam"),
    ("Sir, your card is blocked. To unblock it, I am sending a 6-digit verification code. Please read the code to me so we can activate your account.", "OTP Scam"),
    ("Please share the OTP you just received so we can process your pending transaction.", "OTP Scam"),
    
    # Banking Scam
    ("This is the credit department. Your bank account has been compromised. We need your account number and card CVV to transfer your money to a secure government locker.", "Banking Scam"),
    ("Your credit card limit is being updated. Tell me your card number, expiry date, and the 3-digit CVV number on the back.", "Banking Scam"),
    ("I am calling from state bank support. Confirm your bank account password and username to prevent temporary suspension.", "Banking Scam"),

    # UPI Scam
    ("Congratulations! You won a cash reward of 10,000 rupees. I am sending a payment link. Please scan the QR code and enter your UPI PIN to claim the money.", "UPI Scam"),
    ("To receive the money for the furniture you listed, click this request link and enter your UPI security pin to accept the payment.", "UPI Scam"),
    ("Please authorize the UPI request in your app to receive the cashback rewards immediately.", "UPI Scam"),

    # KYC Scam
    ("Hello, your SIM card KYC update is pending. If you do not update your KYC details now, your mobile number will be blocked within 2 hours. Send your Aadhaar and PAN details.", "KYC Scam"),
    ("Your bank KYC verification has expired. Please verify your identity by sending a photo of your Aadhaar card and PAN card to this number.", "KYC Scam"),
    ("Click this link to complete your identity verification and update your KYC online to prevent account freeze.", "KYC Scam"),

    # Lottery Scam
    ("Dear customer, you have won a lottery prize of 25 Lakhs from Kaun Banega Crorepati. To claim the prize money, you must pay a processing fee of 15,000 rupees.", "Lottery Scam"),
    ("Congratulations, your phone number has won the international lottery draw. Please deposit the tax amount into this account to release your prize cash.", "Lottery Scam"),

    # Government Scam
    ("This is officer Sharma calling from the police department. Your name has appeared in an illegal money laundering case. You must pay a penalty fine now or face arrest.", "Government Scam"),
    ("I am calling from the Tax department. We found discrepancies in your tax filings. Pay the unpaid tax immediately to avoid legal action.", "Government Scam"),

    # Remote Access Scam
    ("Hello, this is tech support. Your computer has been infected with malware. Please download the AnyDesk application or TeamViewer so I can clean your PC remotely.", "Remote Access Scam"),
    ("To fix the banking error, install the screen sharing app called TeamViewer QuickSupport so we can assist you step-by-step.", "Remote Access Scam"),

    # Investment Scam
    ("Invest in our high-yield crypto trading platform. We guarantee a 200% return on your investment in just 7 days with zero risk.", "Investment Scam"),
    ("Join our stock market trading group. We provide insider tips that will double your money in a week. Deposit funds to start trading.", "Investment Scam"),

    # Job Scam
    ("Congratulations, you have been selected for a work-from-home job at Amazon. The salary is 50,000 per month. Pay a registration fee of 2,000 to get the welcome kit.", "Job Scam"),
    ("We are offering part-time jobs liking videos online. To start, pay the security deposit fee which will be refunded after your first task.", "Job Scam"),

    # Loan Scam
    ("Your pre-approved loan of 5 Lakhs is ready for disbursal with a low 2% interest rate. Pay a documentation charge of 5,000 rupees to activate the loan.", "Loan Scam"),
    ("Easy loan approval with no document checks or credit score requirements. Pay processing charges now to receive the loan amount in your account.", "Loan Scam")
]

safe_samples = [
    ("Hi, just calling to ask if we are meeting for dinner tonight at the usual restaurant. Let me know.", "Safe Call"),
    ("Hello, is this Rajesh? I am calling from the courier service, I am standing near your apartment gate. Please collect your package.", "Safe Call"),
    ("Mom, I will be late coming home from college today because we have a group presentation. Don't wait for dinner.", "Safe Call"),
    ("Hi, this is Amit from customer service. You raised a query regarding your internet bill. I am happy to help resolve this.", "Safe Call"),
    ("Hello, I am calling to confirm your dental appointment scheduled for tomorrow at 4 PM. Please let us know if you need to reschedule.", "Safe Call"),
    ("Hey, did you watch the cricket match yesterday? That final over was absolutely incredible!", "Safe Call"),
    ("Hi, your food delivery driver is here at the lobby door. Can you please unlock the main gate?", "Safe Call"),
    ("Good morning, I am calling from HR. We received your resume for the software engineer position and would like to schedule an interview.", "Safe Call"),
    ("Hello, can you please send me the class notes for the chemistry lecture? I missed the class yesterday.", "Safe Call"),
    ("Hey, do you want to play badminton this weekend at the local sports club?", "Safe Call")
]

def build_dataset():
    os.makedirs("phase1-prototype", exist_ok=True)
    with open(DATASET_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["text", "category", "is_scam"])
        
        for text, cat in scam_samples:
            writer.writerow([text, cat, 1])
            
        for text, cat in safe_samples:
            writer.writerow([text, cat, 0])
            
    print(f"Dataset compiled successfully containing {len(scam_samples) + len(safe_samples)} samples in {DATASET_FILE}")

if __name__ == "__main__":
    build_dataset()
