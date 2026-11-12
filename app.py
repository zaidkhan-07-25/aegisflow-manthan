import streamlit as st
import pandas as pd
import numpy as np
import re
import glob
import plotly.express as px
from sklearn.ensemble import IsolationForest

# 1. Clean Corporate Page Setup
st.set_page_config(page_title="AegisFlow | Shadow IT Governance", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; color: #0F172A; }
    section[data-testid="stSidebar"] { background-color: #0F172A; }
    section[data-testid="stSidebar"] * { color: #F8FAFC !important; }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 4px solid #2563EB;
        padding: 16px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .browser-box {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 12px;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
        overflow: hidden;
    }
    .browser-top {
        background: #F1F5F9;
        padding: 10px 16px;
        border-bottom: 1px solid #E2E8F0;
        font-family: monospace;
        font-size: 13px;
        color: #334155;
    }
    .popup-red {
        background: #FEF2F2;
        border: 2px solid #EF4444;
        border-radius: 10px;
        padding: 20px;
        margin: 18px;
    }
    .popup-amber {
        background: #FFFBEB;
        border: 2px solid #F59E0B;
        border-radius: 10px;
        padding: 20px;
        margin: 18px;
    }
    .popup-green {
        background: #ECFDF5;
        border: 2px solid #10B981;
        border-radius: 10px;
        padding: 20px;
        margin: 18px;
    }
</style>
""", unsafe_allow_html=True)

# 2. Load 50-Row Dataset
def get_data():
    csv_files = glob.glob("*.csv")
    if csv_files:
        df = pd.read_csv(csv_files[0])
    else:
        np.random.seed(42)
        base = [
            ("Finance", "iLovePDF Online", "Online Tool", "Approved system too slow", "Q3_Audit_Financials.pdf", "Confidential Financial", 42.5, "None", "No", 0, "No", "Adobe Acrobat Enterprise", 78.5, "Immediate Attention", "RESTRICT"),
            ("Marketing", "ChatGPT Free Web", "AI Assistant", "Missing AI feature", "Festive_Campaign_Copy.docx", "Public / Non-Sensitive", 1.2, "Basic Profile Read", "Yes", 0, "Yes", "Microsoft Copilot", 22.0, "Low-Risk Experimentation", "SANDBOX"),
            ("R&D Engineering", "Cursor AI IDE", "AI Assistant", "Missing AI feature", "Payment_Gateway_Core.py", "Proprietary Source Code", 18.4, "Basic Profile Read", "No", 1650, "Yes", "None", 48.0, "Needs Review", "APPROVE"),
            ("HR", "Unknown-Resume-Parser.ru", "Online Tool", "Urgent deadline", "Candidate_Aadhaar_PAN.xlsx", "Customer / Employee PII", 85.0, "Mail.ReadWrite & Files.ReadWrite.All", "Yes", 0, "No", "Workday HR AI", 96.0, "Immediate Attention", "RESTRICT"),
            ("Sales", "Grammarly Chrome Ext", "Browser Extension", "Approved system too slow", "Client_Pitch_Emails.txt", "Internal Business", 3.1, "Browser DOM ReadAll", "Yes", 1200, "Yes", "Microsoft Editor", 44.0, "Needs Review", "REPLACE"),
            ("Operations", "Notion Personal", "Online Tool", "Approved system too slow", "Supply_Chain_Tracker.md", "Internal Business", 8.5, "Basic Profile Read", "Yes", 800, "Yes", "Microsoft Loop", 52.0, "Needs Review", "REPLACE"),
            ("Finance", "Julius AI Free", "AI Assistant", "Missing AI feature", "Customer_Billing_Raw.csv", "Customer / Employee PII", 120.0, "Files.ReadWrite.All", "Yes", 1800, "No", "Power BI Copilot", 91.5, "Immediate Attention", "RESTRICT"),
            ("Marketing", "Excalidraw Web", "Online Tool", "Unaware of alternative", "Campaign_Flow_Draft.png", "Public / Non-Sensitive", 0.8, "None", "No", 0, "Yes", "None", 12.0, "Low-Risk Experimentation", "SANDBOX"),
            ("Operations", "WeTransfer Free", "File Sharing", "Approved system too slow", "Vendor_Contracts_2026.zip", "Confidential Financial", 210.0, "None", "Yes", 900, "Yes", "OneDrive Corporate", 68.0, "Immediate Attention", "REPLACE"),
            ("Marketing", "Canva Pro Personal", "Online Tool", "Approved system too slow", "Social_Media_Banners.zip", "Public / Non-Sensitive", 14.2, "Basic Profile Read", "Yes", 1000, "Yes", "Adobe Express Corp", 36.0, "Needs Review", "REPLACE"),
        ]
        rows = []
        for i in range(50):
            s = base[i % len(base)]
            rows.append([f"LOG-{101+i}", f"emp{i+1}@apexcorp.in", s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8], s[9], s[10], s[11], s[12], s[13], s[14]])
        cols = ["Log_ID", "Employee_Email", "Entra_Department", "Defender_Tool_Detected", "Tool_Category", "Reason_Adopted", "Defender_File_Uploaded", "Data_Sensitivity", "Defender_Upload_MB", "Entra_OAuth_Scope", "Personal_Account_Used", "Monthly_Cost_INR", "Vendor_SOC2_Safe", "Approved_Alternative", "Risk_Score", "Activity_Status", "Review_Decision"]
        df = pd.DataFrame(rows, columns=cols)

    iso = IsolationForest(contamination=0.20, random_state=42)
    df["ML_Flag"] = np.where(iso.fit_predict(df[["Defender_Upload_MB", "Risk_Score"]]) == -1, "Anomaly", "Normal")
    df["Status"] = np.where(df["Review_Decision"].isin(["RESTRICT", "REPLACE"]), "Action Needed", "Resolved")
    return df

if "df" not in st.session_state:
    st.session_state.df = get_data()

df = st.session_state.df

# 3. Simple 3-Step Left Sidebar
with st.sidebar:
    st.markdown("## 🛡️ AegisFlow")
    st.caption("Smart Shadow IT & AI Governance")
    st.markdown("---")
    step = st.radio(
        "DEMO WALKTHROUGH:",
        [
            "1️⃣ Employee View (Live Popup)",
            "2️⃣ Safe AI Data Scrubber",
            "3️⃣ Manager & IT Dashboard"
        ]
    )
    st.markdown("---")
    st.caption("Manthan 2.0 | Challenge 8\nNaman • Zaid • Rohan • Hare Raj")
    if st.button("🔄 Reset Demo"):
        st.session_state.df = get_data()
        st.rerun()

# ==============================================================================
# STEP 1: EMPLOYEE LAPTOP VIEW (SIMPLE & VISUAL POPUP)
# ==============================================================================
if step == "1️⃣ Employee View (Live Popup)":
    st.title("1️⃣ What Happens on an Employee's Laptop?")
    st.write("Pick a scenario on the left to see the exact popup that appears on the employee's screen:")

    left, right = st.columns([1, 1.4], gap="large")

    with left:
        st.subheader("Choose Scenario")
        scenario = st.radio(
            "What is the employee trying to do?",
            [
                "🚨 Finance uploads Tax/PAN PDF to iLovePDF",
                "💸 Marketing buys Canva Pro on personal card",
                "✅ Designer sketches public wireframe on Excalidraw"
            ]
        )
        uploaded_file = st.file_uploader("Or drop any file from your laptop to test:")
        
        if st.button("▶️ Trigger Live Check & Log Incident", type="primary", use_container_width=True):
            st.toast("Live check executed and logged to IT Dashboard!", icon="🛡️")

    with right:
        st.subheader("Employee's Browser Screen")

        if "Finance" in scenario or uploaded_file is not None:
            fname = uploaded_file.name if uploaded_file else "Q3_Tax_Audit_PAN.pdf"
            st.markdown(f"""
            <div class="browser-box">
                <div class="browser-top">🔴 🟡 🟢 &nbsp; https://www.ilovepdf.com/merge_pdf</div>
                <div class="popup-red">
                    <h3 style="color:#DC2626; margin:0;">⛔ UPLOAD BLOCKED BY AEGISFLOW</h3>
                    <p style="color:#1E293B; font-size:15px; margin-top:8px;">
                        You tried to upload <b>{fname}</b> containing confidential financial / PAN data to an unapproved website.
                    </p>
                    <p style="color:#0F172A; font-size:14px; background:#FFFFFF; padding:12px; border-radius:8px; border:1px solid #FECACA;">
                        <b>✅ How to finish your work safely right now:</b><br>
                        Use <b>Adobe Acrobat Enterprise</b> — ApexCorp already pays for it and your data stays 100% private.
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.button("↗️ Open Adobe Acrobat Enterprise (Approved Tool)", type="primary", use_container_width=True)

        elif "Marketing" in scenario:
            st.markdown("""
            <div class="browser-box">
                <div class="browser-top">🔴 🟡 🟢 &nbsp; https://www.canva.com/pro/checkout</div>
                <div class="popup-amber">
                    <h3 style="color:#D97706; margin:0;">💡 STOP! COMPANY ALREADY OWNS THIS TOOL</h3>
                    <p style="color:#1E293B; font-size:15px; margin-top:8px;">
                        Buying Canva Pro personally wastes <b>₹12,000/year</b> in duplicate software
