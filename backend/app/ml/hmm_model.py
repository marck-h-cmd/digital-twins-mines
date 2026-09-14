import numpy as np
from typing import Dict, Any, List, Tuple

class MiningRiskHMM:
    """
    Modelo de Estado Oculto (Hidden Markov Model - HMM) para la Estimación de Riesgo en Minería Subterránea.
    
    Estados Ocultos Latentes (Hidden States):
      - Estado 0: SEGURO (Operación normal, baja interferencia)
      - Estado 1: INCIPIENTE (Advertencia por acercamiento o aumento de biometría/fatiga)
      - Estado 2: INMINENTE (Peligro crítico de colisión / atropello / gas nocivo)
    """

    def __init__(self, n_states: int = 4):
        self.n_states = n_states
        self.state_labels = {
            0: "NOMINAL_SEGURO",
            1: "RIESGO_INMINENTE_COLISIÓN",
            2: "ALERTA_AMBIENTAL",
            3: "MANIOBRA_INTERMEDIA"
        }
        
        # Matriz de Transición de Estados A (4x4) aprendida con Baum-Welch
        self.transition_matrix = np.array([
            [0.9716, 0.0000, 0.0029, 0.0255],  # Desde NOMINAL_SEGURO
            [0.0000, 0.9317, 0.0000, 0.0683],  # Desde RIESGO_INMINENTE_COLISIÓN
            [0.0192, 0.0000, 0.9808, 0.0000],  # Desde ALERTA_AMBIENTAL
            [0.0877, 0.0833, 0.0000, 0.8290]   # Desde MANIOBRA_INTERMEDIA
        ])
        
        # Distribución de Probabilidad Inicial pi
        self.initial_distribution = np.array([0.50, 0.10, 0.20, 0.20])
        
        # Medias de Emisión por Estado (Vector: [distance_3d, ttc, worker_bpm, fatigue_index, gas_co_ppm])
        self.means = np.array([
            [44.66, 14.66, 76.42, 0.107,  9.13],  # Estado 0: NOMINAL_SEGURO (44.66m)
            [12.14,  2.26, 82.96, 0.087,  9.10],  # Estado 1: RIESGO_INMINENTE_COLISIÓN (12.14m)
            [34.99, 10.99, 76.55, 0.092, 20.27],  # Estado 2: ALERTA_AMBIENTAL (Gas CO 20.27 ppm)
            [31.48,  9.76, 78.78, 0.096,  9.08]   # Estado 3: MANIOBRA_INTERMEDIA (31.48m)
        ])
        
        self.stds = np.array([
            [8.0, 3.5, 6.0, 0.03, 3.0],
            [3.0, 1.2, 8.0, 0.03, 3.0],
            [6.0, 2.5, 6.0, 0.03, 8.0],
            [5.0, 2.0, 6.0, 0.03, 3.0]
        ])

    def _emission_probability(self, obs: np.ndarray, state: int) -> float:
        """Calcula la verosimilitud de la observación dado un estado latente bajo distribución Gaussiana Multivariada independiente."""
        mean = self.means[state]
        std = self.stds[state]
        std = np.maximum(std, 1e-4)
        prob = np.exp(-0.5 * ((obs - mean) / std) ** 2) / (np.sqrt(2 * np.pi) * std)
        return float(np.prod(prob))

    def estimate_hidden_state(self, telemetry: Dict[str, Any], prev_state_probs: np.ndarray = None) -> Dict[str, Any]:
        """
        Inferencia de Bayes / Algoritmo Forward en tiempo real para obtener el estado oculto actual.
        """
        dist = float(telemetry.get('distance_3d', 30.0))
        ttc = float(telemetry.get('ttc', 10.0))
        bpm = float(telemetry.get('worker_bpm', 80.0))
        fatigue = float(telemetry.get('fatigue_index', 0.1))
        gas = float(telemetry.get('gas_co_ppm', 9.0))
        
        obs = np.array([dist, ttc, bpm, fatigue, gas])

        if prev_state_probs is None:
            prior = self.initial_distribution
        else:
            prior = np.dot(prev_state_probs, self.transition_matrix)

        likelihoods = np.zeros(self.n_states)
        for s in range(self.n_states):
            likelihoods[s] = prior[s] * self._emission_probability(obs, s)

        total = np.sum(likelihoods)
        if total > 0:
            posterior = likelihoods / total
        else:
            posterior = prior

        current_state = int(np.argmax(posterior))

        return {
            "hidden_state_id": current_state,
            "hidden_state_name": self.state_labels[current_state],
            "state_probabilities": {
                name: round(float(posterior[idx]), 4)
                for idx, name in self.state_labels.items()
            }
        }

hmm_engine = MiningRiskHMM()
