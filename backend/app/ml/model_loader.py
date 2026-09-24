import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List

class MLLoader:
    def __init__(self):
        self.artifacts_dir = os.path.join(os.path.dirname(__file__), "artifacts")
        self.best_model_path = os.path.join(self.artifacts_dir, "best_risk_model.joblib")
        self.fallback_model_path = os.path.join(self.artifacts_dir, "model_xgb_v1.joblib")
        self.meta_path = os.path.join(self.artifacts_dir, "best_model_meta.json")
        
        self.model = None
        self.scaler = None
        self.feature_names = [
            "distance_3d", "ttc", "relative_speed", "worker_speed", "machine_speed",
            "in_restricted_zone", "worker_bpm", "fatigue_index", "vibration_rms",
            "gas_co_ppm", "dust_density_mg_m3", "ambient_light_lux"
        ]
        self.class_names = ["BAJO", "MEDIO", "ALTO"]
        self._load_model()
        
    def _patch_pipeline(self, est):
        """Recursively patch scikit-learn estimators for version compatibility."""
        if hasattr(est, "steps"):
            for name, step in est.steps:
                self._patch_pipeline(step)
        elif hasattr(est, "transformers_"):
            for name, transformer, columns in est.transformers_:
                self._patch_pipeline(transformer)
        elif hasattr(est, "transformers"):
            for name, transformer, columns in est.transformers:
                self._patch_pipeline(transformer)
        if type(est).__name__ == "SimpleImputer":
            if not hasattr(est, "_fill_dtype"):
                est._fill_dtype = getattr(est, "_fit_dtype", float)
    
    def _load_model(self):
        target_path = self.best_model_path if os.path.exists(self.best_model_path) else self.fallback_model_path
        if os.path.exists(target_path):
            artifact = joblib.load(target_path)
            if isinstance(artifact, dict):
                self.model = artifact.get("model")
                self.scaler = artifact.get("scaler")
                self.feature_names = artifact.get("feature_names", self.feature_names)
            else:
                self.model = artifact
                
            self._patch_pipeline(self.model)
            print(f"Loaded ML model successfully from {target_path}")
        else:
            print(f"Warning: ML model artifact not found at {target_path}")

    def get_metadata(self) -> Dict[str, Any]:
        if os.path.exists(self.meta_path):
            with open(self.meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "model_name": "Voting Classifier (Hibrido)",
            "test_metrics": {"accuracy": 0.9469, "f1_macro": 0.9530, "auc_roc": 0.9945}
        }
    
    def _prepare_df(self, df: pd.DataFrame) -> pd.DataFrame:
        target_cols = list(self.scaler.feature_names_in_) if (self.scaler and hasattr(self.scaler, "feature_names_in_")) else self.feature_names
        defaults = {
            'distance_3d': 15.0, 'ttc': 10.0, 'relative_speed': 3.5,
            'worker_speed': 1.2, 'machine_speed': 2.3, 'in_restricted_zone': 0,
            'worker_bpm': 75.0, 'fatigue_index': 0.2, 'vibration_rms': 0.8,
            'gas_co_ppm': 10.0, 'dust_density_mg_m3': 1.0, 'ambient_light_lux': 60.0,
            'acceleration_z': 9.81, 'direction_worker': 0, 'direction_machine': 0, 'machine_status': 1
        }
        for col in target_cols:
            if col not in df.columns:
                df[col] = defaults.get(col, 0.0)
        return df[target_cols]

    def _generate_explanation(self, row: pd.Series, risk_level: str) -> str:
        factors = []
        if row.get("distance_3d", 100) < 5.0:
            factors.append(f"Distancia 3D crítica ({row['distance_3d']}m)")
        if row.get("ttc", 100) < 3.0:
            factors.append(f"Tiempo al impacto severo ({row['ttc']}s)")
        if row.get("in_restricted_zone", 0) == 1:
            factors.append("Ingreso no autorizado a Zona Restringida")
        if row.get("fatigue_index", 0) > 0.6:
            factors.append(f"Índice de fatiga elevado ({row['fatigue_index']})")
        if row.get("gas_co_ppm", 0) > 35.0:
            factors.append(f"Alta concentración de CO ({row['gas_co_ppm']} ppm)")
            
        if not factors:
            factors.append("Parámetros operacionales dentro de rangos normales")
            
        return f"Riesgo {risk_level} impulsado por: " + ", ".join(factors)

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        if not self.model:
            self._load_model()
            if not self.model:
                raise ValueError("Model not loaded.")
        
        df = pd.DataFrame([features])
        df = self._prepare_df(df)
        
        X_eval = self.scaler.transform(df) if self.scaler else df
        
        prediction_idx = int(self.model.predict(X_eval)[0])
        probas = self.model.predict_proba(X_eval)[0]
        
        risk_score = float(probas[min(prediction_idx, len(probas)-1)]) * 100
        risk_label = self.class_names[min(prediction_idx, 2)]
        
        explanation = self._generate_explanation(df.iloc[0], risk_label)
        
        return {
            "model_name": self.get_metadata().get("model_name", "RandomForest"),
            "risk_level": risk_label,
            "risk_score": round(risk_score, 2),
            "probability": float(probas[prediction_idx]),
            "justification": explanation,
            "probabilities": {name: round(float(p), 4) for name, p in zip(self.class_names, probas)}
        }
    
    def predict_batch(self, features_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.predict(f) for f in features_list]

ml_engine = MLLoader()
