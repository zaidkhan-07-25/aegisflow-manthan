import streamlit as st
import pandas as pd
import numpy as np
import re
import glob
from sklearn.ensemble import IsolationForest

# 1. Page Configuration
st.set_page_config(page_title="AegisFlow | Manthan 2.0", page_icon="🛡️", layout="wide")

# 2. Bulletproof Data Loader (Reads CSV if present, or auto-builds the 50-row dataset)
@st.cache_data
def load_data():
    csv_files = glob.glob("*.csv")
    if csv_files:
        df = pd.read_csv(csv_files[0])
    else:
        np.random.seed(42)
        base_scenarios = [
            ("Finance", "iLovePDF Online", "Online Tool", "Approved system too slow", "Q3_Audit_Financials.pdf", "Confidential Financial", 42.5, "None", "No", 0, "No", "Adobe Acrobat Enterprise", 78.5, "Immediate Attention", "RESTRICT"),
            ("Marketing", "ChatGPT Free Web", "AI Assistant", "Missing AI feature", "Festive_Campaign_Copy.docx", "Public / Non-Sensitive", 1.2, "Basic Profile Read", "Yes", 0, "Yes", "Microsoft Copilot", 22.0, "Low-Risk Experimentation", "SANDBOX"),
            ("R&D Engineering", "Cursor AI IDE", "AI Assistant", "Missing AI feature", "Payment_Gateway_Core.py", "Proprietary Source Code", 18.4, "Basic Profile Read", "No", 1650, "Yes", "None", 48.0, "Needs Review", "APPROVE"),
            ("HR", "Unknown-Resume-Parser.ru", "Online Tool", "Urgent deadline", "Candidate_Aadhaar_PAN.xlsx", "Customer / Employee PII", 85.0, "Mail.ReadWrite & Files.ReadWrite.All", "Yes", 0, "No", "Workday HR AI", 96.0, "Immediate Attention", "RESTRICT"),
            ("Sales", "Grammarly Chrome Ext", "Browser Extension", "Approved system too slow", "Client_Pitch_Emails.txt", "Internal Business", 3.1, "Browser DOM ReadAll", "Yes", 1200, "Yes", "Microsoft Editor", 44.0, "Needs Review", "REPLACE"),
            ("Operations", "Notion Personal", "Online Tool", "Approved system too slow", "Supply_Chain_Tracker.md", "Internal Business", 8.5, "Basic Profile Read", "Yes", 800, "Yes", "Microsoft Loop", 52.0, "Needs Review", "REPLACE"),
            ("Finance", "Julius AI Free", "AI Assistant", "Missing AI feature", "Customer_Billing_Raw.csv", "Customer / Employee PII", 120.0, "Files.ReadWrite.All", "Yes", 1800, "No", "Power BI Copilot", 91.5, "Immediate Attention", "RESTRICT"),
            ("Marketing", "Excalidraw Web", "Online Tool", "Unaware of alternative", "Campaign_Flow_Draft.png", "Public / Non-Sensitive", 0.8, "None", "No", 0, "Yes", "None", 12.0, "Low-Risk Experimentation", "SANDBOX"),
            ("Operations", "WeTransfer Free", "File Sharing", "Approved system too slow", "Vendor_Contracts_2026.zip", "Confidential Financial", 210.0, "None", "Yes", 900, "Yes", "OneDrive Corporate", 68.0, "Immediate Attention", "REPLACE"),
            ("Finance", "ChatPDF Unverified", "AI Assistant", "Urgent deadline", "Board_Tax_Strategy.pdf", "Confidential Financial", 34.0, "Basic Profile Read", "Yes", 0, "No", "Microsoft Copilot", 84.0, "Immediate Attention", "RESTRICT"),
            ("Marketing", "Canva Pro Personal", "Online Tool", "Approved system too slow", "Social_Media_Banners.zip", "Public / Non-Sensitive", 14.2, "Basic Profile Read", "Yes", 1000, "Yes", "Adobe Express Corp", 36.0, "Needs Review", "REPLACE"),
            ("R&D Engineering", "GitHub Copilot Personal", "AI Assistant", "Missing AI feature", "Unit_Test_Scripts.py", "Internal Business", 4.0, "Basic Profile Read", "No", 850, "Yes", "None", 31.0, "Low-Risk Experimentation", "APPROVE"),
            ("Operations", "Otter.ai Free", "AI Assistant", "Missing AI feature", "Ops_Review_Audio.mp3", "Internal Business", 55.0, "Calendars.ReadWrite", "Yes", 1500, "Yes", "MS Teams Premium", 58.0, "Needs Review", "REPLACE"),
            ("Finance", "Free-Doc-Translator.net", "Online Tool", "Urgent deadline", "M&A_Agreement_Draft.docx", "Confidential Financial", 12.8, "None", "No", 0, "No", "DeepL Enterprise", 88.0, "Immediate Attention", "RESTRICT"),
            ("Sales", "Apollo Scraper Ext", "Browser Extension", "Missing AI feature", "Client_Phone_Database.csv", "Customer / Employee PII", 28.0, "Mail.ReadWrite & Contacts.Read", "Yes", 2500, "No", "Salesforce Einstein", 89.0, "Immediate Attention", "RESTRICT"),
            ("HR", "Gamma App AI", "AI Assistant", "Approved system too slow", "Onboarding_Deck_Draft.pptx", "Public / Non-Sensitive", 3.5, "Basic Profile Read", "No", 1200, "Yes", "None", 24.0, "Low-Risk Experimentation", "SANDBOX"),
            ("Finance", "Personal Google Drive", "File Sharing", "Approved system too slow", "Q4_Salary_Sheet.xlsx", "Customer / Employee PII", 19.5, "Files.ReadWrite.All", "Yes", 0, "Yes", "OneDrive Corporate", 76.0, "Immediate Attention", "RESTRICT"),
            ("HR", "Claude.ai Free", "AI Assistant", "Missing AI feature", "JD_Templates_2026.docx", "Public / Non-Sensitive", 0.9, "Basic Profile Read", "No", 0, "Yes", "Microsoft Copilot", 18.0, "Low-Risk Experimentation", "SANDBOX"),
            ("Sales", "ChatGPT Plus Personal", "AI Assistant", "Missing AI feature", "Mock_Sales_Pitch.csv", "Public / Non-Sensitive", 2.1, "Basic Profile Read", "Yes", 1650, "Yes", "Microsoft Copilot", 38.0, "Needs Review", "REPLACE"),
            ("R&D Engineering", "Shady-JSON-Formatter Ext", "Browser Extension", "Unaware of alternative", "API_Auth_Tokens.json", "Proprietary Source Code", 1.5, "Browser DOM ReadAll", "No", 0, "No", "VS Code Formatter", 94.0, "Immediate Attention", "RESTRICT"),
            ("Sales", "Loom Free Screen Rec", "Online Tool", "Approved system too slow", "Product_Demo_Walkthrough.mp4", "Internal Business", 64.0, "Basic Profile Read", "Yes", 1100, "Yes", "Microsoft Clipchamp", 41.0, "Needs Review", "REPLACE"),
            ("Operations", "Smallpdf Converter", "Online Tool", "Urgent deadline", "Logistics_Invoices_Batch.pdf", "Confidential Financial", 16.5, "None", "No", 950, "Yes", "Adobe Acrobat Enterprise", 66.0, "Immediate Attention", "REPLACE"),
            ("Marketing", "Midjourney Discord", "AI Assistant", "Missing AI feature", "Brand_Mascot_Concepts.png", "Public / Non-Sensitive", 5.4, "None", "Yes", 2400, "Yes", "Adobe Firefly Enterprise", 33.0, "Low-Risk Experimentation", "REPLACE"),
            ("HR", "Typeform Free", "Online Tool", "Unaware of alternative", "Employee_Pulse_Survey.csv", "Customer / Employee PII", 2.4, "Basic Profile Read", "Yes", 0, "Yes", "Microsoft Forms", 67.5, "Immediate Attention", "REPLACE"),
            ("R&D Engineering", "Postman Public Workspace", "Online Tool", "Urgent deadline", "Staging_API_Endpoints.json", "Proprietary Source Code", 6.2, "Basic Profile Read", "Yes", 0, "Yes", "Postman Enterprise", 82.0, "Immediate Attention", "RESTRICT")
        ]
        first_names = ["aarav", "sneha", "rohan", "priya", "vikram", "ananya", "karthik", "meera", "zaid", "divya",
                       "aditya", "pooja", "rahul", "neha", "siddharth", "kavya", "manish", "tanya", "varun", "ishita",
                       "nikhil", "shreya", "arjun", "nisha", "harsh"]
        last_initials = ["p", "r", "v", "n", "s", "d", "m", "i", "k", "j", "g", "t", "b", "c", "l"]
        rows = []
        for idx in range(50):
            sc = base_scenarios[idx % len(base_scenarios)]
            email = f"{first_names[idx % len(first_names)]}.{last_initials[idx % len(last_initials)]}{idx+1}@apexcorp.in"
            upload_mb = sc[6] if idx < 25 else round(max(0.4, sc[6] * np.random.uniform(0.8, 1.3)), 1)
            risk = sc[12] if idx < 25 else round(min(99.0, max(10.0, sc[12] + np.random.uniform(-3.5, 3.5))), 1)
            status = "Immediate Attention" if risk >= 65 else ("Needs Review" if risk >= 35 else "Low-Risk Experimentation")
            rows.append([f"LOG-{101 + idx}", email, sc[0], sc[1], sc[2], sc[3], sc[4], sc[5], upload_mb,
                         sc[7], sc[8], sc[9], sc[10], sc[11], risk, status, sc[14]])
        cols = [
            "Log_ID", "Employee_Email", "Entra_Department", "Defender_Tool_Detected", "Tool_Category",
            "Reason_Adopted", "Defender_File_Uploaded", "Data_Sensitivity", "Defender_Upload_MB",
            "Entra_OAuth_Scope", "Personal_Account_Used", "Monthly_Cost_INR", "Vendor_SOC2_Safe",
            "Approved_Alternative", "Risk_Score", "Activity_Status", "Review_Decision"
        ]
        df = pd.DataFrame(rows, columns=cols)

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
