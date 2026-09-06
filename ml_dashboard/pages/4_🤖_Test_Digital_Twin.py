import streamlit as st
import pandas as pd
import numpy as np
import os
import joblib
from pathlib import Path
from utils.translations import get_text, get_current_lang, render_sidebar

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.markdown("""<style>[data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)
    st.warning("Please login from the main page.")
    st.stop()

render_sidebar()

st.title(get_text("page4_title"))
st.caption(get_text("page4_caption"))

ARTIFACT_DIR = Path(__file__).resolve().parent.parent.parent / "backend" / "app" / "ml" / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "best_risk_model.joblib"

@st.cache_resource
def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

artifact = load_model()

st.subheader(get_text("input_params_title"))

c1, c2, c3 = st.columns(3)

with c1:
    dist = st.number_input(get_text("col_distance_3d"), min_value=0.1, max_value=100.0, value=8.5, step=0.5)
    worker_speed = st.number_input("Velocidad Trabajador (m/s)" if get_current_lang() == "es" else "Worker Speed (m/s)", min_value=0.0, max_value=10.0, value=1.2, step=0.1)
    machine_speed = st.number_input("Velocidad Maquinaria (m/s)" if get_current_lang() == "es" else "Machinery Speed (m/s)", min_value=0.0, max_value=30.0, value=4.0, step=0.5)

with c2:
    ttc = st.number_input(get_text("col_ttc"), min_value=0.1, max_value=30.0, value=3.2, step=0.2)
    in_restr = st.selectbox("¿En Zona Restringida?" if get_current_lang() == "es" else "In Restricted Zone?", options=[0, 1], format_func=lambda x: ("Sí (1)" if x == 1 else "No (0)") if get_current_lang() == "es" else ("Yes (1)" if x == 1 else "No (0)"))
    fatigue = st.slider(get_text("col_fatigue"), min_value=0.0, max_value=1.0, value=0.65, step=0.05)

with c3:
    bpm = st.number_input(get_text("col_bpm"), min_value=40.0, max_value=200.0, value=125.0, step=1.0)
    co_ppm = st.number_input(get_text("col_gas_co"), min_value=0.0, max_value=200.0, value=28.0, step=1.0)
    lux = st.number_input("Iluminación (Lux)" if get_current_lang() == "es" else "Ambient Light (Lux)", min_value=0.0, max_value=500.0, value=35.0, step=5.0)

if st.button(get_text("btn_evaluate_event"), type="primary", use_container_width=True):
    st.subheader(get_text("eval_results_title"))
    
    if dist < 5.0 or ttc < 2.5 or fatigue > 0.8:
        risk_label = get_text("alert_high")
        st.error(f"⚠️ **{risk_label}** — {get_text('alert_high')}")
    elif dist < 12.0 or ttc < 5.0 or fatigue > 0.5:
        risk_label = get_text("alert_medium")
        st.warning(f"⚡ **{risk_label}** — {get_text('alert_medium')}")
    else:
        risk_label = get_text("alert_low")
        st.success(f"✅ **{risk_label}** — {get_text('alert_low')}")
