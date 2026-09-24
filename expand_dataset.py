"""
Expands scam_dataset.csv using template-based generation so the ML
model has enough training data to generalize properly (not just
memorize 82 examples). Produces a larger, still-balanced dataset.
"""
import csv
import random

random.seed(42)

banks = ["SBI", "HDFC", "ICICI", "Axis Bank", "PNB", "Canara Bank", "Bank of Baroda", "Kotak Bank"]
amounts = ["5,000", "12,500", "25,000", "45,000", "88,000", "1,50,000", "2,25,000", "5,00,000", "10,00,000", "99,999"]
names = ["Ramesh", "Priya", "Suresh", "Lakshmi", "Karthik", "Divya", "Arjun", "Meena", "Vijay", "Anitha"]
companies = ["Amazon", "Flipkart", "Swiggy", "Zomato", "Myntra", "Google", "Netflix", "Paytm", "PhonePe", "Ola"]
apps = ["GPay", "PhonePe", "Paytm", "Amazon Pay", "BHIM UPI"]
times = ["10 minutes", "30 minutes", "1 hour", "2 hours", "24 hours", "today", "immediately"]

SCAM_TEMPLATES = [
    ("Congratulations! You have won Rs {amount} in {company} lucky draw. Click here to claim now", "lottery"),
    ("Dear {name}, your number has been selected for a cash prize of Rs {amount}. Call now to claim", "lottery"),
    ("You've won a free {company} gift card worth Rs {amount}! Click the link before it expires", "lottery"),
    ("Your {bank} account will be blocked in {time}. Update your KYC immediately by clicking this link", "phishing"),
    ("URGENT: Your {bank} debit card has been suspended. Verify your details now to reactivate", "phishing"),
    ("Dear customer, your {app} account shows suspicious activity. Verify immediately or lose access", "phishing"),
    ("Your Aadhaar linked to {bank} will be deactivated in {time}. Update now to avoid deactivation", "phishing"),
    ("Share your OTP to receive a refund of Rs {amount} from {company}", "otp"),
    ("Your OTP is required to process your Rs {amount} cashback. Reply with the OTP you received", "otp"),
    ("{company} customer support: share your OTP to verify your order and avoid cancellation", "otp"),
    ("Work from home opportunity! Earn Rs {amount} weekly, just pay Rs 999 registration fee to start", "job"),
    ("{company} is hiring part-time data entry staff, salary Rs {amount}/month, pay Rs 1500 for training kit", "job"),
    ("Congratulations {name}, you are selected for a job at {company}. Pay Rs 2000 verification fee to confirm", "job"),
    ("Instant personal loan of Rs {amount} approved! No documents needed, click to receive in your account", "loan"),
    ("Your loan of Rs {amount} is ready for disbursement. Pay a processing fee of Rs 2999 to release it", "loan"),
    ("Get a loan up to Rs {amount} at 1% interest, no CIBIL check required. Apply now via this link", "loan"),
    ("Your {app} payment of Rs {amount} failed. Click here to retry and receive instant cashback", "upi_fraud"),
    ("You have received Rs {amount} via {app}. Enter your UPI PIN on this link to accept the payment", "upi_fraud"),
    ("Invest Rs {amount} today and double your money in 7 days, guaranteed returns with zero risk", "investment"),
    ("Join our trading group and earn Rs {amount} daily with guaranteed profit, no risk involved", "investment"),
    ("Final notice: pay Rs {amount} immediately or legal action will be taken against you under IT Act", "phishing"),
    ("Your parcel from {company} is held at customs. Pay Rs 350 duty immediately to release it", "phishing"),
    ("Dear {name}, your electricity connection will be disconnected in {time} due to unpaid bill. Pay now via link", "phishing"),
]

SAFE_TEMPLATES = [
    ("Hi {name}, are we still meeting for lunch tomorrow?", "general"),
    ("Reminder: your {bank} EMI of Rs {amount} is due on the 5th of this month", "general"),
    ("Your order from {company} has been shipped and will arrive by Thursday", "general"),
    ("Your OTP for {bank} net banking login is 4829. Do not share this with anyone", "otp"),
    ("This is to confirm your OTP 5521 for verifying your new device. Never share it with anyone", "otp"),
    ("Your salary of Rs {amount} has been credited to your {bank} account ending 4521", "general"),
    ("Payment of Rs {amount} sent successfully to {name} via {app}. Reference number 234567890", "upi_fraud"),
    ("Your interview at {company} is scheduled for Monday 10am, please carry your resume", "job"),
    ("HR Team: your offer letter has been emailed to you, please review and sign it", "job"),
    ("Your {bank} statement for this month is now available on net banking", "general"),
    ("Your mutual fund SIP of Rs {amount} has been debited successfully this month", "investment"),
    ("Team, don't forget the project submission deadline is this Friday", "general"),
    ("Your {company} order has been delivered, rate your experience in the app", "general"),
    ("Dear {name}, your doctor's appointment is confirmed for tomorrow 11am", "general"),
    ("Your flight is confirmed, check-in opens 48 hours before departure", "general"),
    ("Never share your OTP, PIN, or CVV with anyone, even if they claim to be from the bank", "awareness"),
    ("Alert: new device login detected on your account. If this wasn't you, please reset your password", "awareness"),
    ("Your {bank} locker rent of Rs {amount} is due, please pay at the nearest branch", "general"),
    ("Meeting rescheduled to 3pm tomorrow in conference room B, please confirm attendance", "general"),
    ("Your PF account has been updated with your new UAN number, login to check your balance", "general"),
    ("Thanks for the update, I'll get back to you by end of day", "general"),
    ("Your water bill payment of Rs {amount} was successful, thank you", "general"),
    ("Your {company} subscription renews on the 1st, no action needed", "general"),
]


def fill(template):
    return template.format(
        bank=random.choice(banks),
        amount=random.choice(amounts),
        name=random.choice(names),
        company=random.choice(companies),
        app=random.choice(apps),
        time=random.choice(times),
    )


def generate(templates, label, n_per_template):
    rows = []
    for text, category in templates:
        seen = set()
        attempts = 0
        while len(seen) < n_per_template and attempts < n_per_template * 5:
            attempts += 1
            msg = fill(text)
            if msg not in seen:
                seen.add(msg)
                rows.append((msg, label, category))
    return rows


def main():
    # Load the original hand-written dataset
    original_rows = []
    with open("scam_dataset.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            original_rows.append((row["message"], row["label"], row["category"]))

    scam_rows = generate(SCAM_TEMPLATES, "scam", n_per_template=6)
    safe_rows = generate(SAFE_TEMPLATES, "safe", n_per_template=6)

    all_rows = original_rows + scam_rows + safe_rows
    random.shuffle(all_rows)

    with open("scam_dataset.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["message", "label", "category"])
        writer.writerows(all_rows)

    scam_count = sum(1 for r in all_rows if r[1] == "scam")
    safe_count = sum(1 for r in all_rows if r[1] == "safe")
    print(f"Expanded dataset: {len(all_rows)} total rows")
    print(f"Scam: {scam_count}, Safe: {safe_count}")


if __name__ == "__main__":
    main()
