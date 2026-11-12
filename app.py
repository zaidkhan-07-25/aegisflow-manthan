import streamlit as st
import pandas as pd
import numpy as np
import re
import glob
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest

# 1. Page Configuration
st.set_page_config(page_title="AegisFlow | Shadow IT Command Center", page_icon="🛡️", layout="wide")

# Custom Styling for Executive Cards & Badges
st.markdown("""
<style>
    .stMetric {
        background-color: #1E293B;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #06B6D4;
    }
</style>
""", unsafe_allow_html=True)

# 2. Load Data + ML Scoring
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
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

# Sidebar: Live Telemetry Ingestion & Simulation
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=64)
    st.title("AegisFlow Engine")
    st.caption("Manthan 2.0 | Challenge 8")
    st.markdown("---")
    uploaded_csv = st.file_uploader("📂 Upload Defender/Entra KQL CSV", type=["csv"])
    df = load_data(uploaded_csv)
    st.success(f"✅ {len(df)} Telemetry Logs Active")
    st.info("**Connected Sources:**\n- Microsoft Defender Cloud Apps\n- Microsoft Entra ID (6 Depts)\n- Scikit-learn IsolationForest")

# Header
st.title("🛡️ AegisFlow: Shadow IT & Citizen AI Command Center")
st.markdown("**Real-Time Risk Scoring, FinOps SaaS Recovery & Automated Governance Matrix**")

# Top Executive KPI Row
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Shadow Logs", len(df), "+12% vs last wk")
k2.metric("Critical Threats (RESTRICT)", len(df[df["Review_Decision"] == "RESTRICT"]), "Action Required", delta_color="inverse")
k3.metric("Safe Sandboxes", len(df[df["Review_Decision"] == "SANDBOX"]), "Zero Friction")
k4.metric("Orphaned Personal Files", len(df[df["Personal_Account_Used"] == "Yes"]), "Offboarding Risk", delta_color="inverse")
k5.metric("Wasted SaaS Spend / Yr", f"₹{df['Monthly_Cost_INR'].sum() * 12:,}", f"₹{df['Monthly_Cost_INR'].sum():,}/mo")

st.divider()

# 4 Interactive Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 1. Executive Analytics & Heatmap",
    "👩‍💻 2. Employee Tool Risk Gauge",
    "🧪 3. AI Data Sanitizer (DLP)",
    "🔐 4. SecOps Triage & KQL Pipeline"
])

# --- TAB 1: VISUAL ANALYTICS (PLOTLY) ---
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        fig_dept = px.bar(
            df.groupby(["Entra_Department", "Review_Decision"]).size().reset_index(name="Count"),
            x="Entra_Department", y="Count", color="Review_Decision",
            title="Shadow IT Governance Decisions by Department",
            color_discrete_map={"RESTRICT": "#EF4444", "REPLACE": "#F59E0B", "SANDBOX": "#10B981", "APPROVE": "#3B82F6"},
            barmode="stack"
        )
        st.plotly_chart(fig_dept, use_container_width=True)

    with c2:
        fig_scatter = px.scatter(
            df, x="Defender_Upload_MB", y="Risk_Score", color="Review_Decision",
            size="Monthly_Cost_INR", hover_data=["Defender_Tool_Detected", "Entra_Department", "Data_Sensitivity"],
            title="ML Risk Cluster: Upload Volume (MB) vs. Risk Score",
            color_discrete_map={"RESTRICT": "#EF4444", "REPLACE": "#F59E0B", "SANDBOX": "#10B981", "APPROVE": "#3B82F6"}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig_reason = px.pie(
            df, names="Reason_Adopted", title="Root Cause: Why Employees Bypassed Official Systems",
            hole=0.45, color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_reason, use_container_width=True)

    with c4:
        spend_df = df.groupby("Entra_Department")["Monthly_Cost_INR"].sum().reset_index().sort_values("Monthly_Cost_INR", ascending=True)
        fig_spend = px.bar(
            spend_df, x="Monthly_Cost_INR", y="Entra_Department", orientation="h",
            title="Duplicate Monthly SaaS Leakage by Department (INR)",
            text="Monthly_Cost_INR", color_discrete_sequence=["#06B6D4"]
        )
        st.plotly_chart(fig_spend, use_container_width=True)

# --- TAB 2: EMPLOYEE TOOL CHECKER WITH SPEEDOMETER GAUGE ---
with tab2:
    st.subheader("Interactive Tool Vetting & Self-Service Redirect")
    col1, col2 = st.columns([1, 1.3])
    
    with col1:
        selected_dept = st.selectbox("Your Entra ID Department:", sorted(df["Entra_Department"].unique()))
        selected_tool = st.selectbox("Select External Tool:", sorted(df["Defender_Tool_Detected"].unique()))
        intended_data = st.radio(
            "Data Sensitivity Level:",
            ["Public / Non-Sensitive", "Internal Business", "Confidential Financial", "Customer / Employee PII", "Proprietary Source Code"]
        )
        upload_est = st.slider("Estimated File Upload Size (MB):", 0.5, 250.0, 15.0)

    with col2:
        tool_row = df[df["Defender_Tool_Detected"] == selected_tool].iloc[0]
        base_score = tool_row["Risk_Score"]
        if intended_data in ["Customer / Employee PII", "Proprietary Source Code", "Confidential Financial"]:
            live_score = min(99.0, max(base_score, 85.0))
        else:
            live_score = base_score

        # Plotly Speedometer Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=live_score,
            title={'text': f"Live ML Risk Score: {selected_tool}"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#EF4444" if live_score >= 65 else ("#F59E0B" if live_score >= 35 else "#10B981")},
                'steps': [
                    {'range': [0, 35], 'color': "rgba(16, 185, 129, 0.2)"},
                    {'range': [35, 65], 'color': "rgba(245, 158, 11, 0.2)"},
                    {'range': [65, 100], 'color': "rgba(239, 68, 68, 0.2)"}
                ]
            }
        ))
        fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

        if live_score >= 65 or tool_row["Vendor_SOC2_Safe"] == "No":
            st.error("🚨 **DECISION: RESTRICT (Blocked)** — High risk of data leak or DPDP violation.")
            if tool_row["Approved_Alternative"] != "None":
                st.info(f"✅ **Approved Alternative:** Use **{tool_row['Approved_Alternative']}** instead.")
        elif tool_row["Approved_Alternative"] != "None":
            st.warning(f"🔄 **DECISION: REPLACE** — Switch to **{tool_row['Approved_Alternative']}** to save ₹{tool_row['Monthly_Cost_INR']}/mo.")
        elif live_score < 35:
            st.success("✅ **DECISION: SANDBOX APPROVED** — Safe for 14-day experimentation with non-sensitive data.")
        else:
            st.success("🌟 **DECISION: APPROVE** — High-value innovation tool routed to fast-track procurement.")

# --- TAB 3: SAFE AI DATA SANITIZER ---
with tab3:
    st.subheader("🧪 Real-Time Prompt & Document Sanitizer (Preventing Samsung/Amazon Leaks)")
    c_in, c_out = st.columns(2)
    with c_in:
        sample_text = (
            "Confidential Q3 Report: ApexCorp Retail signed a supply contract with vendor Rajesh Kumar "
            "(Email: rajesh.k@vendor.in, Phone: +91-9876543210, PAN: ABCDE1234F) worth Rs. 45,00,000 for Bengaluru warehouses."
        )
        user_text = st.text_area("1. Paste Raw Confidential Text:", sample_text, height=180)
        sanitize_btn = st.button("✨ Scrub PII & Financials Now", type="primary")
    with c_out:
        st.write("2. Safe Sanitized Output (Ready for Sandbox AI):")
        if sanitize_btn or user_text:
            cleaned = re.sub(r'[\w\.-]+@[\w\.-]+', '[EMAIL_REDACTED]', user_text)
            cleaned = re.sub(r'(\+91[\-\s]?)?[6-9]\d{9}', '[PHONE_REDACTED]', cleaned)
            cleaned = re.sub(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', '[PAN_REDACTED]', cleaned)
            cleaned = re.sub(r'(Rs\.?|INR|₹)\s?[\d,]+', '[FINANCIAL_AMOUNT_REDACTED]', cleaned)
            st.code(cleaned, language="text")

# --- TAB 4: SECOPS TRIAGE & KQL ---
with tab4:
    st.subheader("🔐 Live SecOps Triage Queue & Automated Remediation")
    f1, f2 = st.columns(2)
    with f1:
        dept_filter = st.multiselect("Filter Department:", sorted(df["Entra_Department"].unique()), default=sorted(df["Entra_Department"].unique()))
    with f2:
        dec_filter = st.multiselect("Filter Decision:", sorted(df["Review_Decision"].unique()), default=sorted(df["Review_Decision"].unique()))

    filtered_df = df[(df["Entra_Department"].isin(dept_filter)) & (df["Review_Decision"].isin(dec_filter))]
    st.dataframe(filtered_df, use_container_width=True)

    if st.button("⚡ Execute Power Automate Remediation (Revoke OAuth & Send Teams Nudges)", type="primary"):
        r_cnt = len(filtered_df[filtered_df["Review_Decision"] == "RESTRICT"])
        rep_cnt = len(filtered_df[filtered_df["Review_Decision"] == "REPLACE"])
        st.toast(f"Power Automate: Revoked {r_cnt} OAuth tokens & sent {rep_cnt} migration nudges!", icon="⚡")
        st.success(f"✅ Automated remediation dispatched for {r_cnt + rep_cnt} flagged events.")

    with st.expander("📡 View Underlying Microsoft Defender + Entra ID KQL Query"):
        st.code("""CloudAppEvents
| where Timestamp > ago(7d) and IsApprovedApp == false
| join kind=inner (
    IdentityInfo | where Department in ("Finance", "Marketing", "R&D Engineering", "HR", "Sales", "Operations")
) on $left.AccountId == $right.AccountObjectId
| project ReportId, AccountUpn, Department, Application, ApplicationCategory, UploadBytes, OAuthPermissionLevel""", language="sql")
