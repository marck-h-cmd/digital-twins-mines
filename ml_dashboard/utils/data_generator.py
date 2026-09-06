import numpy as np
import pandas as pd

def generate_mining_telemetry_dataset(n_samples=1000, random_state=42):
    """
    Genera un dataset sintético realista de telemetría de minería subterránea
    para la predicción del riesgo de interacción hombre-máquina (Sistema M-11).
    """
    np.random.seed(random_state)
    
    # 1. Variables de Posicionamiento y Proximidad
    distance_3d = np.random.exponential(scale=15.0, size=n_samples) + 1.0  # 1.0m a 60m+
    distance_3d = np.clip(distance_3d, 0.5, 50.0)
    
    worker_speed = np.random.normal(loc=1.2, scale=0.4, size=n_samples)
    worker_speed = np.clip(worker_speed, 0.0, 3.5)
    
    machine_speed = np.random.normal(loc=3.5, scale=1.2, size=n_samples)
    machine_speed = np.clip(machine_speed, 0.0, 10.0)
    
    relative_speed = worker_speed + machine_speed + np.random.normal(0, 0.3, size=n_samples)
    relative_speed = np.clip(relative_speed, 0.1, 13.0)
    
    # Tiempo al impacto (TTC) = Distancia / Velocidad Relativa
    ttc = distance_3d / np.maximum(relative_speed, 0.1)
    ttc = np.clip(ttc, 0.2, 60.0)
    
    in_restricted_zone = np.random.binomial(n=1, p=0.25, size=n_samples)
    
    # 2. Biometría del Trabajador
    fatigue_index = np.random.beta(a=2, b=5, size=n_samples)  # sesgado hacia valores bajos-medios
    worker_bpm = 60 + fatigue_index * 60 + np.random.normal(0, 8, size=n_samples)
    worker_bpm = np.clip(worker_bpm, 55, 175)
    
    # 3. Condiciones Ambientales
    gas_co_ppm = np.random.exponential(scale=12.0, size=n_samples)
    gas_co_ppm = np.clip(gas_co_ppm, 0.0, 120.0)
    
    dust_density_mg_m3 = np.random.exponential(scale=1.5, size=n_samples)
    dust_density_mg_m3 = np.clip(dust_density_mg_m3, 0.1, 10.0)
    
    ambient_light_lux = np.random.normal(loc=65.0, scale=25.0, size=n_samples)
    ambient_light_lux = np.clip(ambient_light_lux, 5.0, 150.0)
    
    vibration_rms = np.random.exponential(scale=1.0, size=n_samples)
    
    # 4. Cálculo del Riesgo (Fórmula de Riesgo Basada en Física y Fisiología)
    risk_score = (
        (15.0 / np.maximum(distance_3d, 0.5)) * 2.5 +
        (10.0 / np.maximum(ttc, 0.2)) * 3.0 +
        in_restricted_zone * 4.0 +
        fatigue_index * 3.5 +
        (gas_co_ppm / 30.0) * 1.5 +
        (dust_density_mg_m3 / 3.0) * 1.0 -
        (ambient_light_lux / 100.0) * 0.8 +
        np.random.normal(0, 1.2, size=n_samples)
    )
    
    # Clasificación en 3 Niveles: 0: Bajo, 1: Medio, 2: Alto
    p33, p75 = np.percentile(risk_score, [45, 78])
    risk_level = np.zeros(n_samples, dtype=int)
    risk_level[risk_score >= p33] = 1
    risk_level[risk_score >= p75] = 2
    
    df = pd.DataFrame({
        "distance_3d": np.round(distance_3d, 2),
        "ttc": np.round(ttc, 2),
        "relative_speed": np.round(relative_speed, 2),
        "worker_speed": np.round(worker_speed, 2),
        "machine_speed": np.round(machine_speed, 2),
        "in_restricted_zone": in_restricted_zone,
        "worker_bpm": np.round(worker_bpm, 1),
        "fatigue_index": np.round(fatigue_index, 2),
        "vibration_rms": np.round(vibration_rms, 2),
        "gas_co_ppm": np.round(gas_co_ppm, 1),
        "dust_density_mg_m3": np.round(dust_density_mg_m3, 2),
        "ambient_light_lux": np.round(ambient_light_lux, 1),
        "risk_level": risk_level
    })
    
    return df

if __name__ == "__main__":
    df = generate_mining_telemetry_dataset()
    print(f"Dataset generado exitosamente: {df.shape}")
    print(df["risk_level"].value_counts())
