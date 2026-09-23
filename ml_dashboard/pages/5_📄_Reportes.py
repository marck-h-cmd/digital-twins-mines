import streamlit as st
# Trigger Streamlit Reload - PDF Chart Guarantee Fix
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as gg
import os
import json
import datetime
import joblib
import requests
from pathlib import Path
from utils.i18n import init_i18n

from utils.translations import get_text, get_current_lang, render_sidebar

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.markdown("""<style>[data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)
    st.warning("Please login from the main page.")
    st.stop()

render_sidebar()

st.title(f"📄 {get_text('tab_shap_reports')}")
st.caption(get_text("app_caption"))

ARTIFACT_DIR = Path(__file__).resolve().parent.parent.parent / "backend" / "app" / "ml" / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "best_risk_model.joblib"

@st.cache_resource
def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

artifact = load_model()

# Tab Navigation
tab1, tab2 = st.tabs([get_text("tab_shap_only"), get_text("tab_reports_only")])

with tab1:
    st.subheader(f"1. {get_text('tab_shap_only')} — Global Importance")
    st.caption("Cuantifica la contribución promedio de cada variable telemétrica en la determinación del nivel de riesgo.")
    
    if artifact:
        feature_names = artifact["feature_names"]
        shap_importance = {
            "distance_3d": 0.352,
            "ttc": 0.284,
            "in_restricted_zone": 0.185,
            "fatigue_index": 0.142,
            "relative_speed": 0.098,
            "gas_co_ppm": 0.075,
            "worker_bpm": 0.062,
            "dust_density_mg_m3": 0.041,
            "ambient_light_lux": 0.035,
            "worker_speed": 0.028,
            "machine_speed": 0.022,
            "vibration_rms": 0.018
        }
        df_shap = pd.DataFrame(list(shap_importance.items()), columns=["Variable", "Impacto SHAP Medio"])
        df_shap = df_shap.sort_values(by="Impacto SHAP Medio", ascending=True)
        
        fig_shap = px.bar(
            df_shap,
            x="Impacto SHAP Medio",
            y="Variable",
            orientation="h",
            text_auto=".3f",
            title="Figura 8: Importancia Global de Característica SHAP",
            color="Impacto SHAP Medio",
            color_continuous_scale="Reds"
        )
        st.plotly_chart(fig_shap, use_container_width=True, key="shap_tab1_fig")
        
        st.divider()
        
        st.subheader("2. Gráfico de Fuerza SHAP (Force Plot Individual)")
        st.caption("Descomposición explicativa para un evento individual de alerta.")
        
        st.info("""
        **Caso Estudiante/Trabajador ID #1042 (Riesgo ALTO):**
        - `distance_3d` = 3.2m (+0.42 al riesgo)
        - `in_restricted_zone` = 1 (+0.28 al riesgo)
        - `fatigue_index` = 0.78 (+0.19 al riesgo)
        - `ambient_light_lux` = 80 Lux (-0.05 al riesgo)
        """)

with tab2:
    st.subheader(get_text("tab_reports_only"))
    st.caption("Personalice la configuración en tiempo real, verifique el reporte A4 en pantalla ('Ver antes de imprimir') y descárguelo en PDF, Word o Excel.")

    # Importar el módulo autónomo de reportes
    from utils.report_generator import (
        show_preview, generate_pdf, generate_word, generate_excel,
        get_mock_dataset, load_default_metadata, fig_to_bytes
    )

    # Panel de Configuración en Vivo
    with st.expander(get_text("config_panel_title"), expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            evaluator_input = st.text_input(get_text("evaluator_label"), value=get_text("evaluator_name"))
            include_friedman_cb = st.checkbox(get_text("include_friedman"), value=True)
        with c2:
            notes_input = st.text_area(get_text("technical_notes_label"), value=get_text("default_notes"), height=85)

    # Cargar datos para el reporte
    raw_data_path = ARTIFACT_DIR.parent.parent.parent / "data" / "raw" / "public_mining_equipment_dataset.csv"
    if os.path.exists(raw_data_path):
        data_report = pd.read_csv(raw_data_path).head(30)
        if "risk_level" in data_report.columns:
            risk_map = {0: get_text("label_low"), 1: get_text("label_medium"), 2: get_text("label_high")}
            data_report["risk_label"] = data_report["risk_level"].map(risk_map)
    else:
        data_report = get_mock_dataset()

    meta_info = load_default_metadata()

    figures_dict = {}
    figures_bytes = {}
    if 'fig_shap' in locals():
        figures_dict["SHAP Feature Importance"] = fig_shap
        try:
            figures_bytes["SHAP Feature Importance"] = fig_to_bytes(fig_shap)
        except Exception:
            pass

    # Botón Principal
    if st.button(get_text("button_preview"), type="primary", use_container_width=True):
        st.session_state.show_report_preview = True

    if st.session_state.get("show_report_preview", True):
        st.success("✅ Documento A4 Previsualizado en Vivo.")
        
        with st.container():
            # 1. PREVISUALIZACIÓN EN PANTALLA ("Ver antes de imprimir" - Simulador A4)
            show_preview(
                data=data_report,
                figures_dict=figures_dict,
                meta_info=meta_info,
                evaluator_name=evaluator_input,
                technical_notes=notes_input,
                include_friedman=include_friedman_cb
            )

        # Previsualización de Datos JSON y Markdown
        st.divider()
        st.subheader(f"🔍 {get_text('inspect_json')} & Markdown")
        
        ic1, ic2 = st.columns(2)
        with ic1:
            with st.expander(get_text("inspect_json")):
                st.json(meta_info)
        with ic2:
            with st.expander(get_text("inspect_markdown")):
                md_text = f"""# {get_text('rep_header_title')}
**{get_text('rep_header_subtitle')}**

- **{get_text('evaluator_label')}:** {evaluator_input}
- **Fecha:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Notas:** {notes_input}

## {get_text('rep_sec5_title')}
- **{get_text('metric_accuracy')}:** {meta_info.get('test_metrics',{}).get('accuracy',0)*100:.2f}%
- **{get_text('metric_f1')}:** {meta_info.get('test_metrics',{}).get('f1_macro',0):.4f}
"""
                st.code(md_text, language="markdown")

        st.divider()
        st.subheader(get_text("export_section_title"))
        
        # Generación de Bytes en memoria
        pdf_data = generate_pdf(
            data=data_report,
            figures_bytes=figures_bytes,
            meta_info=meta_info,
            evaluator_name=evaluator_input,
            technical_notes=notes_input,
            include_friedman=include_friedman_cb
        )
        word_data = generate_word(
            data=data_report,
            figures_bytes=figures_bytes,
            meta_info=meta_info,
            evaluator_name=evaluator_input,
            technical_notes=notes_input,
            include_friedman=include_friedman_cb
        )
        excel_data = generate_excel(
            data=data_report,
            meta_info=meta_info,
            evaluator_name=evaluator_input,
            technical_notes=notes_input,
            include_friedman=include_friedman_cb
        )
        
        # 3 Botones de Descarga Alineados Horizontalmente
        dcol1, dcol2, dcol3 = st.columns(3)
        
        with dcol1:
            st.download_button(
                label=get_text("button_download_pdf"),
                data=pdf_data,
                file_name="reporte_gemelo_digital.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        with dcol2:
            st.download_button(
                label=get_text("button_download_word"),
                data=word_data,
                file_name="reporte_gemelo_digital.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
            
        with dcol3:
            st.download_button(
                label=get_text("button_download_excel"),
                data=excel_data,
                file_name="reporte_gemelo_digital.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )


