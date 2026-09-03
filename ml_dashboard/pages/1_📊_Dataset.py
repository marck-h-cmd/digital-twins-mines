import streamlit as st
import pandas as pd
import plotly.express as px
from utils.i18n import init_i18n

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.markdown("""<style>[data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)
    st.warning("Please login from the main page.")
    st.stop()

init_i18n()
t = st.session_state.t

st.title(t["nav_dataset"])

import os
from pathlib import Path

@st.cache_data
def load_data():
    possible_paths = [
        Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "synthetic_interactions.csv",
        Path("data/raw/synthetic_interactions.csv"),
        Path("../data/raw/synthetic_interactions.csv"),
    ]
    for p in possible_paths:
        if os.path.exists(p):
            try:
                return pd.read_csv(p)
            except Exception as e:
                st.error(f"Error reading CSV at {p}: {e}")
                return pd.DataFrame()
    st.error(f"Dataset file not found. Tried paths: {[str(p) for p in possible_paths]}")
    return pd.DataFrame()

df = load_data()

if not df.empty:
    st.write(f"### M-11 Dataset Multimodal (50,000 Registros)")
    st.dataframe(df.head(100))
    
    # Map numeric labels to descriptive readable labels
    risk_labels = {0: 'BAJO (0)', 1: 'MEDIO (1)', 2: 'ALTO (2)'}
    df['risk_label'] = df['risk_level'].map(lambda x: risk_labels.get(x, str(x)))

    status_labels = {0: 'Detenida (0)', 1: 'Operando (1)', 2: 'Reversa (2)', 3: 'Transporte (3)'}
    if 'machine_status' in df.columns:
        df['status_label'] = df['machine_status'].map(lambda x: status_labels.get(x, str(x)))

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribución por Nivel de Riesgo")
        risk_counts = df['risk_label'].value_counts().reset_index()
        risk_counts.columns = ['Nivel_Riesgo', 'Cantidad']
        fig = px.pie(
            risk_counts,
            values='Cantidad',
            names='Nivel_Riesgo',
            title="Distribución de Alertas por Riesgo",
            hole=0.35,
            color='Nivel_Riesgo',
            color_discrete_map={
                'BAJO (0)': '#22c55e',
                'MEDIO (1)': '#eab308',
                'ALTO (2)': '#ef4444'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Frecuencia de Estado Operativo de Maquinaria")
        if 'status_label' in df.columns:
            status_counts = df['status_label'].value_counts().reset_index()
            status_counts.columns = ['Estado_Maquina', 'Cantidad']
            fig2 = px.bar(
                status_counts,
                x='Estado_Maquina',
                y='Cantidad',
                color='Estado_Maquina',
                title="Conteo por Estado Operativo LHD/Scooptram"
            )
            st.plotly_chart(fig2, use_container_width=True)

    # Histogram of distance_3d vs risk_level
    if 'distance_3d' in df.columns:
        st.subheader("Histograma: Distancia 3D vs Nivel de Riesgo")
        fig3 = px.histogram(
            df,
            x="distance_3d",
            color="risk_label",
            nbins=40,
            title="Distribución de Distancias Físicas por Nivel de Riesgo",
            color_discrete_map={
                'BAJO (0)': '#22c55e',
                'MEDIO (1)': '#eab308',
                'ALTO (2)': '#ef4444'
            }
        )
        st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("No data available.")
