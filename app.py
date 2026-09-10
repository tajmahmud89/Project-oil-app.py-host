import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from supabase import create_client

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="OIL SIF-Precursor Intelligence",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CONFIGURATION ----------------
SUPABASE_URL = "https://rmbpxtqzxxjcbapuzmxz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtYnB4dHF6eHhqY2JhcHV6bXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgzNjQ5NDMsImV4cCI6MjEwMzk0MDk0M30.ZUvIgfMbz9nf6iJ4v7Uk-vbvy1fvaNxr0vRrhqclJlU"
N8N_WEBHOOK_URL = "https://thesilentvisualizer.app.n8n.cloud/webhook/submit-safety-log"

# ---------------- LIGHT CORPORATE THEME INJECTION (OIL INDIA BRANDING) ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #f8fafc !important;
    }

    /* Force Global Text Visibility */
    p, span, label, h1, h2, h3, h4, h5, h6, li, .stMarkdown, .stText {
        color: #0f172a !important;
    }

    /* Keep specific red accents */
    .title-highlight {
        color: #e31837 !important;
    }

    /* Sidebar Light Glass Styling */
    section[data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid rgba(226, 232, 240, 1) !important;
    }

    /* Light Glassmorphic Containers */
    .glass-card {
        background-color: #ffffff;
        border: 1px solid rgba(227, 24, 55, 0.15);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(227, 24, 55, 0.5); /* OIL Red Accent */
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(227, 24, 55, 0.08);
    }

    /* Custom KPI Typography */
    .metric-title {
        color: #64748b !important;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .metric-value {
        color: #0f172a !important;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    .metric-badge {
        display: inline-block;
        font-size: 0.75rem;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 700;
        margin-top: 10px;
    }
    
    /* Risk KPI Badge */
    .badge-red {
        background-color: rgba(227, 24, 55, 0.1);
        color: #e31837 !important; 
        border: 1px solid rgba(227, 24, 55, 0.3);
    }
    
    /* System Active KPI Badge (Green) */
    .badge-green {
        background-color: rgba(34, 197, 94, 0.1);
        color: #16a34a !important; 
        border: 1px solid rgba(34, 197, 94, 0.3);
    }

    /* Submit Button Styling (OIL Red Gradient) */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #e31837 0%, #b91c1c 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        box-shadow: 0 4px 15px rgba(227, 24, 55, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%) !important;
        box-shadow: 0 6px 20px rgba(227, 24, 55, 0.4) !important;
        transform: scale(1.02) !important;
    }
    
    /* Explicitly make the text of the button white */
    div.stButton > button:first-child * {
        color: #ffffff !important;
    }

    /* Input Fields - Forced Solid White Background & Dark Text */
    input, textarea, div[data-baseweb="select"] > div, div[data-baseweb="base-input"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        border: 1px solid rgba(148, 163, 184, 0.4) !important;
        border-radius: 8px !important;
    }
    
    input:focus, textarea:focus, div[data-baseweb="select"] > div:focus {
        border-color: #e31837 !important;
        box-shadow: 0 0 0 1px #e31837 !important;
    }

    /* Dataframe / Table Container - Forced Solid White Background */
    [data-testid="stDataFrame"], [data-testid="stDataFrame"] > div, [data-testid="stDataFrame"] canvas {
        background-color: #ffffff !important;
        border: 1px solid rgba(226, 232, 240, 1) !important;
        border-radius: 12px !important;
    }
    
    /* Table Text Visibility */
    .stDataFrame * {
        color: #0f172a !important;
    }

</style>
""", unsafe_allow_html=True)

# Initialize Supabase Client
@st.cache_resource
def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()
def extract_text_from_spreadsheet(uploaded_file, file_ext):
    if file_ext == "csv":
        df_file = pd.read_csv(uploaded_file)
    else:
        df_file = pd.read_excel(uploaded_file)
    
    extracted_text = []
    for index, row in df_file.iterrows():
        extracted_text.append(f"Observation {index+1}: " + " | ".join(row.astype(str).tolist()))
    
    return "\n--- [NEXT RECORD] ---\n".join(extracted_text)

# ---------------- HEADER ----------------
st.markdown("""
<div style="padding: 10px 0 30px 0; border-bottom: 1px solid rgba(227, 24, 55, 0.15); margin-bottom: 30px;">
    <h1 style="font-size: 2.4rem; font-weight: 800; margin-bottom: 4px; display: flex; align-items: center; gap: 10px;">
        <span class="title-highlight">Oil India Limited</span> | SIF Intelligence Engine
    </h1>
    <p style="font-size: 1.04rem; color: #64748b; margin: 0; font-weight: 500;">
        Real-Time Safety Triage, IOGP Rule Auto-Mapping, and Precursor Density Analytics
    </p>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR: INGESTION FORM ----------------
# ---------------- SIDEBAR: INGESTION FORM ----------------
with st.sidebar:
    st.markdown('<div style="font-size: 1.4rem; font-weight: 700; color: #000000; margin-bottom: 8px;">Submit Field Safety Observation</div>', unsafe_allow_html=True)
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
    
    # --- DYNAMIC BUTTON RENDERING ---
    if uploaded_file is not None:
        file_ext = uploaded_file.name.split(".")[-1].lower()
        if file_ext == "csv":
            submit_btn = st.button("🚀 Process CSV Report", use_container_width=True)
        else:
            submit_btn = st.button("🚀 Process Excel Report", use_container_width=True)
    else:
        submit_btn = st.button("🚀 Ingest Manual Narrative", use_container_width=True)
    
    # --- EXECUTION LOGIC ---
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
    df = pd.DataFrame(response.data)
except Exception as e:
    df = pd.DataFrame()
    st.error(f"Database Fetch Error: {e}")

if not df.empty:
    total_logs = len(df)
    sif_df = df[df["is_sif_potential"] == True] if "is_sif_potential" in df.columns else pd.DataFrame()
    sif_count = len(sif_df)
    sif_rate = (sif_count / total_logs) * 100 if total_logs > 0 else 0.0

    # Custom HTML Glass KPI Cards (Light Corporate Theme)
    kpi1, kpi2, kpi3 = st.columns(3)
    
    with kpi1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">Total Ingested Reports</div>
            <div class="metric-value">{total_logs:,}</div>
            <div class="metric-badge badge-green">System Active</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi2:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">Identified SIF Precursors</div>
            <div class="metric-value" style="color: #e31837;">{sif_count:,}</div>
            <div class="metric-badge badge-red">High-Energy Risk</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-title">SIF Precursor Density</div>
            <div class="metric-value">{sif_rate:.1f}%</div>
            <div class="metric-badge badge-red">Overall Ratio</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

    # Visual Analytics Row
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-size: 1.1rem; font-weight: 700; color: #0f172a; margin-bottom: 15px;'>📍 SIF Precursor Density by Asset / Location</h3>", unsafe_allow_html=True)
        
        if not sif_df.empty and "location" in sif_df.columns:
            density = sif_df["location"].value_counts().reset_index()
            density.columns = ["Location", "SIF Precursor Count"]
            
            # Identify max value for dynamic scaling
            max_count = density["SIF Precursor Count"].max()
            density = density.sort_values(by="SIF Precursor Count", ascending=True)
            
            fig_bar = px.bar(
                density,
                x="SIF Precursor Count",
                y="Location",
                color="SIF Precursor Count",
                color_continuous_scale=["#ffffff", "#e31837"], 
                text="SIF Precursor Count",
                orientation="h",
                range_color=[0, max_count] # Locks 0 to white and max to red
            )
            
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#0f172a", family="Plus Jakarta Sans"),
                xaxis=dict(
                    title="", 
                    showgrid=False, 
                    showline=False,
                    showticklabels=False,
                    range=[0, max_count * 1.15] # 15% padding prevents numbers from hitting the boundary
                ),
                yaxis=dict(
                    title="", 
                    showgrid=False, 
                    showline=False,
                    tickangle=0,
                    tickfont=dict(color="#0f172a", size=13, family="Plus Jakarta Sans")
                ),
                coloraxis_colorbar=dict(
                    title=dict(text="Risk Scale", font=dict(color="#64748b", size=12)),
                    thicknessmode="pixels", thickness=15,
                    lenmode="pixels", len=200,
                    yanchor="middle", y=0.5,
                    tickfont=dict(color="#0f172a", size=11)
                ),
                margin=dict(l=10, r=30, t=30, b=10),
                hoverlabel=dict(bgcolor="#ffffff", font_size=13, font_family="Plus Jakarta Sans")
            )
            
            fig_bar.update_traces(
                textposition='outside',
                textfont=dict(size=14, color="#0f172a"),
                marker=dict(line=dict(color="rgba(227, 24, 55, 0.4)", width=1)),
                hovertemplate="<b>%{y}</b><br>Precursors: %{x}<extra></extra>"
            )
            
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No SIF Precursors identified in current logs.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-size: 1.1rem; font-weight: 700; color: #0f172a; margin-bottom: 15px;'>⚠️ Top Violated IOGP Life-Saving Rules</h3>", unsafe_allow_html=True)
        if not sif_df.empty and "iogp_rules" in sif_df.columns:
            all_rules = [rule for rules_list in sif_df["iogp_rules"].dropna() if isinstance(rules_list, list) for rule in rules_list]
            if all_rules:
                rule_series = pd.Series(all_rules).value_counts().reset_index()
                rule_series.columns = ["IOGP Rule", "Violation Count"]
                
                # Updated high-contrast corporate palette for distinct rule segments
                fig_pie = px.pie(
                    rule_series,
                    names="IOGP Rule",
                    values="Violation Count",
                    hole=0.6,
                    color_discrete_sequence=["#e31837", "#0ea5e9", "#f59e0b", "#10b981", "#8b5cf6", "#475569", "#0f172a"]
                )
                fig_pie.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#0f172a", family="Plus Jakarta Sans"),
                    margin=dict(l=10, r=10, t=10, b=10),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                fig_pie.update_traces(marker=dict(line=dict(color='#ffffff', width=2)))
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No IOGP rules mapped yet.")
        else:
            st.info("No rules data available.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

    # High-Risk Precursor Incident Feed
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size: 1.1rem; font-weight: 700; color: #0f172a; margin-bottom: 15px;'> Real-Time HSE Intelligence Feed</h3>", unsafe_allow_html=True)
    
    display_cols = [
        "created_at", "location", "activity", "is_sif_potential",
        "iogp_rules", "energy_source", "barrier_status", "recommended_action"
    ]
    actual_cols = [col for col in display_cols if col in df.columns]
    
    st.dataframe(
        df[actual_cols].sort_values(by=actual_cols[0], ascending=False),
        use_container_width=True,
        height=300
    )
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Database is currently empty. Use the sidebar form to submit test incident logs.")