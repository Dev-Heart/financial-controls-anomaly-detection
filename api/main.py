import pandas as pd
import numpy as np
import json
import logging
import os
import matplotlib.pyplot as plt
from thefuzz import fuzz, process

# ----------------------------
# Configuration
# ----------------------------
# Ensure we load from the project root
config_path = "config.json"
if os.path.exists(config_path):
    with open(config_path) as f:
        config = json.load(f)
else:
    config = {}

THRESHOLD_AMOUNT = config.get("threshold_amount", 10000)

# ----------------------------
# Logging
# ----------------------------
# Ensure output directory exists before logging
os.makedirs("outputs", exist_ok=True)
logging.basicConfig(filename='outputs/processing.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# ----------------------------
# Load transactions
# ----------------------------
def load_transactions(file_path):
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} transactions from {file_path}")
        logging.info(f"Loaded {len(df)} transactions from {file_path}")
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        logging.error(f"Error loading CSV: {e}")
        return pd.DataFrame()

# ----------------------------
# Anomaly Detection Functions
# ----------------------------
def detect_duplicate_payments(df):
    # Mapping 'Payee' logic to 'vendor' and 'Date' to 'date'
    duplicates = df[df.duplicated(subset=['date', 'amount', 'vendor'], keep=False)]
    print(f"Duplicate payments flagged: {len(duplicates)}")
    logging.info(f"Duplicate payments flagged: {len(duplicates)}")
    return duplicates

def detect_unusual_timing(df):
    # Ensure date is datetime
    df['date'] = pd.to_datetime(df['date'])
    unusual = df[df['date'].dt.weekday >= 5]  # Sat/Sun
    print(f"Unusual timing flagged: {len(unusual)}")
    logging.info(f"Unusual timing flagged: {len(unusual)}")
    return unusual

def detect_round_number_abuse(df):
    round_numbers = df[df['amount'] % 1000 == 0]
    print(f"Round-number abuse flagged: {len(round_numbers)}")
    logging.info(f"Round-number abuse flagged: {len(round_numbers)}")
    return round_numbers

def detect_threshold_avoidance(df, threshold=THRESHOLD_AMOUNT):
    flagged = df[(df['amount'] >= threshold * 0.9) & (df['amount'] < threshold)]
    print(f"Threshold avoidance flagged: {len(flagged)}")
    logging.info(f"Threshold avoidance flagged: {len(flagged)}")
    return flagged

# ----------------------------
# Fraud Hunter Functions
# ----------------------------
def analyze_benford(df):
    """
    Perform Benford's Law analysis on the leading digits of transaction amounts.
    """
    # Extract leading digits (1-9)
    amounts = df['amount'].dropna()
    leading_digits = amounts.apply(lambda x: int(str(abs(x))[0]) if abs(x) >= 1 else None).dropna()
    
    if leading_digits.empty:
        return pd.DataFrame()
    
    counts = leading_digits.value_counts(normalize=True).sort_index()
    
    # Standard Benford distribution
    benford_ref = pd.Series({d: np.log10(1 + 1/d) for d in range(1, 10)})
    
    analysis = pd.DataFrame({
        'Actual': counts,
        'Expected': benford_ref
    }).fillna(0)
    
    logging.info("Performed Benford's Law analysis")
    return analysis

def detect_fuzzy_duplicates(df, threshold=90):
    """
    Detect similar vendor names using fuzzy matching.
    """
    vendors = df['vendor'].unique()
    fuzzy_matches = []
    
    for i, v1 in enumerate(vendors):
        for v2 in vendors[i+1:]:
            score = fuzz.ratio(str(v1), str(v2))
            if score >= threshold:
                fuzzy_matches.append({
                    'Vendor 1': v1,
                    'Vendor 2': v2,
                    'Similarity Score': score
                })
    
    logging.info(f"Fuzzy matching detected {len(fuzzy_matches)} similar vendor name pairs")
    return pd.DataFrame(fuzzy_matches)

# ----------------------------
# Risk Summary & Export
# ----------------------------
def generate_risk_summary(duplicate, timing, round_number, threshold, output_file="outputs/risk_summary.csv"):
    summary = {
        "Metric": ["Duplicate Payments", "Unusual Timing", "Round-Number Abuse", "Threshold Avoidance"],
        "Count": [len(duplicate), len(timing), len(round_number), len(threshold)]
    }
    df_summary = pd.DataFrame(summary)
    df_summary.to_csv(output_file, index=False)
    
    print("\n=== RISK SUMMARY ===")
    print(df_summary.to_string(index=False))
    print("\nControl recommendations:")
    print("- Review duplicate payments")
    print("- Investigate unusual timing transactions")
    print("- Monitor round-number payments")
    print("- Enforce thresholds and approval limits")
    print(f"\nRisk summary exported to {output_file}")
    logging.info(f"Risk summary exported to {output_file}")

def visualize_anomalies(duplicate, timing, round_number, threshold, output_file="outputs/anomaly_summary.png"):
    """
    Create a bar chart of flagged anomalies and save as PNG.
    """
    labels = ["Duplicate Payments", "Unusual Timing", "Round-Number Abuse", "Threshold Avoidance"]
    counts = [len(duplicate), len(timing), len(round_number), len(threshold)]

    plt.figure(figsize=(10,6))
    bars = plt.bar(labels, counts, color='teal')
    
    # Add value labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, int(yval), ha='center', va='bottom')
    
    plt.title("Transaction Anomalies Summary")
    plt.ylabel("Number of Transactions")
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    
    print(f"Anomaly summary chart saved to {output_file}")
    logging.info(f"Anomaly summary chart saved to {output_file}")

# ----------------------------
# Main
# ----------------------------
def main():
    # File path for root directory execution
    file_path = "data/sample_transactions.csv"
    df = load_transactions(file_path)
    
    if not df.empty:
        duplicates = detect_duplicate_payments(df)
        unusual = detect_unusual_timing(df)
        round_num = detect_round_number_abuse(df)
        threshold_flags = detect_threshold_avoidance(df)
        
        generate_risk_summary(duplicates, unusual, round_num, threshold_flags)
        visualize_anomalies(duplicates, unusual, round_num, threshold_flags)
    else:
        print("No transactions to process.")

if __name__ == "__main__":
    main()
