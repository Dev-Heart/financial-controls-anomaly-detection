import streamlit as st
import pandas as pd
import os
import sys
import numpy as np

# Ensure we can import from the scripts directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
from main import (
    detect_duplicate_payments,
    detect_unusual_timing,
    detect_round_number_abuse,
    detect_threshold_avoidance,
    analyze_benford,
    detect_fuzzy_duplicates
)

st.set_page_config(page_title="Financial Anomaly Detector", layout="wide")

st.title("🛡️ Financial Controls & Anomaly Detection System")
st.markdown("---")

# Sidebar Configuration
st.sidebar.header("⚙️ Configuration")
threshold = st.sidebar.slider("Approval Threshold", min_value=1000, max_value=50000, value=10000, step=500)
uploaded_file = st.sidebar.file_uploader("Upload Transaction CSV", type="csv")

st.sidebar.markdown("---")
st.sidebar.header("🎨 User Preferences")
currency = st.sidebar.selectbox("Currency Symbol", ["$", "R", "€", "£", "₦", "¥", "Br"], index=1)
decimal_points = st.sidebar.number_input("Decimal Precision", min_value=0, max_value=4, value=2)
thousands_sep = st.sidebar.checkbox("Use Thousands Separator", value=True)

# Formatting Helper
def format_currency(val):
    if thousands_sep:
        return f"{currency}{val:,.{decimal_points}f}"
    else:
        return f"{currency}{val:.{decimal_points}f}"

# Data Loading & Mapping
def detect_columns(columns):
    """
    Attempt to auto-detect Date, Amount, and Vendor columns based on name patterns.
    """
    mapping = {"date": None, "amount": None, "vendor": None}
    for col in columns:
        col_lower = col.lower()
        if "date" in col_lower and not mapping["date"]:
            mapping["date"] = col
        elif ("amount" in col_lower or "amt" in col_lower or "sum" in col_lower or "total" in col_lower) and not mapping["amount"]:
            mapping["amount"] = col
        elif ("vendor" in col_lower or "payee" in col_lower or "merchant" in col_lower or "supplier" in col_lower) and not mapping["vendor"]:
            mapping["vendor"] = col
    return mapping

def load_and_map_data(file):
    try:
        df = pd.read_csv(file)
        if df.empty:
            st.error("The uploaded CSV is empty.")
            return None
        
        st.sidebar.subheader("🗺️ Column Mapping")
        st.sidebar.info("Map your CSV headers to the expected fields.")
        
        auto_map = detect_columns(df.columns)
        
        date_col = st.sidebar.selectbox("Date Column", df.columns, index=list(df.columns).index(auto_map["date"]) if auto_map["date"] in df.columns else 0)
        amount_col = st.sidebar.selectbox("Amount Column", df.columns, index=list(df.columns).index(auto_map["amount"]) if auto_map["amount"] in df.columns else (1 if len(df.columns) > 1 else 0))
        vendor_col = st.sidebar.selectbox("Vendor Column", df.columns, index=list(df.columns).index(auto_map["vendor"]) if auto_map["vendor"] in df.columns else (2 if len(df.columns) > 2 else 0))
        
        # Critical: Transform for internal logic
        df_mapped = df[[date_col, amount_col, vendor_col]].copy()
        df_mapped.columns = ['date', 'amount', 'vendor']
        
        # Add original transaction_id if it exists, else create one
        if "transaction_id" in df.columns:
            df_mapped['transaction_id'] = df["transaction_id"]
        else:
            df_mapped['transaction_id'] = [f"TXN_{i+1}" for i in range(len(df_mapped))]
        
        # Casting
        df_mapped['date'] = pd.to_datetime(df_mapped['date'], errors='coerce')
        df_mapped['amount'] = pd.to_numeric(df_mapped['amount'], errors='coerce')
        
        # Validation
        if df_mapped['date'].isna().any():
            st.sidebar.warning(f"⚠️ Some values in {date_col} could not be parsed as dates.")
        if df_mapped['amount'].isna().any():
            st.sidebar.error(f"🚨 Non-numeric values found in {amount_col}. Analysis might be inaccurate.")
            
        return df_mapped.dropna(subset=['date', 'amount']) # Keep valid rows
    except Exception as e:
        st.error(f"Error processing CSV: {e}")
        return None

if uploaded_file is not None:
    df_raw = load_and_map_data(uploaded_file)
else:
    sample_path = os.path.join(os.path.dirname(__file__), "data/sample_transactions.csv")
    if os.path.exists(sample_path):
        # Sample file is already structured correctly, but we use the same loader for consistency
        df_raw = load_and_map_data(sample_path)
    else:
        st.error("No data found. Please upload a CSV.")
        st.stop()

if df_raw is None or df_raw.empty:
    st.info("👋 **Welcome! To begin the forensic analysis:**")
    st.markdown("""
    1. **Upload your CSV** in the sidebar.
    2. **Check the Mapping**: Look at the sidebar 🗺️. If you see warnings about dates or amounts, you likely need to select different columns.
    3. **Verify Date Format**: Ensure your date column is in a standard format (e.g., YYYY-MM-DD or MM/DD/YYYY).
    """)
    if uploaded_file:
        st.error(f"🚨 **Mapping Error**: 0 valid rows found in '{uploaded_file.name}' after mapping and cleanup. Please check your column selections in the sidebar.")
    st.stop()
else:
    st.success(f"✅ Successfully loaded and mapped **{len(df_raw)}** valid transactions.")

# Analysis execution
duplicates = detect_duplicate_payments(df_raw)
unusual_timing = detect_unusual_timing(df_raw)
round_num = detect_round_number_abuse(df_raw)
threshold_flags = detect_threshold_avoidance(df_raw, threshold=threshold)
benford_data = analyze_benford(df_raw)
fuzzy_vendors = detect_fuzzy_duplicates(df_raw)

# Overview Metrics
st.subheader("📊 Analysis Insights")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Duplicates", len(duplicates))
with col2:
    st.metric("Weekend Payments", len(unusual_timing))
with col3:
    st.metric("Round Numbers", len(round_num))
with col4:
    st.metric("Near Threshold", len(threshold_flags))

# Visualization & Forensic Tabs
tabs = st.tabs(["💡 General Findings", "🕵️ Forensic Analysis", "📋 Detailed Results"])

with tabs[0]:
    st.markdown("### 📈 Risk Overview")
    labels = ["Duplicates", "Weekend", "Round Numbers", "Near Threshold"]
    counts = [len(duplicates), len(unusual_timing), len(round_num), len(threshold_flags)]
    df_stats = pd.DataFrame({"Anomaly Type": labels, "Count": counts})
    st.bar_chart(df_stats.set_index("Anomaly Type"))

with tabs[1]:
    st.markdown("### 🧬 Forensic Suite")
    fcol1, fcol2 = st.columns(2)
    
    with fcol1:
        st.markdown("#### Benford's Law Analysis")
        st.info("Checks if the frequency of leading digits follows the natural logarithmic distribution. Significant deviations can indicate manual data entry fraud.")
        if not benford_data.empty:
            st.line_chart(benford_data)
        else:
            st.warning("Insufficient data for Benford Analysis.")
            
    with fcol2:
        st.markdown("#### Fuzzy Vendor Matching")
        st.info("Identifying similar vendor names (e.g., 'ABC Corp' vs 'ABC Corp.').")
        if not fuzzy_vendors.empty:
            st.dataframe(fuzzy_vendors, use_container_width=True)
        else:
            st.success("No suspicious similar vendor names found.")

with tabs[2]:
    st.markdown("### 📋 Detailed Trace")
    sub_tabs = st.tabs(["Duplicates", "Unusual Timing", "Round Numbers", "Threshold Flags"])
    
    # Styled table display
    def display_styled_df(df):
        if not df.empty:
            df_display = df.copy()
            if 'amount' in df_display.columns:
                df_display['amount'] = df_display['amount'].apply(format_currency)
            st.dataframe(df_display, use_container_width=True)
        else:
            st.success("Clean! No anomalies found in this category.")

    with sub_tabs[0]:
        display_styled_df(duplicates)
    with sub_tabs[1]:
        display_styled_df(unusual_timing)
    with sub_tabs[2]:
        display_styled_df(round_num)
    with sub_tabs[3]:
        st.write(f"Transactions between {format_currency(threshold*0.9)} and {format_currency(threshold)}")
        display_styled_df(threshold_flags)

# Raw Data View
if st.checkbox("Show Raw Transaction Data"):
    df_styled = df_raw.copy()
    df_styled['amount'] = df_styled['amount'].apply(format_currency)
    st.dataframe(df_styled, use_container_width=True)

st.markdown("---")
st.caption("Developed by Divine Heart • Portfolio Educational Project")
