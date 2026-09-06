import streamlit as st

TRANSLATIONS = {
    "es": {
        # App & Navigation
        "title": "Panel Científico — Gemelo Digital y Prevención de Riesgos (M-11)",
        "welcome": "Bienvenido al Dashboard Científico de Inteligencia Artificial M-11",
        "desc": "Utilice la barra lateral para navegar entre las fases de Análisis de Datos (EDA), Entrenamiento CV, Pruebas Estadísticas de Hipótesis, Gemelo Digital en Vivo y Generación de Reportes.",
        "app_title": "Panel Científico — Gemelo Digital M-11",
        "app_caption": "Sistema de Alerta Temprana de Riesgo Humano y Prevención Telemétrica",
        "sidebar_title": "⚙️ Configuración & Navegación",
        "sidebar_lang": "🌐 Idioma / Language",
        "login_title": "🔑 Inicio de Sesión — Panel Científico M-11",
        "login_caption": "Acceso seguro para investigadores y supervisores de seguridad minera",
        "fill_credentials": "📝 Rellenar Credenciales Admin",
        "direct_demo_login": "⚡ Login Directo Demo",
        "login_button": "🚀 Iniciar Sesión",
        "logout_button": "🔒 Cerrar Sesión",
        "username_label": "Usuario / Correo Electrónico",
        "password_label": "Contraseña",
        
        # Tabs & Pages
        "tab_dataset": "📊 1. Dataset Ficha 11",
        "tab_cv_training": "🧠 2. Entrenamiento & CV",
        "tab_stats": "📉 3. Pruebas Estadísticas",
        "tab_digital_twin": "🤖 4. Test Gemelo Digital",
        "tab_shap_reports": "📄 5. Explicabilidad & Reportes",
        "tab_shap_only": "🧬 Explicabilidad SHAP",
        "tab_reports_only": "📥 Generador de Reportes",
        
        # Page 1: Dataset EDA
        "page1_title": "📊 Fase 1: Análisis Exploratorio de Datos (EDA) - Telemetría Minera",
        "page1_caption": "Exploración estadística de telemetría de trabajadores y maquinaria en frentes de extracción subterránea (Sistema M-11)",
        "metric_total_telemetry": "Total Registros Telemetría",
        "metric_high_risk_level": "Nivel Riesgo Alto 🔴",
        "metric_avg_dist": "Distancia 3D Promedio",
        "metric_avg_ttc": "TTC Promedio (Tiempo al Impacto)",
        "sample_multimodal": "📋 Muestra del Dataset Multimodal",
        "fig1_title": "Figura 1: Distribución por Nivel de Riesgo",
        "fig2_title": "Figura 2: Distancia 3D vs Nivel de Riesgo",
        "fig3_title": "Figura 3: Matriz de Correlación de Variables Mineras",
        "fig4_title": "Figura 4: Índice de Fatiga vs Frecuencia Cardíaca (BPM)",
        "table1_title": "Tabla 1: Resumen Estadístico Descriptivo",

        # Page 2: CV Training
        "page2_title": "🧠 Fase 3 & 4: Entrenamiento Multimodelo y Validación Cruzada (K-Fold)",
        "page2_caption": "Comparación rigurosa de 5 arquitecturas (3 clásicas + 2 híbridas) con Stratified 5-Fold CV y SMOTE",
        "run_pipeline_info": "💡 Haz clic en 'Ejecutar Pipeline Completo' para re-entrenar las 5 arquitecturas con Stratified K-Fold + SMOTE y guardar los artefactos.",
        "run_pipeline_btn": "🚀 Ejecutar Pipeline",
        "table2_title": "Tabla 2: Evaluación Comparativa de Arquitecturas Tabulares",
        "fig5_title": "Figura 5: Boxplots de Estabilidad del Accuracy por Fold (K=5)",

        # Page 3: Statistical Tests
        "page3_title": "📉 Fase 4.3: Pruebas Estadísticas de Hipótesis (Friedman & Wilcoxon)",
        "page3_caption": "Validación rigurosa no paramétrica para confirmar la superioridad del modelo Campeón",
        "friedman_result_title": "1. Test de Hipótesis Global de Friedman",
        "wilcoxon_result_title": "2. Prueba de Rangos con Signo de Wilcoxon (Post-Hoc Test)",
        "table3_title": "Tabla 3: Resultados del Test de Wilcoxon Par a Par",

        # Page 4: Digital Twin
        "page4_title": "🤖 Gemelo Digital en Vivo & Simulador Telemétrico",
        "page4_caption": "Simulación en tiempo real de eventos de proximidad, fatiga y gases en frente M-11",
        "input_params_title": "1. Ingrese Parámetros Telemétricos de la Interacción",
        "btn_evaluate_event": "⚡ Evaluar Evento Telemétrico",
        "eval_results_title": "2. Resultado de la Inferencia del Gemelo Digital",

        # General Labels & KPIs
        "alert_high": "Riesgo Alto 🔴",
        "alert_medium": "Riesgo Medio 🟡",
        "alert_low": "Riesgo Bajo 🟢",
        "label_high": "ALTO",
        "label_medium": "MEDIO",
        "label_low": "BAJO",
        "total_records": "Total de Registros",
        "evaluator_name": "Ing. SANTOS FERNANDEZ JUAN PEDRO",
        "evaluator_label": "Evaluador / Responsable",
        "technical_notes_label": "Notas Técnicas / Observaciones",
        "default_notes": "Monitoreo telemétrico continuo en frentes de extracción M-11. Registro de alertas operacionales de proximidad y fatiga.",
        
        # Metrics
        "metric_accuracy": "Exactitud (Accuracy)",
        "metric_f1": "F1-Score Macro",
        "metric_precision": "Precisión Macro",
        "metric_recall": "Sensibilidad Macro (Recall)",
        "metric_auc": "Área Bajo la Curva (AUC-ROC)",
        "champion_model": "Modelo Campeón Seleccionado",
        
        # Columns
        "col_entity_id": "ID Trabajador / Entidad",
        "col_distance_3d": "Distancia 3D (m)",
        "col_ttc": "Tiempo Impacto TTC (s)",
        "col_bpm": "Ritmo Cardíaco (BPM)",
        "col_fatigue": "Índice de Fatiga",
        "col_gas_co": "Gas CO (PPM)",
        "col_risk": "Nivel de Riesgo",
        "col_action": "Acción Recomendada",
        
        # Buttons & Actions
        "button_preview": "📄 Generar / Actualizar Previsualización Completa",
        "button_download_pdf": "📥 Descargar PDF",
        "button_download_word": "📥 Descargar Word",
        "button_download_excel": "📥 Descargar Excel",
        "inspect_json": "{ } Estructura JSON Metadata",
        "inspect_markdown": "📝 Resumen Formateado en Markdown",
        "export_section_title": "📥 Exportar Reporte en Formatos Estándar",
        "config_panel_title": "⚙️ Panel de Configuración del Reporte (Personalización en Tiempo Real)",
        "include_friedman": "Incluir Pruebas Estadísticas (Friedman & Wilcoxon)",
        
        # Report Sections
        "rep_header_title": "SISTEMA M-11 — GEMELO DIGITAL Y PREVENCIÓN DE RIESGOS",
        "rep_header_subtitle": "Informe Técnico de Alerta Temprana y Evaluación de Simulaciones",
        "rep_sec1_title": "1. Resumen Ejecutivo de Evaluaciones",
        "rep_sec2_title": "2. Notas Técnicas u Observaciones Clínicas/Técnicas",
        "rep_sec3_title": "3. Muestra de Datos Telemétricos y Alertas",
        "rep_sec4_title": "4. Visualizaciones Físicas y Gráficos Telemétricos",
        "rep_sec5_title": "5. Rendimiento del Modelo Campeón (RandomForest)",
        "rep_sec6_title": "6. ANEXO: Validación Estadística de Hipótesis (Friedman & Wilcoxon)",
    },
    "en": {
        # App & Navigation
        "title": "Scientific Panel — Digital Twin & Risk Prevention (M-11)",
        "welcome": "Welcome to M-11 AI Scientific Dashboard",
        "desc": "Use the sidebar to navigate between Data Analysis (EDA), CV Training, Statistical Hypothesis Testing, Live Digital Twin, and Report Generation.",
        "app_title": "Scientific Panel — M-11 Digital Twin",
        "app_caption": "Human Risk Early Warning System & Telemetry Prevention",
        "sidebar_title": "⚙️ Settings & Navigation",
        "sidebar_lang": "🌐 Language / Idioma",
        "login_title": "🔑 Login — M-11 Scientific Panel",
        "login_caption": "Secure access for researchers and mining safety supervisors",
        "fill_credentials": "📝 Fill Admin Credentials",
        "direct_demo_login": "⚡ Direct Demo Login",
        "login_button": "🚀 Log In",
        "logout_button": "🔒 Log Out",
        "username_label": "Username / Email",
        "password_label": "Password",
        
        # Tabs & Pages
        "tab_dataset": "📊 1. Dataset Sheet 11",
        "tab_cv_training": "🧠 2. CV Training",
        "tab_stats": "📉 3. Statistical Tests",
        "tab_digital_twin": "🤖 4. Digital Twin Test",
        "tab_shap_reports": "📄 5. Explainability & Reports",
        "tab_shap_only": "🧬 SHAP Explainability",
        "tab_reports_only": "📥 Report Generator",

        # Page 1: Dataset EDA
        "page1_title": "📊 Phase 1: Exploratory Data Analysis (EDA) - Mining Telemetry",
        "page1_caption": "Statistical exploration of worker and machinery telemetry in underground extraction fronts (M-11 System)",
        "metric_total_telemetry": "Total Telemetry Records",
        "metric_high_risk_level": "High Risk Level 🔴",
        "metric_avg_dist": "Average 3D Distance",
        "metric_avg_ttc": "Average TTC (Time to Collision)",
        "sample_multimodal": "📋 Multimodal Dataset Sample",
        "fig1_title": "Figure 1: Distribution by Risk Level",
        "fig2_title": "Figure 2: 3D Distance vs Risk Level",
        "fig3_title": "Figure 3: Mining Variables Correlation Matrix",
        "fig4_title": "Figure 4: Fatigue Index vs Heart Rate (BPM)",
        "table1_title": "Table 1: Descriptive Statistical Summary",

        # Page 2: CV Training
        "page2_title": "🧠 Phase 3 & 4: Multi-model Training & Cross-Validation (K-Fold)",
        "page2_caption": "Rigorous comparison of 5 architectures (3 classical + 2 hybrid) with Stratified 5-Fold CV and SMOTE",
        "run_pipeline_info": "💡 Click 'Run Full Pipeline' to retrain the 5 architectures with Stratified K-Fold + SMOTE and save artifacts.",
        "run_pipeline_btn": "🚀 Run Pipeline",
        "table2_title": "Table 2: Comparative Evaluation of Tabular Architectures",
        "fig5_title": "Figure 5: Accuracy Stability Boxplots by Fold (K=5)",

        # Page 3: Statistical Tests
        "page3_title": "📉 Phase 4.3: Statistical Hypothesis Testing (Friedman & Wilcoxon)",
        "page3_caption": "Rigorous non-parametric validation to confirm Champion model superiority",
        "friedman_result_title": "1. Friedman Global Hypothesis Test",
        "wilcoxon_result_title": "2. Wilcoxon Signed-Rank Test (Post-Hoc Test)",
        "table3_title": "Table 3: Pairwise Wilcoxon Test Results",

        # Page 4: Digital Twin
        "page4_title": "🤖 Live Digital Twin & Telemetry Simulator",
        "page4_caption": "Real-time simulation of proximity, fatigue, and gas events at M-11 front",
        "input_params_title": "1. Input Interaction Telemetric Parameters",
        "btn_evaluate_event": "⚡ Evaluate Telemetric Event",
        "eval_results_title": "2. Digital Twin Inference Result",
        
        # General Labels & KPIs
        "alert_high": "High Risk 🔴",
        "alert_medium": "Medium Risk 🟡",
        "alert_low": "Low Risk 🟢",
        "label_high": "HIGH",
        "label_medium": "MEDIUM",
        "label_low": "LOW",
        "total_records": "Total Records",
        "evaluator_name": "Ing. SANTOS FERNANDEZ JUAN PEDRO",
        "evaluator_label": "Evaluator / Supervisor",
        "technical_notes_label": "Technical Notes / Remarks",
        "default_notes": "Continuous telemetric monitoring at M-11 extraction fronts. Proximity and fatigue operational alert log.",
        
        # Metrics
        "metric_accuracy": "Accuracy",
        "metric_f1": "Macro F1-Score",
        "metric_precision": "Macro Precision",
        "metric_recall": "Macro Sensitivity (Recall)",
        "metric_auc": "Area Under Curve (AUC-ROC)",
        "champion_model": "Selected Champion Model",
        
        # Columns
        "col_entity_id": "Worker ID / Entity",
        "col_distance_3d": "3D Distance (m)",
        "col_ttc": "Time to Collision TTC (s)",
        "col_bpm": "Heart Rate (BPM)",
        "col_fatigue": "Fatigue Index",
        "col_gas_co": "Gas CO (PPM)",
        "col_risk": "Risk Level",
        "col_action": "Recommended Action",
        
        # Buttons & Actions
        "button_preview": "📄 Generate / Update Complete Preview",
        "button_download_pdf": "📥 Download PDF",
        "button_download_word": "📥 Download Word",
        "button_download_excel": "📥 Download Excel",
        "inspect_json": "{ } JSON Metadata Structure",
        "inspect_markdown": "📝 Formatted Markdown Summary",
        "export_section_title": "📥 Export Report in Standard Formats",
        "config_panel_title": "⚙️ Report Configuration Panel (Real-time Customization)",
        "include_friedman": "Include Statistical Tests (Friedman & Wilcoxon)",
        
        # Report Sections
        "rep_header_title": "SYSTEM M-11 — DIGITAL TWIN AND RISK PREVENTION",
        "rep_header_subtitle": "Early Warning Technical Report & Simulation Evaluation",
        "rep_sec1_title": "1. Executive Summary of Evaluations",
        "rep_sec2_title": "2. Technical & Clinical Remarks",
        "rep_sec3_title": "3. Telemetric Data & Alert Sample",
        "rep_sec4_title": "4. Physical Visualizations & Telemetry Charts",
        "rep_sec5_title": "5. Champion Model Performance (RandomForest)",
        "rep_sec6_title": "6. APPENDIX: Statistical Hypothesis Validation (Friedman & Wilcoxon)",
    }
}


def get_text(key: str, default: str = None) -> str:
    """
    Retorna la traducción correspondiente a la clave `key` según el idioma actual en `st.session_state`.
    Soporta fallback a español o al parámetro `default` si la clave no existe.
    """
    lang = st.session_state.get("language", st.session_state.get("lang", "es"))
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["es"])
    if key in lang_dict:
        return lang_dict[key]
    if default is not None:
        return default
    return TRANSLATIONS["es"].get(key, key)


def get_current_lang() -> str:
    """Retorna el código de idioma actual ('es' o 'en')."""
    return st.session_state.get("language", st.session_state.get("lang", "es"))


def init_language():
    """Inicializa la clave `language` en session_state si no existe."""
    if "language" not in st.session_state and "lang" not in st.session_state:
        st.session_state.language = "es"
        st.session_state.lang = "es"
    elif "language" not in st.session_state:
        st.session_state.language = st.session_state.lang
    elif "lang" not in st.session_state:
        st.session_state.lang = st.session_state.language


def render_sidebar():
    """Renderiza la barra lateral compartida con selector de idioma en todas las páginas."""
    init_language()
    st.sidebar.title(get_text("sidebar_title"))
    
    current_l = get_current_lang()
    lang_choice = st.sidebar.selectbox(
        get_text("sidebar_lang"),
        options=["es", "en"],
        format_func=lambda x: "🇪🇸 Español" if x == "es" else "🇺🇸 English",
        index=0 if current_l == "es" else 1,
        key="shared_global_lang_selectbox"
    )
    if lang_choice != current_l:
        st.session_state.language = lang_choice
        st.session_state.lang = lang_choice
        if hasattr(st, "rerun"):
            st.rerun()
        elif hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
            
    st.sidebar.divider()
    st.sidebar.info(get_text("app_title"))
