import sys
import os
import time
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier, StackingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score, roc_auc_score, confusion_matrix
)
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE

RANDOM_STATE = 42

def load_official_dataset():
    """Carga el dataset oficial de la Ficha 11 / Paper desde data/raw/public_mining_equipment_dataset.csv."""
    possible_paths = [
        Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "public_mining_equipment_dataset.csv",
        Path("data/raw/public_mining_equipment_dataset.csv"),
    ]
    for p in possible_paths:
        if os.path.exists(p):
            print(f"📦 Cargando Dataset Oficial de Ficha 11 desde: {p}")
            df = pd.read_csv(p)
            return df
    raise FileNotFoundError("No se encontró public_mining_equipment_dataset.csv en data/raw/")

def train_and_evaluate_cv():
    print("=" * 60)
    print("🚀 FASE 1 & 2: Carga de Dataset Oficial Ficha 11 y Validacion Cruzada (K=5)")
    print("=" * 60)
    
    # 1. Cargar Dataset Oficial de Ficha 11
    df = load_official_dataset()
    
    feature_cols = [
        'distance_3d', 'worker_speed', 'machine_speed', 'relative_speed',
        'direction_worker', 'direction_machine', 'ttc', 'in_restricted_zone',
        'machine_status', 'worker_bpm', 'fatigue_index', 'vibration_rms',
        'acceleration_z', 'gas_co_ppm', 'dust_density_mg_m3', 'ambient_light_lux'
    ]
    
    X = df[feature_cols]
    y = df["risk_level"].astype(int)
    
    # 2. División Train/Test Estratificada (80/20) con Semilla 42
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )
    
    # 3. Definición de las 5 Arquitecturas Oficiales (Ficha 11 / Revistas Q1)
    def build_models():
        rf = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=RANDOM_STATE, n_jobs=-1)
        xgb = XGBClassifier(n_estimators=150, max_depth=6, learning_rate=0.1, eval_metric='mlogloss', random_state=RANDOM_STATE)
        mlp = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=RANDOM_STATE)
        
        stacking = StackingClassifier(
            estimators=[('rf', rf), ('xgb', xgb)],
            final_estimator=LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
            cv=3
        )
        
        voting = VotingClassifier(
            estimators=[('rf', rf), ('xgb', xgb), ('mlp', mlp)],
            voting='soft'
        )
        
        return {
            "RandomForest": rf,
            "XGBoost": xgb,
            "MLP_NeuralNet": mlp,
            "Stacking_Ensemble": stacking,
            "Voting_Ensemble": voting
        }
    
    # 4. K-Fold Estratificado (K=5, random_state=42)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    
    cv_results = {model_name: [] for model_name in build_models().keys()}
    
    print("\n🔄 Ejecutando Stratified 5-Fold CV con SMOTE en Dataset Oficial...")
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(X_train, y_train), 1):
        X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
        y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]
        
        smote = SMOTE(random_state=RANDOM_STATE)
        X_tr_res, y_tr_res = smote.fit_resample(X_tr, y_tr)
        
        scaler = StandardScaler()
        X_tr_scaled = scaler.fit_transform(X_tr_res)
        X_val_scaled = scaler.transform(X_val)
        
        models = build_models()
        
        for model_name, model in models.items():
            model.fit(X_tr_scaled, y_tr_res)
            
            t_start_inf = time.time()
            y_pred = model.predict(X_val_scaled)
            t_end_inf = time.time()
            
            y_proba = model.predict_proba(X_val_scaled)
            
            inf_time_per_sample = ((t_end_inf - t_start_inf) / len(X_val)) * 1000.0
            
            acc = accuracy_score(y_val, y_pred)
            f1_macro = f1_score(y_val, y_pred, average='macro')
            f1_micro = f1_score(y_val, y_pred, average='micro')
            prec_macro = precision_score(y_val, y_pred, average='macro', zero_division=0)
            rec_macro = recall_score(y_val, y_pred, average='macro', zero_division=0)
            auc_roc = roc_auc_score(y_val, y_proba, multi_class='ovr')
            
            cv_results[model_name].append({
                "fold": fold,
                "accuracy": float(acc),
                "f1_macro": float(f1_macro),
                "f1_micro": float(f1_micro),
                "precision_macro": float(prec_macro),
                "recall_macro": float(rec_macro),
                "auc_roc": float(auc_roc),
                "inference_time_ms": float(inf_time_per_sample)
            })
            
    print("\n✅ Resumen de Validación Cruzada (Promedios):")
    for model_name, folds in cv_results.items():
        accs = [f["accuracy"] for f in folds]
        f1s = [f["f1_macro"] for f in folds]
        aucs = [f["auc_roc"] for f in folds]
        print(f"  🏆 {model_name:20s} | Acc: {np.mean(accs):.4f} ± {np.std(accs):.4f} | F1: {np.mean(f1s):.4f} | AUC: {np.mean(aucs):.4f}")
        
    artifact_dir = os.path.join(os.path.dirname(__file__), "..", "app", "ml", "artifacts")
    os.makedirs(artifact_dir, exist_ok=True)
    
    cv_metrics_path = os.path.join(artifact_dir, "cv_metrics_results.json")
    with open(cv_metrics_path, "w", encoding="utf-8") as f:
        json.dump(cv_results, f, indent=2, ensure_ascii=False)
        
    data_dump_path = os.path.join(artifact_dir, "processed_data.joblib")
    joblib.dump({
        "X_train": X_train, "X_test": X_test,
        "y_train": y_train, "y_test": y_test,
        "feature_names": feature_cols
    }, data_dump_path)
    
    return cv_results

if __name__ == "__main__":
    train_and_evaluate_cv()
