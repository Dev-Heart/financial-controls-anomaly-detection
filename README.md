# Financial Controls & Anomaly Detection System

## Overview
This project is a portfolio-ready **Financial Controls & Anomaly Detection System** designed to bridge the gap between accounting, internal controls, and data analytics. It processes general ledger or transaction data to identify potential fraud, errors, or control bypasses.

## Key Features
- **Duplicate Payment Detection**: Identifies potential double payments based on identical amount, vendor, and date.
- **Unusual Timing Detection**: Flags transactions occurring on weekends or outside normal business hours.
- **Round-Number Abuse**: Detects transactions with exact round numbers (multiple of 1,000), a common red flag in manual fraud.
- **Threshold Avoidance**: Highlights transactions just below the \$10,000 approval threshold, indicating possible attempts to bypass manager review.
- **Benford's Law Analysis**: Mathematical anomaly detection based on leading-digit frequency to identify artificial data patterns.
- **Fuzzy Vendor Matching**: Automated detection of similar vendor names (e.g., "ABC Corp" vs "ABC Corp.") to catch potential ghost accounts.
- **Visual Analytics**: Interactive Streamlit dashboard with automated bar charts and forensic diagnostic plots.
- **User Personalization**: Toggle between different currency regions ($, €, £, ₦) and numerical precision settings.
- **Reporting & Logging**: Exports a Risk Summary (CSV) and maintains a persistent audit trail (Log).
- **Automated Verification**: Includes a comprehensive suite of unit tests to ensure detection accuracy.
- **Configurable Settings**: Customizable thresholds via `config.json`.

## Project Structure
```text
financial-controls-anomaly-detection/
├── data/                 # Sample and input CSV transactions
├── scripts/              # Core logic and tests
│   ├── main.py           # Main analysis script
│   └── test_detector.py # Automated unit tests
├── outputs/              # Exported reports, logs, and charts
├── config.json           # System configuration and thresholds
├── requirements.txt      # Project dependencies
└── venv/                 # Python virtual environment
```

## Setup & Usage

### 1. Prerequisites
- Python 3.9.6

### 2. Setup
Clone the repository and set up the virtual environment:
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Analysis
Execute the detector from the project root:
```bash
python3 scripts/main.py
```

### 4. Launch Interactive Dashboard
Run the Streamlit app for a visual, interactive experience:
```bash
streamlit run scripts/app.py
```

### 5. Run Tests
Verify system stability with automated tests:
```bash
python3 scripts/test_detector.py
```

### 5. Review Results
- Check the terminal output for an immediate risk summary.
- View `outputs/anomaly_summary.png` for a graphical overview.
- View `outputs/risk_summary.csv` for a structured report.
- Review `outputs/processing.log` for execution details.

## Recruiter Value
This system demonstrates:
- **Accounting Logic**: Understanding of internal controls and fraud risk factors.
- **Data Reasoning**: Ability to translate control objectives into technical detection rules.
- **Automation Skills**: Using Python/Pandas to scale auditing and risk management.
## Disclaimer
This tool and example outputs are for educational and portfolio purposes only. The scenarios, assumptions, and outputs are illustrative and should not be interpreted as professional financial advice.

Developed by **Divine Heart**. For inquiries, feedback, or collaboration, visit [GitHub](https://github.com/Dev-Heart).
