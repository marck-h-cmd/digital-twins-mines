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
    
    # Mapeo de valores por defecto idénticos a model_loader.py del backend
    defaults = {
        'distance_3d': 15.0, 'ttc': 10.0, 'relative_speed': 3.5,
        'worker_speed': 1.2, 'machine_speed': 2.3, 'in_restricted_zone': 0,
        'worker_bpm': 75.0, 'fatigue_index': 0.2, 'vibration_rms': 0.8,
        'gas_co_ppm': 10.0, 'dust_density_mg_m3': 1.0, 'ambient_light_lux': 60.0,
        'acceleration_z': 9.81, 'direction_worker': 0, 'direction_machine': 0, 'machine_status': 1
    }

    # Construir mapa de características telemétricas
    rel_speed = float(worker_speed + machine_speed)
    input_features = {
        'distance_3d': float(dist),
        'worker_speed': float(worker_speed),
        'machine_speed': float(machine_speed),
        'relative_speed': rel_speed,
        'direction_worker': 0,
        'direction_machine': 0,
        'ttc': float(ttc),
        'in_restricted_zone': int(in_restr),
        'machine_status': 1,
        'worker_bpm': float(bpm),
        'fatigue_index': float(fatigue),
        'vibration_rms': 0.8,
        'acceleration_z': 9.81,
        'gas_co_ppm': float(co_ppm),
        'dust_density_mg_m3': 1.0,
        'ambient_light_lux': float(lux)
    }

    model_obj = None
    scaler_obj = None
    model_name = "RandomForest"

    if isinstance(artifact, dict):
        model_obj = artifact.get("model")
        scaler_obj = artifact.get("scaler")
        model_name = artifact.get("model_name", "RandomForest")
    elif artifact is not None:
        model_obj = artifact

    if model_obj is not None:
        # Determinar nombres de columnas requeridos por el scaler/modelo
        required_cols = None
        if scaler_obj is not None and hasattr(scaler_obj, "feature_names_in_"):
            required_cols = list(scaler_obj.feature_names_in_)
        elif isinstance(artifact, dict) and "feature_names" in artifact:
            required_cols = artifact["feature_names"]
        
        if required_cols:
            for col in required_cols:
                if col not in input_features:
                    input_features[col] = defaults.get(col, 0.0)
            df_eval = pd.DataFrame([input_features])[required_cols]
        else:
            df_eval = pd.DataFrame([input_features])

        X_eval = scaler_obj.transform(df_eval) if scaler_obj is not None else df_eval.values
        pred_idx = int(model_obj.predict(X_eval)[0])
        probas = model_obj.predict_proba(X_eval)[0]
        
        class_labels = ["BAJO", "MEDIO", "ALTO"]
        predicted_class = class_labels[min(pred_idx, 2)]
        confidence = float(probas[pred_idx]) * 100

        res_col1, res_col2 = st.columns([1, 2])
        with res_col1:
            st.metric(label=f"Modelo Campeón ({model_name})", value=predicted_class, delta=f"Confianza: {confidence:.1f}%")

        with res_col2:
            st.write("**Probabilidades por Clase de Riesgo:**")
            st.progress(float(probas[0]), text=f"BAJO: {probas[0]*100:.1f}%")
            st.progress(float(probas[1]), text=f"MEDIO: {probas[1]*100:.1f}%")
            st.progress(float(probas[2]), text=f"ALTO: {probas[2]*100:.1f}%")

        if predicted_class == "ALTO":
            st.error(f"⚠️ **RIESGO ALTO (COLISIÓN / PELIGRO DETECTADO)** — Confianza del modelo: {confidence:.1f}%")
        elif predicted_class == "MEDIO":
            st.warning(f"⚡ **RIESGO MEDIO (PRECAUCIÓN OPERATIVA)** — Confianza del modelo: {confidence:.1f}%")
        else:
            st.success(f"✅ **RIESGO BAJO (OPERACIÓN SEGURA)** — Confianza del modelo: {confidence:.1f}%")
    else:
        # Fallback si no está el archivo compilado .joblib
        if dist < 5.0 or ttc < 2.5 or fatigue > 0.8:
            st.error("⚠️ **RIESGO ALTO** — Inferencia heurística (Artefacto no cargado)")
        elif dist < 12.0 or ttc < 5.0 or fatigue > 0.5:
            st.warning("⚡ **RIESGO MEDIO** — Inferencia heurística (Artefacto no cargado)")
        else:
            st.success("✅ **RIESGO BAJO** — Inferencia heurística (Artefacto no cargado)")
