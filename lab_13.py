import re

class RegexSpamFilter:
    """Dynamic Spam Filter engine using weighted regular expressions."""

    def __init__(self, threshold=50):
        # Classification threshold score (default >= 50 is SPAM)
        self.threshold = threshold
        
        # Weighted Regex Pattern Rules
        # (Pattern Name, Regular Expression, Weight/Score Impact)
        self.rules = [
            (
                "Urgency / Action Words",
                r'\b(act now|urgent|immediate action|limited time|offer expires|claim now|don\'?t delay)\b',
                25
            ),
            (
                "Financial / Money Scams",
                r'\b(make money fast|100% free|risk[- ]free|wire transfer|passive income|guaranteed profits|crypto bonus|double your money)\b',
                30
            ),
            (
                "Phishing / Account Triggers",
                r'\b(verify your account|account suspended|login below|update billing|security alert|bank details)\b',
                35
            ),
            (
                "Suspicious / Shortened Links",
                r'https?://(bit\.ly|tinyurl\.com|t\.co|cutt\.ly|ow\.ly|is\.gd)/[a-zA-Z0-9]+',
                20
            ),
            (
                "Obfuscated Spam Words",
                r'\b(f[.\s_-]*r[.\s_-]*e[.\s_-]*e|c[.\s_-]*a[.\s_-]*s[.\s_-]*h|w[.\s_-]*i[.\s_-]*n)\b',
                25
            ),
            (
                "Excessive Currency / Large Amounts",
                r'(\$\s*\d{1,3}(,\d{3})*|\b\d+\s*(dollars|usd|btc|eth)\b)',
                15
            ),
            (
                "Excessive Exclamation Marks",
                r'!{2,}',
                10
            ),
            (
                "Excessive ALL CAPS Words",
                r'\b[A-Z]{4,}\b',
                10
            )
        ]

    def analyze(self, text: str):
        """Scans text against spam regex rules and calculates total spam score."""
        total_score = 0
        matched_details = []

        for rule_name, pattern, weight in self.rules:
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            
            # Special case: count how many ALL CAPS words exist to weight properly
            if rule_name == "Excessive ALL CAPS Words":
                # Filter out standard acronyms or single characters
                caps_matches = [m for m in matches if m not in ('HTTP', 'HTTPS', 'HTML')]
                if len(caps_matches) >= 2:
                    score_added = min(len(caps_matches) * 5, 20)
                    total_score += score_added
                    matched_details.append((rule_name, caps_matches, score_added))
            elif matches:
                # Deduplicate matched terms for clean reporting
                unique_matches = list(set(matches))
                total_score += weight
                matched_details.append((rule_name, unique_matches, weight))

        is_spam = total_score >= self.threshold
        return {
            "score": total_score,
            "is_spam": is_spam,
            "matches": matched_details
        }


def print_spam_report(text: str, result: dict, threshold: int):
    """Prints a formatted evaluation report in the terminal."""
    print("\n" + "=" * 60)
    print("EMAIL / MESSAGE CONTENT:")
    print("-" * 60)
    print(text.strip())
    print("-" * 60)
    
    status_symbol = "🚨 SPAM DETECTED" if result["is_spam"] else "✅ CLEAN / HAM"
    print(f"Status        : {status_symbol}")
    print(f"Spam Score    : {result['score']} / {threshold} (Threshold)")
    
    if result["matches"]:
        print("\nTriggered Rules Breakdown:")
        print(f"  {'Rule Category':<30} {'Weight':<8} {'Matched Pattern(s)'}")
        print("  " + "-" * 56)
        for rule_name, matches, weight in result["matches"]:
            # Format match string neatly
            str_matches = ", ".join([str(m) for m in matches])
            if len(str_matches) > 25:
                str_matches = str_matches[:22] + "..."
            print(f"  {rule_name:<30} +{weight:<7} {str_matches}")
    else:
        print("\nNo spam rules triggered.")
    print("=" * 60 + "\n")


def main():
    filter_engine = RegexSpamFilter(threshold=40)

    # Sample test messages
    sample_spam = """
    URGENT: Verify your account immediately! 
    You have won $5,000 in guaranteed profits. Claim now at http://bit.ly/xyz123 
    DON'T DELAY, offer expires today!! F.R.E.E ACCESS!
    """

    sample_ham = """
    Hi Alex,
    Could you please review the lab_12.py script when you have time? 
    We need to submit the assignment before tomorrow afternoon.
    Thanks!
    """

    print("=== Dynamic Regex Spam Filter System ===")
    
    # Run pre-configured tests
    print_spam_report(sample_spam, filter_engine.analyze(sample_spam), filter_engine.threshold)
    print_spam_report(sample_ham, filter_engine.analyze(sample_ham), filter_engine.threshold)

    # Interactive Mode
    print("Interactive Mode: Type or paste a message to test (or 'exit' to quit)")
    
    while True:
        try:
            user_input = input("\nEnter message > ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue
        if user_input.lower() in ('exit', 'quit'):
            break

        analysis = filter_engine.analyze(user_input)
        print_spam_report(user_input, analysis, filter_engine.threshold)


if __name__ == '__main__':
    main()