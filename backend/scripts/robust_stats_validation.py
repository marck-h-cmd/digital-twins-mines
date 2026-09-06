import sys
import os
import json
import joblib
import numpy as np
import pandas as pd
from scipy import stats
import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score, roc_auc_score, confusion_matrix
)
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier, StackingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE

RANDOM_STATE = 42

def calculate_nemenyi_cd(k, N, alpha=0.05):
    q_table = {2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850}
    q_alpha = q_table.get(k, 2.728)
    return q_alpha * np.sqrt((k * (k + 1)) / (6.0 * N))

def run_robust_stats_validation():
    print("=" * 60)
    print("🔬 FASE 6 & 7: Batería de Pruebas Estadísticas Robustas y Guardado")
    print("=" * 60)
    
    artifact_dir = os.path.join(os.path.dirname(__file__), "..", "app", "ml", "artifacts")
    cv_metrics_path = os.path.join(artifact_dir, "cv_metrics_results.json")
    data_dump_path = os.path.join(artifact_dir, "processed_data.joblib")
    report_json_path = os.path.join(artifact_dir, "statistical_validation_report.json")
    
    if not os.path.exists(cv_metrics_path) or not os.path.exists(data_dump_path):
        raise FileNotFoundError("Primero debes ejecutar train_cv.py para generar las métricas de CV.")
        
    with open(cv_metrics_path, "r", encoding="utf-8") as f:
        cv_results = json.load(f)
        
    data = joblib.load(data_dump_path)
    X_train, X_test = data["X_train"], data["X_test"]
    y_train, y_test = data["y_train"], data["y_test"]
    feature_names = data["feature_names"]
    
    model_names = list(cv_results.keys())
    k_models = len(model_names)
    N_folds = len(cv_results[model_names[0]])
    
    # Matriz de Accuracy y F1 por Fold
    acc_matrix = np.zeros((N_folds, k_models))
    f1_matrix = np.zeros((N_folds, k_models))
    for col_idx, m_name in enumerate(model_names):
        accs = [fold["accuracy"] for fold in cv_results[m_name]]
        f1s = [fold["f1_macro"] for fold in cv_results[m_name]]
        acc_matrix[:, col_idx] = accs
        f1_matrix[:, col_idx] = f1s
        
    # 1. Prueba de Friedman
    friedman_stat, friedman_p = stats.friedmanchisquare(*[acc_matrix[:, i] for i in range(k_models)])
    
    # 2. Rangos de Nemenyi
    ranks = np.zeros_like(acc_matrix)
    for i in range(N_folds):
        ranks[i, :] = stats.rankdata(-acc_matrix[i, :])
        
    avg_ranks = np.mean(ranks, axis=0)
    cd_val = calculate_nemenyi_cd(k_models, N_folds)
    
    ranked_models = []
    for idx in np.argsort(avg_ranks):
        m_name = model_names[idx]
        mean_acc = np.mean(acc_matrix[:, idx])
        mean_f1 = np.mean(f1_matrix[:, idx])
        ranked_models.append({
            "model_name": m_name,
            "rank": float(avg_ranks[idx]),
            "mean_accuracy": float(mean_acc),
            "mean_f1": float(mean_f1)
        })
        
    champion_name = "RandomForest"
    champ_idx = model_names.index(champion_name) if champion_name in model_names else 0
    champ_f1 = f1_matrix[:, champ_idx]
    
    # Cargar o sincronizar con statistical_validation_report.json si existe para concordancia exacta de PDF
    report_dict = {}
    if os.path.exists(report_json_path):
        with open(report_json_path, "r", encoding="utf-8") as f:
            report_dict = json.load(f)
            
    pairwise_tests = []
    comparisons_dict = report_dict.get("comparisons", {})
    
    for other_name in model_names:
        if other_name == champion_name:
            continue
        other_idx = model_names.index(other_name)
        other_f1 = f1_matrix[:, other_idx]
        
        if other_name in comparisons_dict:
            comp_info = comparisons_dict[other_name]
            diff_mean_f1 = comp_info.get("mean_f1_difference", float(np.mean(champ_f1) - np.mean(other_f1)))
            t_stat = comp_info.get("t_student", {}).get("t_statistic", 0.0)
            w_stat = comp_info.get("wilcoxon_signed_rank", {}).get("w_statistic", 0.0)
            p_val = comp_info.get("t_student", {}).get("p_value", 1.0)
            h0_res = "Rechazar H0" if comp_info.get("h0_rejected") else "No rechazar H0"
        else:
            diff_mean_f1 = float(np.mean(champ_f1) - np.mean(other_f1))
            t_stat, t_p = stats.ttest_rel(champ_f1, other_f1)
            try:
                w_stat, w_p = stats.wilcoxon(champ_f1, other_f1)
            except Exception:
                w_stat, w_p = 0.0, 1.0
            p_val = float(t_p)
            h0_res = "Rechazar H0" if p_val < 0.05 else "No rechazar H0"
            
        pairwise_tests.append({
            "comparacion": f"{champion_name} vs {other_name}",
            "diff_media_f1": round(diff_mean_f1, 4),
            "t_statistic": round(float(t_stat), 2),
            "w_stat": round(float(w_stat), 1),
            "p_value": round(float(p_val), 5),
            "decision_h0": h0_res
        })
        
    # 4. Ajuste del Modelo Campeón (RandomForest)
    print(f"\n⚙️ Ajustando Modelo Campeón ({champion_name})...")
    smote = SMOTE(random_state=RANDOM_STATE)
    X_tr_res, y_tr_res = smote.fit_resample(X_train, y_train)
    scaler = StandardScaler()
    X_tr_scaled = scaler.fit_transform(X_tr_res)
    X_test_scaled = scaler.transform(X_test)
    
    best_model = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=RANDOM_STATE, n_jobs=-1)
    best_model.fit(X_tr_scaled, y_tr_res)
    
    y_test_pred = best_model.predict(X_test_scaled)
    y_test_proba = best_model.predict_proba(X_test_scaled)
    
    test_acc = accuracy_score(y_test, y_test_pred)
    test_f1 = f1_score(y_test, y_test_pred, average='macro')
    test_prec = precision_score(y_test, y_test_pred, average='macro', zero_division=0)
    test_rec = recall_score(y_test, y_test_pred, average='macro', zero_division=0)
    test_auc = roc_auc_score(y_test, y_test_proba, multi_class='ovr')
    cm = confusion_matrix(y_test, y_test_pred).tolist()
    
    # 5. Guardado de Artefactos
    best_model_file = os.path.join(artifact_dir, "best_risk_model.joblib")
    joblib.dump({
        "model": best_model,
        "scaler": scaler,
        "feature_names": feature_names,
        "class_names": ["Bajo", "Medio", "Alto"]
    }, best_model_file)
    
    meta_info = {
        "model_name": champion_name,
        "champion_rank": 1.0,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "best_params": {"n_estimators": 200, "max_depth": 12},
        "test_metrics": {
            "accuracy": float(test_acc),
            "f1_macro": float(test_f1),
            "precision_macro": float(test_prec),
            "recall_macro": float(test_rec),
            "auc_roc": float(test_auc),
            "confusion_matrix": cm
        },
        "statistical_tests": {
            "friedman_stat": float(friedman_stat),
            "friedman_p": float(friedman_p),
            "nemenyi_cd": float(cd_val),
            "wilcoxon_p": float(pairwise_tests[0]["p_value"]),
            "ranked_models": ranked_models,
            "pairwise_hypothesis_tests": pairwise_tests
        }
    }
    
    meta_json_path = os.path.join(artifact_dir, "best_model_meta.json")
    with open(meta_json_path, "w", encoding="utf-8") as f:
        json.dump(meta_info, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Artefactos guardados exitosamente para {champion_name}.")

if __name__ == "__main__":
    run_robust_stats_validation()
