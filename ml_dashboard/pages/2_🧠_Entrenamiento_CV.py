import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as gg
import os
import json
import joblib
from pathlib import Path
from utils.translations import get_text, get_current_lang, render_sidebar
from utils.data_generator import generate_mining_telemetry_dataset

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.markdown("""<style>[data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)
    st.warning("Please login from the main page.")
    st.stop()

render_sidebar()

st.title(get_text("page2_title"))
st.caption(get_text("page2_caption"))

ARTIFACT_DIR = Path(__file__).resolve().parent.parent.parent / "backend" / "app" / "ml" / "artifacts"
CV_METRICS_PATH = ARTIFACT_DIR / "cv_metrics_results.json"
META_PATH = ARTIFACT_DIR / "best_model_meta.json"

@st.cache_data
def load_cv_data():
    cv_data = None
    meta_data = None
    if os.path.exists(CV_METRICS_PATH):
        with open(CV_METRICS_PATH, "r", encoding="utf-8") as f:
            cv_data = json.load(f)
    if os.path.exists(META_PATH):
        with open(META_PATH, "r", encoding="utf-8") as f:
            meta_data = json.load(f)
    return cv_data, meta_data

cv_results, meta_info = load_cv_data()

# Botón para ejecutar el pipeline de entrenamiento
col_tr1, col_tr2 = st.columns([3, 1])
with col_tr1:
    st.info(get_text("run_pipeline_info"))
with col_tr2:
    if st.button(get_text("run_pipeline_btn"), type="primary", use_container_width=True):
        with st.spinner("Training models with Stratified 5-Fold CV..."):
            from backend.scripts.train_cv import train_and_evaluate_cv
            from backend.scripts.robust_stats_validation import run_robust_stats_validation
            train_and_evaluate_cv()
            run_robust_stats_validation()
            st.cache_data.clear()
            st.success("¡Pipeline OK!")
            st.rerun()

st.divider()

if cv_results:
    # 1. Tabla Comparativa de Rendimiento
    st.subheader(get_text("table2_title"))
    
    summary_rows = []
    champion_name = meta_info.get("model_name", "Voting Classifier") if meta_info else ""
    
    for model_name, folds in cv_results.items():
        accs = [f["accuracy"] for f in folds]
        f1s = [f["f1_macro"] for f in folds]
        recs = [f["recall_macro"] for f in folds]
        aucs = [f["auc_roc"] for f in folds]
        inf_times = [f["inference_time_ms"] for f in folds]
        
        is_champion = (model_name == champion_name)
        badge = "🏆 " + get_text("champion_model") if is_champion else "⚪ Evaluated"
        
        summary_rows.append({
            "Status": badge,
            "Architecture": model_name,
            get_text("metric_accuracy"): f"{np.mean(accs):.4f} ± {np.std(accs):.4f}",
            get_text("metric_f1"): f"{np.mean(f1s):.4f}",
            get_text("metric_recall"): f"{np.mean(recs):.4f}",
            get_text("metric_auc"): f"{np.mean(aucs):.4f}",
            "Inference Time (ms)": f"{np.mean(inf_times):.2f} ms"
        })
        
    df_summary = pd.DataFrame(summary_rows)
    st.dataframe(df_summary, use_container_width=True)
    
    st.divider()
    
    # 2. Boxplot de Estabilidad (Figura 5)
    st.subheader(get_text("fig5_title"))
    
    boxplot_data = []
    for model_name, folds in cv_results.items():
        for fold in folds:
            boxplot_data.append({
                "Modelo": model_name,
                "Fold": f"Fold {fold['fold']}",
                "Accuracy": fold["accuracy"]
            })
    df_box = pd.DataFrame(boxplot_data)
    fig5 = px.box(df_box, x="Modelo", y="Accuracy", color="Modelo", points="all")
    st.plotly_chart(fig5, use_container_width=True)
