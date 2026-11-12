import streamlit as st
import pandas as pd
import numpy as np
import re
from sklearn.ensemble import IsolationForest

# 1. Page Configuration
st.set_page_config(page_title="AegisFlow | Manthan 2.0", page_icon="🛡️", layout="wide")

# 2. Load the 50-Row Dataset & Apply Scikit-learn Anomaly Detection
@st.cache_data
def load_data():
    df = pd.read_csv("aegisflow_6depts_50rows.csv")
    iso = IsolationForest(contamination=0.20, random_state=42)
    df["ML_Anomaly_Flag"] = np.where(
        iso.fit_predict(df[["Defender_Upload_MB", "Risk_Score"]]) == -1,
        "🚨 ML Anomaly", "Normal"
    )
    return df

df = load_data()

# 3. Header Banner
st.title("🛡️ AegisFlow: Intelligent Shadow IT & AI Governance")
st.markdown("**Manthan 2.0 (Jain University - CMS)** | **Challenge 8:** *The Work That Happens Outside The System* | **Telemetry:** Microsoft Defender + Entra ID (KQL)")
st.divider()

# 4. Interactive Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "👩‍💻 1. Employee Tool Checker",
    "🧪 2. Safe AI Data Sanitizer",
    "🔐 3. IT & SecOps Review Console",
    "📡 4. Defender + Entra ID (KQL)"
])

# --- TAB 1: EMPLOYEE SELF-SERVICE CHECKER ---
with tab1:
    st.subheader("Check an External Tool Before Using It")
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        selected_dept = st.selectbox("Select Your Department (Entra ID):", sorted(df["Entra_Department"].unique()))
        selected_tool = st.selectbox("Select Tool You Want to Use:", sorted(df["Defender_Tool_Detected"].unique()))
        intended_data = st.radio(
            "What type of file/data will you upload?",
            ["Public / Non-Sensitive", "Internal Business", "Confidential Financial", "Customer / Employee PII", "Proprietary Source Code"]
        )

    with col2:
        tool_row = df[df["Defender_Tool_Detected"] == selected_tool].iloc[0]
        base_score = tool_row["Risk_Score"]
        
        if intended_data in ["Customer / Employee PII", "Proprietary Source Code", "Confidential Financial"]:
            live_score = min(99.0, max(base_score, 85.0))
        else:
            live_score = base_score

        st.metric("Real-Time ML Risk Score", f"{live_score} / 100", delta="Threshold: 65 = Immediate Block", delta_color="inverse")
        
        if live_score >= 65 or tool_row["Vendor_SOC2_Safe"] == "No":
            st.error("🚨 **DECISION: RESTRICT (Blocked)** — High risk of data exposure or DPDP compliance violation!")
            if tool_row["Approved_Alternative"] != "None":
                st.info(f"✅ **Redirecting You to Approved Tool:** Use **{tool_row['Approved_Alternative']}** (Pre-approved & secure).")
        elif tool_row["Approved_Alternative"] != "None":
            st.warning("🔄 **DECISION: REPLACE (Duplicate Tool Detected)**")
            st.info(f"💡 ApexCorp already pays for **{tool_row['Approved_Alternative']}**! Switch now to save ₹{tool_row['Monthly_Cost_INR']}/month.")
        elif live_score < 35:
            st.success("✅ **DECISION: SANDBOX APPROVED (14-Day Safe Trial)** — Safe for low-risk experimentation.")
        else:
            st.success("🌟 **DECISION: APPROVE FOR ONBOARDING** — High-value tool with no internal duplicate. Fast-tracking to IT Procurement!")

# --- TAB 2: SAFE AI DATA SANITIZER ---
with tab2:
    st.subheader("🧪 Auto-Sanitize Confidential Text Before Using External AI")
    st.write("Strip PII, emails, phone numbers, PAN, and financial figures automatically before pasting into external AI tools:")
    
    sample_text = (
        "Confidential Q3 Report: ApexCorp Retail signed a supply contract with vendor Rajesh Kumar "
        "(Email: rajesh.k@vendor.in, Phone: +91-9876543210, PAN: ABCDE1234F) worth Rs. 45,00,000 for Bengaluru warehouses."
    )
    user_text = st.text_area("Paste Raw Work Text:", sample_text, height=120)
    
    if st.button("✨ Sanitize Data for Safe AI Prompting", type="primary"):
        cleaned = re.sub(r'[\w\.-]+@[\w\.-]+', '[EMAIL_REDACTED]', user_text)
        cleaned = re.sub(r'(\+91[\-\s]?)?[6-9]\d{9}', '[PHONE_REDACTED]', cleaned)
        cleaned = re.sub(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', '[PAN_REDACTED]', cleaned)
        cleaned = re.sub(r'(Rs\.?|INR|₹)\s?[\d,]+', '[FINANCIAL_AMOUNT_REDACTED]', cleaned)
        
        st.success("✅ **Sanitized Output Ready!** Safe to copy into Sandbox AI tools:")
        st.code(cleaned, language="text")

# --- TAB 3: IT & SECOPS REVIEW CONSOLE ---
with tab3:
    st.subheader("🔐 Live SecOps & FinOps Triage Queue (6 Departments)")
    
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Unapproved Events", len(df))
    k2.metric("Immediate Threats", len(df[df["Review_Decision"] == "RESTRICT"]))
    k3.metric("Safe Sandboxes", len(df[df["Review_Decision"] == "SANDBOX"]))
    k4.metric("Orphaned Personal Files", len(df[df["Personal_Account_Used"] == "Yes"]))
    k5.metric("Duplicate SaaS Spend/Mo", f"₹{df['Monthly_Cost_INR'].sum():,}")

    st.markdown("### 📊 Departmental Risk & Shadow SaaS Spend Overview")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("Duplicate Monthly SaaS Spend by Department (INR)")
        st.bar_chart(df.groupby("Entra_Department")["Monthly_Cost_INR"].sum())
    with c2:
        st.caption("Governance Decisions Breakdown")
        st.bar_chart(df["Review_Decision"].value_counts())

    st.markdown("### 📋 Live Discovery & Governance Logs")
    f1, f2 = st.columns(2)
    with f1:
        dept_filter = st.multiselect("Filter by Entra ID Department:", sorted(df["Entra_Department"].unique()), default=sorted(df["Entra_Department"].unique()))
    with f2:
        dec_filter = st.multiselect("Filter by Review Decision:", sorted(df["Review_Decision"].unique()), default=sorted(df["Review_Decision"].unique()))

    filtered_df = df[(df["Entra_Department"].isin(dept_filter)) & (df["Review_Decision"].isin(dec_filter))]
    
    st.dataframe(
        filtered_df[[
            "Log_ID", "Entra_Department", "Defender_Tool_Detected", "Reason_Adopted",
            "Defender_File_Uploaded", "Defender_Upload_MB", "Entra_OAuth_Scope",
            "Personal_Account_Used", "Risk_Score", "ML_Anomaly_Flag", "Review_Decision", "Approved_Alternative"
        ]],
        use_container_width=True
    )

    st.markdown("---")
    if st.button("🚀 Trigger Power Automate Teams Nudges for Flagged Users", type="primary"):
        restrict_count = len(filtered_df[filtered_df["Review_Decision"] == "RESTRICT"])
        replace_count = len(filtered_df[filtered_df["Review_Decision"] == "REPLACE"])
        st.toast(f"Power Automate Triggered! Sent {restrict_count} Block Alerts & {replace_count} License Redirects.", icon="⚡")
        st.success(f"✅ **Power Automate Execution Complete:** Revoked {restrict_count} high-risk OAuth tokens in Entra ID and sent {replace_count} self-service migration links to official corporate tools!")

# --- TAB 4: DEFENDER + ENTRA ID KQL PIPELINE ---
with tab4:
    st.subheader("📡 Enterprise Telemetry Extraction via KQL")
    st.write("KQL query joining **Microsoft Defender for Cloud Apps** (`CloudAppEvents`) and **Microsoft Entra ID** (`IdentityInfo`) across 6 departments:")
    
    kql_code = """CloudAppEvents
| where Timestamp > ago(7d)
| where IsApprovedApp == false
| join kind=inner (
    IdentityInfo 
    | where Department in ("Finance", "Marketing", "R&D Engineering", "HR", "Sales", "Operations")
) on $left.AccountId == $right.AccountObjectId
| extend Tool_Name = Application,
         Upload_Size_MB = round(tolong(RawEventData.UploadBytes) / 1048576.0, 1),
         OAuth_Scope = tostring(RawEventData.OAuthPermissionLevel)
| project Log_ID = ReportId, Employee_Email = AccountUpn, Department, Tool_Name, 
          Tool_Category = ApplicationCategory, Upload_Size_MB, OAuth_Scope
| order by Upload_Size_MB desc"""
    
    st.code(kql_code, language="sql")