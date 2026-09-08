import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from supabase import create_client

# ---------------- CONFIGURATION ----------------
SUPABASE_URL = "https://rmbpxtqzxxjcbapuzmxz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtYnB4dHF6eHhqY2JhcHV6bXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgzNjQ5NDMsImV4cCI6MjEwMzk0MDk0M30.ZUvIgfMbz9nf6iJ4v7Uk-vbvy1fvaNxr0vRrhqclJlU"
N8N_WEBHOOK_URL = "https://thesilentvisualizer.app.n8n.cloud/webhook/submit-safety-log"

# Initialize Supabase Client
@st.cache_resource
def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

st.set_page_config(
    page_title="OIL SIF-Precursor Intelligence",
    page_icon="🛡️",
    layout="wide"
)

# ---------------- HEADER ----------------
st.title("🛡️ Oil India Limited — SIF Precursor Intelligence Engine")
st.caption("AI-Powered Safety Triage, IOGP Life-Saving Rules Auto-Mapping, and Precursor Density Analytics")

# ---------------- SIDEBAR: INGESTION FORM ----------------
with st.sidebar:
    st.header("📝 Submit Field Safety Observation")
    st.markdown("Enter unstructured near-miss or observation text from drilling, workover, or production operations.")
    
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
    
    text = st.text_area("Observation / Incident Narrative", height=150, placeholder="Describe what happened, any equipment involved, and immediate safeguards present...")
    
    submit_btn = st.button("🚀 Ingest & Triage via AI Pipeline", use_container_width=True)
    
    if submit_btn:
        if text.strip():
            payload = {
                "report_id": f"OIL-WEB-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}",
                "location": loc,
                "activity": act,
                "report_text": text
            }
            with st.spinner("Dispatching payload through n8n workflow engine..."):
                try:
                    res = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=20)
                    if res.status_code == 200:
                        st.success("Triage Complete: Record classified, stored in database, and notifications routed.")
                    else:
                        st.error(f"Execution Error ({res.status_code}): {res.text}")
                except Exception as e:
                    st.error(f"Could not connect to n8n Webhook: {e}")
        else:
            st.warning("Please enter narrative text before submitting.")

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
    sif_df = df[df["is_sif_potential"] == True]
    sif_count = len(sif_df)
    sif_rate = (sif_count / total_logs) * 100 if total_logs > 0 else 0.0

    # Top KPI Metrics
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Ingested Reports", total_logs)
    kpi2.metric("Identified SIF Precursors", sif_count)
    kpi3.metric("SIF Precursor Density", f"{sif_rate:.1f}%")
    
    st.divider()

    # Visual Analytics Row
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📍 SIF Precursor Density by Asset / Location")
        if not sif_df.empty:
            density = sif_df["location"].value_counts().reset_index()
            density.columns = ["Location", "SIF Precursor Count"]
            fig_bar = px.bar(
                density,
                x="Location",
                y="SIF Precursor Count",
                color="SIF Precursor Count",
                color_continuous_scale="Reds",
                text="SIF Precursor Count"
            )
            fig_bar.update_layout(xaxis_title="Operating Asset", yaxis_title="Count of Fatal Precursors")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No SIF Precursors identified in current logs.")

    with col_right:
        st.subheader("⚠️ Top Violated IOGP Life-Saving Rules")
        if not sif_df.empty and "iogp_rules" in sif_df.columns:
            all_rules = [rule for rules_list in sif_df["iogp_rules"].dropna() for rule in rules_list]
            if all_rules:
                rule_series = pd.Series(all_rules).value_counts().reset_index()
                rule_series.columns = ["IOGP Rule", "Violation Count"]
                fig_pie = px.pie(
                    rule_series,
                    names="IOGP Rule",
                    values="Violation Count",
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No IOGP rules mapped yet.")
        else:
            st.info("No rules data available.")

    # High-Risk Precursor Incident Feed
    st.subheader("📋 Real-Time HSE Intelligence Feed")
    display_cols = [
        "created_at", "location", "activity", "is_sif_potential",
        "iogp_rules", "energy_source", "barrier_status", "recommended_action"
    ]
    st.dataframe(
        df[display_cols].sort_values(by="created_at", ascending=False),
        use_container_width=True
    )
else:
    st.info("Database is currently empty. Use the sidebar form to submit test incident logs.")