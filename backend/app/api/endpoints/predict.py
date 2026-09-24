from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
import asyncio

from app.api.deps import get_current_user
from app.ml.model_loader import ml_engine
from app.schemas.interaction import InteractionCreate
from app.services.alert_engine import process_prediction

router = APIRouter()

class PredictionResult(BaseModel):
    risk_level: str
    risk_score: float
    probability: Optional[float] = None
    justification: Optional[str] = None
    probabilities: Optional[Dict[str, float]] = None

@router.get("/model/best")
def get_best_model_metadata() -> Any:
    """Retorna la información y metadatos del Modelo Campeón."""
    return ml_engine.get_metadata()

@router.post("/", response_model=PredictionResult)
async def predict_interaction(
    *,
    interaction_in: InteractionCreate,
    current_user = Depends(get_current_user),
) -> Any:
    # 1. Ejecutar inferencia con el modelo campeón
    features = interaction_in.model_dump()
    result = ml_engine.predict(features)
    
    # 2. Procesar alertas e interactuar con el motor de eventos
    await process_prediction(interaction_in, result)
    
    return result

@router.post("/batch", response_model=List[PredictionResult])
async def predict_interactions_batch(
    *,
    interactions_in: List[InteractionCreate],
    current_user = Depends(get_current_user),
) -> Any:
    features_list = [i.model_dump() for i in interactions_in]
    results = ml_engine.predict_batch(features_list)
    
    for interaction, result in zip(interactions_in, results):
        await process_prediction(interaction, result)
        
    return results

async def run_simulation_background():
    scenarios = []
    
    # Caso 1: Aproximación segura (Safe pass)
    for i in range(10):
        scenarios.append({
            "worker_id": 1, "machine_id": 1,
            "worker_x": 0.0, "worker_y": 0.0, "worker_z": 0.0,
            "machine_x": 30.0 - (i * 3.0), "machine_y": 0.0, "machine_z": 5.0, # Pasando por otro carril (z=5)
            "direction_worker": 0, "direction_machine": 4,
            "distance_3d": abs(30.0 - (i * 3.0)), "ttc": 99.0,
            "worker_speed": 0.0, "machine_speed": 4.0, "relative_speed": 4.0,
            "in_restricted_zone": 0, "machine_status": 1,
            "worker_bpm": 75.0 + i, "fatigue_index": 0.1,
            "vibration_rms": 0.5, "acceleration_z": 9.8,
            "gas_co_ppm": 5.0, "dust_density_mg_m3": 0.5, "ambient_light_lux": 80.0
        })

    # Caso 2: Fatiga y ambiente tóxico, máquina estática
    for i in range(8):
        scenarios.append({
            "worker_id": 1, "machine_id": 1,
            "worker_x": 0.0, "worker_y": 0.0, "worker_z": 0.0,
            "machine_x": 15.0, "machine_y": 0.0, "machine_z": 5.0,
            "direction_worker": 0, "direction_machine": 0,
            "distance_3d": 15.0, "ttc": 99.0,
            "worker_speed": 0.0, "machine_speed": 0.0, "relative_speed": 0.0,
            "in_restricted_zone": 1, "machine_status": 0,
            "worker_bpm": 85.0 + (i * 5), "fatigue_index": 0.2 + (i * 0.1),
            "vibration_rms": 0.5, "acceleration_z": 9.8,
            "gas_co_ppm": 10.0 + (i * 8.0), "dust_density_mg_m3": 1.0 + (i * 0.5), "ambient_light_lux": 40.0 - (i * 2)
        })

    # Caso 3: Colisión Inminente
    for i in range(8):
        dist = 25.0 - (i * 3.0)
        scenarios.append({
            "worker_id": 1, "machine_id": 1,
            "worker_x": 0.0, "worker_y": 0.0, "worker_z": 0.0,
            "machine_x": dist, "machine_y": 0.0, "machine_z": 0.0, # Viene directo por el mismo carril (z=0)
            "direction_worker": 0, "direction_machine": 4,
            "distance_3d": dist, "ttc": dist / 4.5 if dist > 0 else 0.1,
            "worker_speed": 0.0, "machine_speed": 4.5, "relative_speed": 4.5,
            "in_restricted_zone": 1, "machine_status": 1,
            "worker_bpm": 120.0 + (i * 4), "fatigue_index": 0.8,
            "vibration_rms": 2.0 + (i * 0.2), "acceleration_z": 9.8,
            "gas_co_ppm": 30.0, "dust_density_mg_m3": 4.0, "ambient_light_lux": 20.0
        })

    for item in scenarios:
        interaction_in = InteractionCreate(**item)
        features = interaction_in.model_dump()
        result = ml_engine.predict(features)
        await process_prediction(interaction_in, result)
        await asyncio.sleep(1.5)

@router.post("/simulate")
async def trigger_simulation(
    background_tasks: BackgroundTasks,
) -> Any:
    background_tasks.add_task(run_simulation_background)
    return {"message": "Simulación de telemetría de minería iniciada exitosamente"}
