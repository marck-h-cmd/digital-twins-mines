from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
import asyncio
import math
import random

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
    # Semilla aleatoria del escenario: 50% de probabilidad de colisión
    es_colision = random.choice([True, False])
    
    # Condiciones iniciales de la Cinemática
    worker_x, worker_z = 0.0, 0.0
    machine_x = 40.0
    # Si NO es colisión, la grúa pasa por un carril seguro (z = 6.0)
    # Si ES colisión, la grúa viene por el mismo carril o muy cerca (z = 0.0 a 1.0)
    machine_z = random.uniform(0.0, 1.0) if es_colision else random.uniform(5.5, 7.0)
    
    machine_speed = random.uniform(3.0, 5.0)
    
    # Valores base de telemetría para el inicio
    base_bpm = random.uniform(70.0, 85.0)
    base_gas = random.uniform(2.0, 10.0)
    base_fatigue = random.uniform(0.1, 0.25)

    # El botón de simulación del Frontend asume unos 40 segundos, 
    # por ende a 1.5s por paso son aproximadamente 26 pasos.
    for i in range(26):
        # 1. Aplicar "Jitter" estocástico (ruido orgánico) a los sensores
        bpm = base_bpm + random.uniform(-4, 4)
        gas = base_gas + random.uniform(-1.5, 2.0)
        fatigue = base_fatigue + random.uniform(-0.02, 0.04)
        
        # Lógica de estrés orgánico:
        # Si es colisión y la grúa está cerca (< 20m), el trabajador entra en pánico gradualmente
        if es_colision and machine_x < 20.0:
            base_bpm += random.uniform(1.0, 4.0)
            base_fatigue += random.uniform(0.01, 0.05)
            base_gas += random.uniform(0.5, 2.5)
            
        # Limitar valores a rangos realistas
        bpm = min(max(bpm, 60.0), 160.0)
        gas = min(max(gas, 0.0), 150.0)
        fatigue = min(max(fatigue, 0.0), 1.0)
        
        # 2. Cinemática (Movimiento lineal)
        # La grúa se mueve hacia el origen (x=0) a una velocidad constante
        # Como deltaT es 1.5s, Desplazamiento = v * 1.5
        delta_t = 1.5
        machine_x -= (machine_speed * delta_t)
        
        # Pequeño drift aleatorio en Z (tambaleo del trabajador y de la máquina por terreno irregular)
        worker_z += random.uniform(-0.3, 0.3)
        machine_z += random.uniform(-0.1, 0.1)
        
        # 3. Calcular distancia real con Teorema de Pitágoras (3D proyectado a 2D)
        dist_3d = math.sqrt((machine_x - worker_x)**2 + (machine_z - worker_z)**2)
        
        # Time to Collision (TTC) basado en distancia y velocidad
        ttc = dist_3d / machine_speed if machine_speed > 0 else 99.0

        # Crear el DTO
        interaction_in = InteractionCreate(
            worker_id=1, 
            machine_id=1,
            worker_x=worker_x, worker_y=0.0, worker_z=worker_z,
            machine_x=machine_x, machine_y=0.0, machine_z=machine_z,
            direction_worker=0, 
            direction_machine=4, # Acercándose
            distance_3d=dist_3d, 
            ttc=ttc,
            worker_speed=0.0, 
            machine_speed=machine_speed, 
            relative_speed=machine_speed,
            in_restricted_zone=1 if dist_3d < 12 else 0, 
            machine_status=1,
            worker_bpm=bpm, 
            fatigue_index=fatigue,
            vibration_rms=random.uniform(0.3, 1.8) + (2.0 if (es_colision and dist_3d < 10) else 0.0), 
            acceleration_z=9.8,
            gas_co_ppm=gas, 
            dust_density_mg_m3=random.uniform(0.5, 3.5), 
            ambient_light_lux=random.uniform(35.0, 45.0)
        )
        
        # Ejecutar inferencia e inyectar al Websocket
        features = interaction_in.model_dump()
        result = ml_engine.predict(features)
        await process_prediction(interaction_in, result)
        
        # Esperar 1.5 segundos para la siguiente iteración
        await asyncio.sleep(delta_t)

@router.post("/simulate")
async def trigger_simulation(
    background_tasks: BackgroundTasks,
) -> Any:
    background_tasks.add_task(run_simulation_background)
    return {"message": "Simulación de telemetría de minería iniciada exitosamente"}
