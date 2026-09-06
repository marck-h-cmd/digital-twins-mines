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
    scenarios = [
        # Escenario 1: Normal / Bajo Riesgo
        {
            "worker_id": 1, "machine_id": 1,
            "worker_x": 0.0, "worker_y": 0.0, "worker_z": 0.0,
            "machine_x": 35.0, "machine_y": 0.0, "machine_z": 0.0,
            "direction_worker": 0, "direction_machine": 0,
            "distance_3d": 35.0, "ttc": 45.0,
            "worker_speed": 0.8, "machine_speed": 2.0, "relative_speed": 2.8,
            "in_restricted_zone": 0, "machine_status": 1,
            "worker_bpm": 76.0, "fatigue_index": 0.15,
            "vibration_rms": 0.8, "acceleration_z": 9.81,
            "gas_co_ppm": 8.0, "dust_density_mg_m3": 0.8, "ambient_light_lux": 80.0
        },
        # Escenario 2: Advertencia (Fatiga + Proximidad Moderada)
        {
            "worker_id": 1, "machine_id": 1,
            "worker_x": 0.0, "worker_y": 0.0, "worker_z": 0.0,
            "machine_x": 12.0, "machine_y": 0.0, "machine_z": 0.0,
            "direction_worker": 1, "direction_machine": 5,
            "distance_3d": 12.0, "ttc": 12.0,
            "worker_speed": 1.2, "machine_speed": 4.0, "relative_speed": 5.2,
            "in_restricted_zone": 1, "machine_status": 1,
            "worker_bpm": 115.0, "fatigue_index": 0.48,
            "vibration_rms": 1.8, "acceleration_z": 9.81,
            "gas_co_ppm": 22.0, "dust_density_mg_m3": 2.1, "ambient_light_lux": 45.0
        },
        # Escenario 3: Riesgo Crítico (Colisión Inminente)
        {
            "worker_id": 1, "machine_id": 1,
            "worker_x": 0.0, "worker_y": 0.0, "worker_z": 0.0,
            "machine_x": 4.0, "machine_y": 0.0, "machine_z": 0.0,
            "direction_worker": 0,
            "direction_machine": 4,
            "distance_3d": 4.0, "ttc": 0.8,
            "worker_speed": 0.5, "machine_speed": 4.5, "relative_speed": 5.0,
            "in_restricted_zone": 1, "machine_status": 1,
            "worker_bpm": 145.0, "fatigue_index": 0.88,
            "vibration_rms": 3.2, "acceleration_z": 9.81,
            "gas_co_ppm": 65.0, "dust_density_mg_m3": 5.5, "ambient_light_lux": 15.0
        }
    ]

    for item in scenarios:
        interaction_in = InteractionCreate(**item)
        features = interaction_in.model_dump()
        result = ml_engine.predict(features)
        await process_prediction(interaction_in, result)
        await asyncio.sleep(2.5)

@router.post("/simulate")
async def trigger_simulation(
    background_tasks: BackgroundTasks,
) -> Any:
    background_tasks.add_task(run_simulation_background)
    return {"message": "Simulación de telemetría de minería iniciada exitosamente"}
