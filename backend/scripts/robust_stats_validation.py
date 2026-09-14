import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from scipy import stats
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score, accuracy_score, roc_auc_score
from xgboost import XGBClassifier

# Asegurar codificación utf-8 en consola de Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

RANDOM_STATE = 42

def run_robust_stats_validation():
    print("=" * 85)
    print("🔬 TAREA 2: VALIDACIÓN TÉCNICA DE PIPELINE - PROOF OF CONCEPT (PoC)")
    print("   [Estudio de Ablación Multimodal: Modelo Cinemático Base vs Modelo Híbrido]")
    print("   ⚠️ AVISO METODOLÓGICO: Este test de humo verifica la integridad de la arquitectura")
    print("      software para integrar variables heterogéneas. No constituye validación empírica.")
    print(f"   Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 85)

    # 1. Carga del Dataset
    dataset_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "public_mining_equipment_dataset.csv")
    dataset_path = os.path.abspath(dataset_path)

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"No se encontró el dataset en {dataset_path}")

    df = pd.read_csv(dataset_path)
    print(f"\n📂 Dataset cargado: {dataset_path} ({len(df)} registros)")

    # 2. Definición de Conjuntos de Características (Feature Sets)
    features_base = ['distance_3d', 'ttc', 'relative_speed', 'in_restricted_zone']
    features_hybrid = features_base + ['worker_bpm', 'fatigue_index', 'gas_co_ppm', 'dust_density_mg_m3']
    target_col = 'risk_level'

    X_base = df[features_base].values
    X_hybrid = df[features_hybrid].values
    y = df[target_col].values

    print(f"\n📋 Definición de Experimentos:")
    print(f"   - Modelo Base (Cinemático Espacial)  [4 features]: {features_base}")
    print(f"   - Modelo Híbrido (Multimodal Completo) [8 features]: {features_hybrid}")
    print(f"   - Distribución de Clases Target ({target_col}): {dict(pd.Series(y).value_counts())}")

    # 3. Stratified 10-Fold Cross-Validation
    print("\n⚙️ Ejecutando Stratified K-Fold Cross-Validation (k=10) para Ambos Modelos...")
    skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=RANDOM_STATE)

    f1_base_folds = []
    f1_hybrid_folds = []
    acc_base_folds = []
    acc_hybrid_folds = []

    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X_base, y), start=1):
        # Modelo Base
        xgb_base = XGBClassifier(random_state=RANDOM_STATE, eval_metric='mlogloss', n_estimators=100)
        xgb_base.fit(X_base[train_idx], y[train_idx])
        y_pred_base = xgb_base.predict(X_base[test_idx])
        f1_b = f1_score(y[test_idx], y_pred_base, average='macro')
        acc_b = accuracy_score(y[test_idx], y_pred_base)
        f1_base_folds.append(f1_b)
        acc_base_folds.append(acc_b)

        # Modelo Híbrido
        xgb_hybrid = XGBClassifier(random_state=RANDOM_STATE, eval_metric='mlogloss', n_estimators=100)
        xgb_hybrid.fit(X_hybrid[train_idx], y[train_idx])
        y_pred_hybrid = xgb_hybrid.predict(X_hybrid[test_idx])
        f1_h = f1_score(y[test_idx], y_pred_hybrid, average='macro')
        acc_h = accuracy_score(y[test_idx], y_pred_hybrid)
        f1_hybrid_folds.append(f1_h)
        acc_hybrid_folds.append(acc_h)

    # 4. Pruebas Estadísticas Pareadas y Tamaño del Efecto
    t_stat, p_val_t = stats.ttest_rel(f1_hybrid_folds, f1_base_folds)
    w_stat, p_val_w = stats.wilcoxon(f1_hybrid_folds, f1_base_folds)

    # 5. Imprimir Tabla por Fold
    print("\n📊 TABLA DE RESULTADOS POR FOLD (F1-SCORE MACRO):")
    print("=" * 75)
    print(f"{'Fold':<8} | {'F1 Base (Cinemático)':<22} | {'F1 Híbrido (Multimodal)':<24} | {'Diferencia (H-B)':<15}")
    print("-" * 75)

    diffs = []
    for i in range(10):
        diff = f1_hybrid_folds[i] - f1_base_folds[i]
        diffs.append(diff)
        print(f"Fold {i+1:<3} | {f1_base_folds[i]:<22.4f} | {f1_hybrid_folds[i]:<24.4f} | {diff:<+15.4f}")

    print("-" * 75)
    mean_base = np.mean(f1_base_folds)
    mean_hybrid = np.mean(f1_hybrid_folds)
    mean_diff = np.mean(diffs)
    std_base = np.std(f1_base_folds, ddof=1)
    std_hybrid = np.std(f1_hybrid_folds, ddof=1)
    std_diff = np.std(diffs, ddof=1)

    print(f"{'MEDIA':<8} | {mean_base:<22.4f} | {mean_hybrid:<24.4f} | {mean_diff:<+15.4f}")
    print(f"{'DESV.EST':<8} | {std_base:<22.4f} | {std_hybrid:<24.4f} | {std_diff:<15.4f}")
    print("=" * 75)

    # 6. Diagnóstico Estadístico Avanzado (Shapiro-Wilk, Cohen's d, IC 95%)
    shapiro_stat, shapiro_p = stats.shapiro(diffs)
    cohen_d = mean_diff / (std_diff if std_diff > 0 else 1e-6)
    se_diff = std_diff / np.sqrt(10)
    t_crit = stats.t.ppf(0.975, df=9)
    ic_inf = mean_diff - t_crit * se_diff
    ic_sup = mean_diff + t_crit * se_diff

    print("\n📈 PRUEBAS DE HIPÓTESIS ESTADÍSTICAS REALES (DATASET NO CIRCULAR RECALIBRADO):")
    print("-" * 75)
    print(f"0. Prueba de Normalidad de Diferencias (Shapiro-Wilk):")
    print(f"   - Estadístico W: {shapiro_stat:.4f} | Valor p: {shapiro_p:.4f} -> {'Normal (se justifica t-test)' if shapiro_p >= 0.05 else 'No normal (usar Wilcoxon)'}")
    print(f"1. Prueba t de Student Pareada (ttest_rel):")
    print(f"   - Estadístico t: {t_stat:.4f}")
    print(f"   - Valor p:       {p_val_t:.4e} ({'Significativo p < 0.001' if p_val_t < 0.001 else 'Significativo p < 0.05' if p_val_t < 0.05 else 'No significativo'})")
    print(f"2. Wilcoxon Signed-Rank Test (wilcoxon):")
    print(f"   - Estadístico W: {w_stat:.4f}")
    print(f"   - Valor p:       {p_val_w:.4e} ({'Significativo p < 0.01' if p_val_w < 0.01 else 'No significativo'})")
    print(f"3. Magnitud del Efecto y Confianza:")
    print(f"   - Tamaño de Efecto (Cohen's d): {cohen_d:.4f} ({'Efecto Grande (d > 0.8)' if abs(cohen_d) >= 0.8 else 'Efecto Moderado' if abs(cohen_d) >= 0.5 else 'Efecto Pequeño'})")
    print(f"   - IC 95% de la Diferencia (Δ F1): [{ic_inf:+.4f}, {ic_sup:+.4f}]")

    # 7. Generación de Gráfico Comparativo (Violin Boxplot)
    artifacts_dir = os.path.join(os.path.dirname(__file__), "..", "app", "ml", "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    plot_path = os.path.join(artifacts_dir, "ablation_f1_comparison.png")

    plt.figure(figsize=(9, 6), dpi=300)
    sns.set_theme(style="whitegrid")

    plot_data = pd.DataFrame({
        'F1-Score': f1_base_folds + f1_hybrid_folds,
        'Modelo': ['Base (Cinemático)'] * 10 + ['Híbrido (Multimodal)'] * 10
    })

    ax = sns.boxplot(x='Modelo', y='F1-Score', data=plot_data, palette=['#e74c3c', '#2ecc71'], width=0.4, boxprops=dict(alpha=0.8))
    sns.stripplot(x='Modelo', y='F1-Score', data=plot_data, color='black', size=7, jitter=0.15, alpha=0.7)

    plt.title("Estudio de Ablación de Pipeline: Distribució de F1-Score (10-Fold CV)\nModelo Cinemático Base vs Modelo Híbrido Multimodal", fontsize=12, fontweight='bold', pad=15)
    plt.ylabel("F1-Score (Macro Average)", fontsize=11)
    plt.xlabel("Arquitectura de Características", fontsize=11)
    plt.ylim(0.5, 1.02)

    # Anotación Estadística
    plt.text(0.5, 0.55, f"Prueba t pareada: t = {t_stat:.2f}, p = {p_val_t:.2e}\nWilcoxon: W = {w_stat:.1f}, p = {p_val_w:.4f}",
             horizontalalignment='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.9), fontsize=10)

    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()

    print(f"\n🖼️ Gráfico comparativo de ablación guardado en: {plot_path}")
    print("=" * 85)
    print("✅ VALIDACIÓN TÉCNICA Y PRUEBAS ESTADÍSTICAS FINALIZADAS EXITOSAMENTE.")

if __name__ == "__main__":
    run_robust_stats_validation()
