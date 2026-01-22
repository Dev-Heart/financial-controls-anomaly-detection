import unittest
import pandas as pd
import os
import sys

# Ensure we can import from the scripts directory if run from root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from main import detect_duplicate_payments, detect_unusual_timing, detect_round_number_abuse, detect_threshold_avoidance

class TestAnomalyDetection(unittest.TestCase):

    def setUp(self):
        # Sample test DataFrame matching the project's column names
        self.df = pd.DataFrame({
            "transaction_id": ["TXN_T1", "TXN_T2", "TXN_T3", "TXN_T4"],
            "date": ["2025-12-01", "2025-12-06", "2025-12-07", "2025-12-02"],
            "amount": [1000, 9500, 10000, 5000],
            "vendor": ["Vendor A", "Vendor B", "Vendor A", "Vendor C"]
        })
        self.df['date'] = pd.to_datetime(self.df['date'])

    def test_duplicate_payments(self):
        # In our case, duplicates are based on date/amount/vendor
        # Adding a duplicate row for testing with correct data types
        new_row = pd.DataFrame({
            "transaction_id": ["TXN_T5"],
            "date": ["2025-12-01"],
            "amount": [1000],
            "vendor": ["Vendor A"]
        })
        new_row['date'] = pd.to_datetime(new_row['date'])
        test_df = pd.concat([self.df, new_row], ignore_index=True)
        duplicates = detect_duplicate_payments(test_df)
        self.assertEqual(len(duplicates), 2)  # TXN_T1 and TXN_T5

    def test_unusual_timing(self):
        unusual = detect_unusual_timing(self.df)
        self.assertEqual(len(unusual), 2)  # 2025-12-06 and 2025-12-07 are Sat/Sun

    def test_round_number_abuse(self):
        round_num = detect_round_number_abuse(self.df)
        # 1000, 10000, 5000 are multiples of 1000
        self.assertEqual(len(round_num), 3)

    def test_threshold_avoidance(self):
        # Threshold 10000, 9500 is in the 90% range
        threshold_flagged = detect_threshold_avoidance(self.df, threshold=10000)
        self.assertEqual(len(threshold_flagged), 1)

if __name__ == "__main__":
    unittest.main()
