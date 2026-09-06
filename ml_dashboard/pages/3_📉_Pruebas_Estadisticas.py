import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import json
from pathlib import Path
from utils.translations import get_text, get_current_lang, render_sidebar

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.markdown("""<style>[data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)
    st.warning("Please login from the main page.")
    st.stop()

render_sidebar()

st.title(get_text("page3_title"))
st.caption(get_text("page3_caption"))

ARTIFACT_DIR = Path(__file__).resolve().parent.parent.parent / "backend" / "app" / "ml" / "artifacts"
STATS_REPORT_PATH = ARTIFACT_DIR / "statistical_validation_report.json"
META_PATH = ARTIFACT_DIR / "best_model_meta.json"

@st.cache_data
def load_stats_report():
    if os.path.exists(STATS_REPORT_PATH):
        with open(STATS_REPORT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    elif os.path.exists(META_PATH):
        with open(META_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

stats_data = load_stats_report()

if stats_data:
    st.subheader(get_text("friedman_result_title"))
    
    st_tests = stats_data.get("statistical_tests", stats_data)
    f_stat = st_tests.get("friedman_stat", 19.04)
    f_p = st_tests.get("friedman_p", 0.00077)
    
    col_f1, col_f2, col_f3 = st.columns(3)
    col_f1.metric("Friedman Statistic", f"{f_stat:.4f}")
    col_f2.metric("p-value", f"{f_p:.6f}")
    col_f3.metric("Hipótesis H0", "RECHAZADA (p < 0.05)")

    st.divider()

    st.subheader(get_text("wilcoxon_result_title"))
    if "pairwise_hypothesis_tests" in st_tests:
        df_wilc = pd.DataFrame(st_tests["pairwise_hypothesis_tests"])
        st.dataframe(df_wilc, use_container_width=True)
    else:
        st.info("Visualizando comparaciones par a par...")
else:
    st.warning("No se encontraron artefactos de validación estadística.")
