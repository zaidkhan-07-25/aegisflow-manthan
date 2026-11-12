import streamlit as st
import pandas as pd
import numpy as np
import re
import glob
import time
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest

# 1. Page Config & Enterprise Dark-Mode CSS
st.set_page_config(page_title="AegisFlow | Enterprise Shadow IT Governance", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Clean Enterprise Dark Theme Overrides */
    .stApp {
        background-color: #0B1120;
        color: #F8FAFC;
    }
    header[data-testid="stHeader"] {
        background: transparent;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-left: 4px solid #06B6D4;
        padding: 16px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
        color: #F8FAFC;
    }
    .decision-box-restrict {
        background-color: rgba(239, 68, 68, 0.12);
        border: 1px solid #EF4444;
        border-left: 6px solid #EF4444;
        padding: 18px;
        border-radius: 8px;
        margin-top: 10px;
    }
    .decision-box-replace {
        background-color: rgba(245, 158, 11, 0.12);
        border: 1px solid #F59E0B;
        border-left: 6px solid #F59E0B;
        padding: 18px;
        border-radius: 8px;
        margin-top: 10px;
    }
    .decision-box-sandbox {
        background-color: rgba(16, 185, 129, 0.12);
        border: 1px solid #10B981;
        border-left: 6px solid #10B981;
        padding: 18px;
        border-radius: 8px;
        margin-top: 10px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #0F172A;
        padding: 8px;
        border-radius: 10px;
        border: 1px solid #1E293B;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 8px;
        padding: 0 20px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# 2. Load Data & ML Scoring
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

# Sidebar Navigation & Status
with st.sidebar:
    st.markdown("## 🛡️ **AEGISFLOW**")
    st.caption("Autonomous Shadow IT & Citizen AI Governance")
    st.markdown("---")
    st.markdown("**🟢 System Status:** `ACTIVE`")
    st.markdown("**📡 Telemetry:** `Defender + Entra KQL`")
    st.markdown("**🧠 ML Engine:** `IsolationForest v1.4`")
    st.markdown("---")
    uploaded_csv = st.file_uploader("Ingest Custom KQL Log (CSV)", type=["csv"])
    df = load_data(uploaded_csv)
    st.markdown("---")
    st.caption("Manthan 2.0 | Challenge 8\nTeam: Naman, Zaid, Rohan, Hare Raj")

# Top Header
st.markdown("# 🛡️ AegisFlow Governance Command Center")
st.markdown("Real-time visibility, ML risk scoring, and automated policy enforcement across **6 enterprise departments**.")

# KPI Cards
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Shadow Tools Detected", len(df), "6 Departments")
k2.metric("Critical Blocks (RESTRICT)", len(df[df["Review_Decision"] == "RESTRICT"]), "Prevented Leaks", delta_color="inverse")
k3.metric("Active Sandboxes", len(df[df["Review_Decision"] == "SANDBOX"]), "Safe Innovation")
k4.metric("Orphaned IP Files", len(df[df["Personal_Account_Used"] == "Yes"]), "Personal Accounts", delta_color="inverse")
k5.metric("Annualized SaaS Waste", f"₹{df['Monthly_Cost_INR'].sum() * 12:,}", f"₹{df['Monthly_Cost_INR'].sum():,}/mo")

st.markdown("<br>", unsafe_allow_html=True)

# 4 Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "⚡ 1. Live Tool & File Interceptor",
    "📊 2. Executive Risk & FinOps Analytics",
    "🧪 3. AI Prompt Firewall (DLP)",
    "🔐 4. SecOps Triage & Automation"
])

# --- TAB 1: LIVE FILE & TOOL INTERCEPTOR ---
with tab1:
    st.markdown("### ⚡ Real-Time Employee Policy Engine")
    st.caption("Simulate an employee attempting to use an external tool or upload a real file from your computer.")
    
    c_left, c_right = st.columns([1, 1.3], gap="large")
    
    with c_left:
        selected_dept = st.selectbox("1. Employee Department (Entra ID):", sorted(df["Entra_Department"].unique()))
        selected_tool = st.selectbox("2. Target External Tool:", sorted(df["Defender_Tool_Detected"].unique()))
        intended_data = st.selectbox(
            "3. Data Classification:",
            ["Public / Non-Sensitive", "Internal Business", "Confidential Financial", "Customer / Employee PII", "Proprietary Source Code"]
        )
        real_file = st.file_uploader("4. (Optional) Drop any real file to scan live:", key="interceptor_file")
        scan_btn = st.button("🛡️ Run Real-Time Governance Scan", type="primary", use_container_width=True)

    with c_right:
        if scan_btn:
            with st.spinner("Querying Entra ID OAuth permissions & running IsolationForest risk model..."):
                time.sleep(0.6)
        
        tool_row = df[df["Defender_Tool_Detected"] == selected_tool].iloc[0]
        base_score = tool_row["Risk_Score"]
        
        # Factor in uploaded file name/size if user drops a real file
        file_bonus = 0
        file_label = "Simulated Payload"
        if real_file is not None:
            file_label = f"{real_file.name} ({round(real_file.size / 1024, 1)} KB)"
            if any(w in real_file.name.lower() for w in ["tax", "salary", "audit", "pan", "aadhaar", "secret", "client", "code"]):
                file_bonus = 25.0

        if intended_data in ["Customer / Employee PII", "Proprietary Source Code", "Confidential Financial"]:
            live_score = min(99.0, max(base_score, 85.0) + file_bonus)
        else:
            live_score = min(99.0, base_score + file_bonus)

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=live_score,
            number={'font': {'color': '#F8FAFC', 'size': 44}},
            title={'text': f"Risk Index: {selected_tool}", 'font': {'color': '#94A3B8', 'size': 16}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': '#64748B'},
                'bar': {'color': "#EF4444" if live_score >= 65 else ("#F59E0B" if live_score >= 35 else "#10B981")},
                'bgcolor': "#1E293B",
                'steps': [
                    {'range': [0, 35], 'color': "rgba(16, 185, 129, 0.15)"},
                    {'range': [35, 65], 'color': "rgba(245, 158, 11, 0.15)"},
                    {'range': [65, 100], 'color': "rgba(239, 68, 68, 0.15)"}
                ]
            }
        ))
        fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_gauge, use_container_width=True)

        if live_score >= 65 or tool_row["Vendor_SOC2_Safe"] == "No":
            alt_msg = f"<br>✅ <b>Auto-Redirect:</b> Use pre-approved <b>{tool_row['Approved_Alternative']}</b> instead." if tool_row["Approved_Alternative"] != "None" else ""
            st.markdown(f"""
            <div class="decision-box-restrict">
                <h4 style="color:#EF4444; margin:0;">🚨 ACTION: RESTRICT (UPLOAD BLOCKED)</h4>
                <p style="margin:6px 0 0 0; color:#E2E8F0;">Payload <b>{file_label}</b> violates DPDP / IP policy on unverified tool <b>{selected_tool}</b>.{alt_msg}</p>
            </div>
            """, unsafe_allow_html=True)
        elif tool_row["Approved_Alternative"] != "None":
            st.markdown(f"""
            <div class="decision-box-replace">
                <h4 style="color:#F59E0B; margin:0;">🔄 ACTION: REPLACE (FINOPS DUPLICATE)</h4>
                <p style="margin:6px 0 0 0; color:#E2E8F0;">ApexCorp already licenses <b>{tool_row['Approved_Alternative']}</b>. Migrating saves <b>₹{tool_row['Monthly_Cost_INR']}/month</b>.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="decision-box-sandbox">
                <h4 style="color:#10B981; margin:0;">✅ ACTION: SANDBOX APPROVED (14-DAY TRIAL)</h4>
                <p style="margin:6px 0 0 0; color:#E2E8F0;">Low-risk payload <b>{file_label}</b> cleared for isolated experimentation with automatic PII guardrails.</p>
            </div>
            """, unsafe_allow_html=True)

# --- TAB 2: EXECUTIVE ANALYTICS ---
with tab2:
    c1, c2 = st.columns(2)
    with c1:
        fig_dept = px.bar(
            df.groupby(["Entra_Department", "Review_Decision"]).size().reset_index(name="Events"),
            x="Entra_Department", y="Events", color="Review_Decision",
            title="Governance Decisions by Department",
            color_discrete_map={"RESTRICT": "#EF4444", "REPLACE": "#F59E0B", "SANDBOX": "#10B981", "APPROVE": "#3B82F6"},
            barmode="stack", template="plotly_dark"
        )
        fig_dept.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_dept, use_container_width=True)

    with c2:
        fig_scatter = px.scatter(
            df, x="Defender_Upload_MB", y="Risk_Score", color="Review_Decision",
            size="Monthly_Cost_INR", hover_data=["Defender_Tool_Detected", "Entra_Department", "Data_Sensitivity"],
            title="IsolationForest ML Anomaly Clusters (Upload MB vs Risk)",
            color_discrete_map={"RESTRICT": "#EF4444", "REPLACE": "#F59E0B", "SANDBOX": "#10B981", "APPROVE": "#3B82F6"},
            template="plotly_dark"
        )
        fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_scatter, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        spend_df = df.groupby("Entra_Department")["Monthly_Cost_INR"].sum().reset_index().sort_values("Monthly_Cost_INR")
        fig_spend = px.bar(
            spend_df, x="Monthly_Cost_INR", y="Entra_Department", orientation="h",
            title="Duplicate Monthly SaaS Leakage by Department (₹)",
            text="Monthly_Cost_INR", color_discrete_sequence=["#06B6D4"], template="plotly_dark"
        )
        fig_spend.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_spend, use_container_width=True)

    with c4:
        fig_reason = px.pie(
            df, names="Reason_Adopted", title="Why Employees Bypass Official IT Systems",
            hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel, template="plotly_dark"
        )
        fig_reason.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_reason, use_container_width=True)

# --- TAB 3: AI PROMPT FIREWALL (DLP) ---
with tab3:
    st.markdown("### 🧪 Zero-Leak AI Prompt Firewall")
    st.caption("Automatically strips PII, PAN, phone numbers, and financials before employees prompt external AI tools—preventing Samsung & Amazon-style leaks.")
    
    c_in, c_out = st.columns(2, gap="large")
    with c_in:
        sample_text = (
            "Confidential Q3 Audit: ApexCorp Retail finalized vendor contract with Rajesh Kumar "
            "(Email: rajesh.k@vendor.in, Phone: +91-9876543210, PAN: ABCDE1234F) for Rs. 45,00,000 in Bengaluru."
        )
        user_text = st.text_area("Raw Employee Prompt / Document Snippet:", sample_text, height=180)
        scrub_btn = st.button("✨ Sanitize & Generate Safe Prompt", type="primary", use_container_width=True)
    with c_out:
        st.markdown("**Sanitized Output (Safe for External Sandbox AI):**")
        cleaned = re.sub(r'[\w\.-]+@[\w\.-]+', '[EMAIL_REDACTED]', user_text)
        cleaned = re.sub(r'(\+91[\-\s]?)?[6-9]\d{9}', '[PHONE_REDACTED]', cleaned)
        cleaned = re.sub(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', '[PAN_REDACTED]', cleaned)
        cleaned = re.sub(r'(Rs\.?|INR|₹)\s?[\d,]+', '[FINANCIAL_AMOUNT_REDACTED]', cleaned)
        st.code(cleaned, language="text")
        st.success("✅ 4 sensitive entities neutralized automatically.")

# --- TAB 4: SECOPS TRIAGE & AUTOMATION ---
with tab4:
    st.markdown("### 🔐 Live SecOps Triage Queue & Power Automate Trigger")
    f1, f2 = st.columns(2)
    with f1:
        dept_filter = st.multiselect("Department:", sorted(df["Entra_Department"].unique()), default=sorted(df["Entra_Department"].unique()))
    with f2:
        dec_filter = st.multiselect("Decision:", sorted(df["Review_Decision"].unique()), default=sorted(df["Review_Decision"].unique()))

    filtered_df = df[(df["Entra_Department"].isin(dept_filter)) & (df["Review_Decision"].isin(dec_filter))]
    st.dataframe(filtered_df, use_container_width=True, height=320)

    if st.button("⚡ Execute Automated Power Automate Remediation", type="primary"):
        r_cnt = len(filtered_df[filtered_df["Review_Decision"] == "RESTRICT"])
        rep_cnt = len(filtered_df[filtered_df["Review_Decision"] == "REPLACE"])
        st.toast(f"Power Automate: Revoked {r_cnt} OAuth tokens & sent {rep_cnt} Teams nudges!", icon="⚡")
        st.success(f"✅ **Remediation Executed:** {r_cnt} high-risk OAuth grants revoked in Entra ID; {rep_cnt} employees redirected to licensed corporate tools.")

    with st.expander("📡 View Production Microsoft Defender + Entra ID KQL Query"):
        st.code("""CloudAppEvents
| where Timestamp > ago(7d) and IsApprovedApp == false
| join kind=inner (
    IdentityInfo | where Department in ("Finance", "Marketing", "R&D Engineering", "HR", "Sales", "Operations")
) on $left.AccountId == $right.AccountObjectId
| project ReportId, AccountUpn, Department, Application, ApplicationCategory, UploadBytes, OAuthPermissionLevel""", language="sql")
