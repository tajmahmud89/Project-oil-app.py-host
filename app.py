import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from supabase import create_client

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="OIL SIF-Precursor Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CONFIGURATION ----------------
SUPABASE_URL = "https://rmbpxtqzxxjcbapuzmxz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtYnB4dHF6eHhqY2JhcHV6bXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgzNjQ5NDMsImV4cCI6MjEwMzk0MDk0M30.ZUvIgfMbz9nf6iJ4v7Uk-vbvy1fvaNxr0vRrhqclJlU"
N8N_WEBHOOK_URL = "https://project-oil-app-py-host.onrender.com"

# ---------------- SPREADSHEET PARSING FUNCTION ----------------
def extract_text_from_spreadsheet(uploaded_file, file_ext):
    """Parses uploaded CSV or XLSX spreadsheet files into concatenated text records."""
    if file_ext == "csv":
        df_file = pd.read_csv(uploaded_file)
    else:
        df_file = pd.read_excel(uploaded_file)
    
    extracted_text = []
    for index, row in df_file.iterrows():
        extracted_text.append(f"Observation {index+1}: " + " | ".join(row.astype(str).tolist()))
    
    return "\n--- [NEXT RECORD] ---\n".join(extracted_text)

# ---------------- GLASSMORPHIC THEME INJECTION ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Background Setup */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(15, 23, 42, 1) 0%, rgba(10, 15, 29, 1) 90.2%);
        color: #f1f5f9;
    }

    /* Sidebar Glassmorphic Styling */
    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.75) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* Glass Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.55);
        backdrop-filter: blur(12px) saturate(160%);
        -webkit-backdrop-filter: blur(12px) saturate(160%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(56, 189, 248, 0.3);
        transform: translateY(-2px);
    }

    /* KPI Value Display */
    .metric-title {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-value {
        color: #f8fafc;
        font-size: 1.85rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .metric-badge {
        display: inline-block;
        font-size: 0.75rem;
        padding: 2px 8px;
        border-radius: 9999px;
        font-weight: 600;
        margin-top: 4px;
    }
    .badge-red {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .badge-blue {
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }

    /* Primary Interactive Buttons */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 20px rgba(2, 132, 199, 0.35) !important;
        transition: all 0.2s ease !important;
    }
    
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important;
        box-shadow: 0 6px 24px rgba(2, 132, 199, 0.5) !important;
        transform: translateY(-1px) !important;
    }

    /* Input Field Styling */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div, div[data-testid="stFileUploader"] {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        color: #f8fafc !important;
    }

    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 1px #38bdf8 !important;
    }

    /* Tables & Dataframes */
    [data-testid="stDataFrame"] {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Supabase Client
@st.cache_resource
def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

# ---------------- HEADER ----------------
st.markdown("""
<div style="padding: 12px 0 24px 0;">
    <h1 style="font-size: 2.2rem; font-weight: 700; color: #f8fafc; margin-bottom: 6px;">
        🛡️ Oil India Limited — SIF Precursor Intelligence Engine
    </h1>
    <p style="font-size: 1rem; color: #94a3b8; margin: 0;">
        Automated AI Triage, IOGP Life-Saving Rules Auto-Mapping, and Operational Risk Density Analytics
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR: INGESTION FORM ----------------
with st.sidebar:
    st.markdown("### 📝 Submit Observation")
    st.caption("Ingest unstructured near-miss or unsafe condition narratives directly from field operations.")
    
    loc = st.selectbox("Location / Operating Rig", [
        "Duliajan Central Workshop",
        "Moran Rig #04",
        "Baghewala Heavy Oil Wellhead",
        "Pipeline Pump Station #03",
        "Kumchai Drilling Site",
        "Digboi Production Field"
    ])
    
    act = st.selectbox("Operational Activity", [
        "High-Pressure Line Depressurization",
        "Crane & Heavy Mechanical Lifting",
        "Hot Work & Cutting Operations",
        "Confined Space Mud Tank Cleaning",
        "Derrick Mast Maintenance",
        "Routine Facility Housekeeping"
    ])
    
    st.markdown("### 📁 Bulk Spreadsheet Ingestion")
    uploaded_file = st.file_uploader("Upload CSV or XLSX Reports", type=["csv", "xlsx"])
    
    st.markdown("**OR**")
    
    text = st.text_area("Observation / Incident Narrative", height=140, placeholder="Describe what happened, any high-energy equipment involved, and safeguards present...")
    
    submit_btn = st.button("🚀 Ingest & Triage via AI Pipeline", use_container_width=True)
    
    if submit_btn:
        final_text_payload = ""
        
        # 1. Process Uploaded File
        if uploaded_file is not None:
            file_ext = uploaded_file.name.split(".")[-1].lower()
            with st.spinner(f"Extracting records from {file_ext.upper()} file..."):
                try:
                    final_text_payload = extract_text_from_spreadsheet(uploaded_file, file_ext)
                except Exception as ex:
                    st.error(f"Error reading spreadsheet: {ex}")
        
        # 2. Fallback to Manual Text Box
        elif text.strip():
            final_text_payload = text.strip()
            
        # 3. Dispatch Payload
        if final_text_payload:
            payload = {
                "report_id": f"OIL-WEB-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}",
                "location": loc,
                "activity": act,
                "report_text": final_text_payload,
                "is_batch": uploaded_file is not None
            }
            with st.spinner("Dispatching payload through n8n workflow engine..."):
                try:
                    res = requests.post(N8N_WEBHOOK_URL.strip(), json=payload, timeout=20)
                    if res.status_code == 200:
                        st.success("✅ AI Triage Successful: Telemetry parsed, SIF risk mapped to IOGP Rules, committed to secure database, and real-time alerts routed via n8n.")
                    else:
                        st.error(f"Execution Error ({res.status_code}): {res.text}")
                except Exception as e:
                    st.error(f"Could not connect to n8n Webhook: {e}")
        else:
            st.warning("Please upload a CSV/XLSX file or enter narrative text before submitting.")

# ---------------- MAIN DASHBOARD & ANALYTICS ----------------
try:
    response = supabase.table("oil_safety_logs").select("*").execute()
    data = response.data
    df = pd.DataFrame(data)
except Exception as e:
    df = pd.DataFrame()
    st.error(f"Database Fetch Error: {e}")

if not df.empty:
    total_logs = len(df)
    sif_df = df[df["is_sif_potential"] == True] if "is_sif_potential" in df.columns else pd.DataFrame()
    sif_count = len(sif_df)
    sif_rate = (sif_count / total_logs) * 100 if total_logs > 0 else 0.0

    # Top KPI Metrics Cards (Glassmorphic Container)
    kpi1, kpi2, kpi3 = st.columns(3)
    
    with kpi1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">Total Ingested Reports</div>
            <div class="metric-value">{total_logs:,}</div>
            <div class="metric-badge badge-blue">Telemetry Active</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi2:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">Identified SIF Precursors</div>
            <div class="metric-value" style="color: #f87171;">{sif_count:,}</div>
            <div class="metric-badge badge-red">Critical High-Energy</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">SIF Precursor Density</div>
            <div class="metric-value">{sif_rate:.1f}%</div>
            <div class="metric-badge badge-red">Precursor Ratio</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # Visual Analytics Row
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("📍 SIF Precursor Density by Asset")
        if not sif_df.empty and "location" in sif_df.columns:
            density = sif_df["location"].value_counts().reset_index()
            density.columns = ["Location", "SIF Precursor Count"]
            
            fig_bar = px.bar(
                density,
                x="Location",
                y="SIF Precursor Count",
                color="SIF Precursor Count",
                color_continuous_scale=["#f87171", "#ef4444", "#b91c1c"],
                text="SIF Precursor Count"
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Asset Location"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Fatal Precursors"),
                coloraxis_showscale=False,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            fig_bar.update_traces(textposition='outside', marker_line_color='rgba(255,255,255,0.15)', marker_line_width=1)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No SIF Precursors identified in current logs.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("⚠️ Top Violated IOGP Rules")
        if not sif_df.empty and "iogp_rules" in sif_df.columns:
            all_rules = [rule for rules_list in sif_df["iogp_rules"].dropna() if isinstance(rules_list, list) for rule in rules_list]
            if all_rules:
                rule_series = pd.Series(all_rules).value_counts().reset_index()
                rule_series.columns = ["IOGP Rule", "Violation Count"]
                fig_pie = px.pie(
                    rule_series,
                    names="IOGP Rule",
                    values="Violation Count",
                    hole=0.55,
                    color_discrete_sequence=["#ef4444", "#f97316", "#eab308", "#06b6d4", "#3b82f6"]
                )
                fig_pie.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
                    margin=dict(l=20, r=20, t=20, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                fig_pie.update_traces(marker=dict(line=dict(color='rgba(15, 23, 42, 0.8)', width=2)))
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No IOGP rules mapped yet.")
        else:
            st.info("No rules data available.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # High-Risk Precursor Incident Feed
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📋 Real-Time HSE Intelligence Feed")
    
    standard_cols = [
        "created_at", "location", "activity", "is_sif_potential",
        "iogp_rules", "energy_source", "barrier_status", "recommended_action"
    ]
    display_cols = [col for col in standard_cols if col in df.columns]
    
    sort_column = "created_at" if "created_at" in df.columns else df.columns[0]
    
    st.dataframe(
        df[display_cols].sort_values(by=sort_column, ascending=False),
        use_container_width=True,
        height=350
    )
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Database is currently empty. Use the sidebar form to submit test incident logs.")