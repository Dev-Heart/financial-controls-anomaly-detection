from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from main import (
    detect_duplicate_payments,
    detect_unusual_timing,
    detect_round_number_abuse,
    detect_threshold_avoidance,
    analyze_benford,
    detect_fuzzy_duplicates
)

app = Flask(__name__)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Convert to DataFrame
        # Expecting input: [{"date": "...", "amount": 123, "vendor": "..."}, ...]
        df = pd.DataFrame(data)
        
        # Data Cleaning
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
        # Drop invalid rows
        df = df.dropna(subset=['date', 'amount'])
        
        if df.empty:
            return jsonify({"error": "No valid data after parsing"}), 400

        # Run Detectors
        # 1. Duplicates
        duplicates = detect_duplicate_payments(df)
        
        # 2. Timing
        unusual_timing = detect_unusual_timing(df)
        
        # 3. Round Numbers
        round_numbers = detect_round_number_abuse(df)
        
        # 4. Threshold Avoidance - getting threshold from request or default
        threshold = request.args.get('threshold', default=10000, type=float) 
        # Alternatively check if it's in the body, but usually query params for config
        
        threshold_flags = detect_threshold_avoidance(df, threshold=threshold)
        
        # 5. Benford
        benford_analysis = analyze_benford(df)
        # Convert Benford result to simple dict for JSON
        benford_json = []
        if not benford_analysis.empty:
            # benford_analysis has 'Actual' and 'Expected' columns
            # We want to send it as a list of points
            benford_analysis['Digit'] = benford_analysis.index
            benford_json = benford_analysis.to_dict(orient='records')
            
        # 6. Fuzzy Duplicates
        fuzzy_duplicates = detect_fuzzy_duplicates(df)
        
        # Prepare Response
        response = {
            "summary": {
                "total_transactions": len(df),
                "duplicates": len(duplicates),
                "unusual_timing": len(unusual_timing),
                "round_numbers": len(round_numbers),
                "threshold_flags": len(threshold_flags)
            },
            "details": {
                "duplicates": duplicates.to_dict(orient='records') if not duplicates.empty else [],
                "unusual_timing": unusual_timing.to_dict(orient='records') if not unusual_timing.empty else [],
                "round_numbers": round_numbers.to_dict(orient='records') if not round_numbers.empty else [],
                "threshold_flags": threshold_flags.to_dict(orient='records') if not threshold_flags.empty else [],
                "benford": benford_json,
                "fuzzy_duplicates": fuzzy_duplicates.to_dict(orient='records') if not fuzzy_duplicates.empty else []
            }
        }
        
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel requires 'app' to be exposed
if __name__ == '__main__':
    app.run(debug=True)
