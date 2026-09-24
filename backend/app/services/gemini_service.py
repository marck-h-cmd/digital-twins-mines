import os
import logging
from dotenv import load_dotenv
from app.core.config import settings

# LangChain Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)

# Modelos actuales de Google Gemini en LangChain
PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest"
]

class GeminiService:
    """Motor de Inteligencia Artificial para el sistema M-11 impulsado por LangChain."""

    def __init__(self):
        self._cached_key = None
        self._llm = None
        self._chat_chain = None
        self._alert_chain = None

        # Plantilla de Prompt para Chat conversacional con el operador
        self.chat_prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "Eres M-11 AI, un asistente de inteligencia artificial experto en seguridad y prevención de riesgos en minería subterránea. "
                "Responde de forma clara, técnica, precisa y concisa a las consultas de los operadores mineros, "
                "haciendo énfasis en protocolos de seguridad operacional, monitoreo de gases tóxicos/asfixiantes (CO, NO2, CH4, O2), fatiga del personal, "
                "zonas de exclusión de maquinaria pesada y respuesta a emergencias. Responde en el mismo idioma en que te hablen."
            )),
            ("human", "{user_message}")
        ])

        # Plantilla de Prompt para Análisis de Alertas operacionales
        self.alert_prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un experto en seguridad minera subterránea. Responde estrictamente en formato Markdown bien estructurado."),
            ("human", (
                "Analiza la siguiente alerta registrada por el sistema M-11:\n\n"
                "- **Nivel de Riesgo**: {alert_level}\n"
                "- **Mensaje Original**: {message}\n"
                "- **Fecha y Hora**: {created_at}\n\n"
                "Responde en formato Markdown con las siguientes secciones:\n"
                "## Evaluación de la situación\n"
                "## Causas probables\n"
                "## Acciones inmediatas recomendadas\n"
                "## Medidas preventivas a largo plazo"
            ))
        ])

    def _get_api_key(self) -> str:
        load_dotenv(override=False)
        return (os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY or "").strip()

    def _get_llm_with_fallbacks(self):
        api_key = self._get_api_key()
        if not api_key:
            return None

        if self._llm is None or self._cached_key != api_key:
            try:
                primary = ChatGoogleGenerativeAI(
                    model=PRIMARY_MODEL,
                    google_api_key=api_key,
                    temperature=0.7
                )
                fallbacks = [
                    ChatGoogleGenerativeAI(
                        model=m,
                        google_api_key=api_key,
                        temperature=0.7
                    ) for m in FALLBACK_MODELS
                ]
                self._llm = primary.with_fallbacks(fallbacks)
                self._cached_key = api_key

                # Compilar cadenas ejecutables de LangChain (LCEL)
                self._chat_chain = self.chat_prompt | self._llm | StrOutputParser()
                self._alert_chain = self.alert_prompt | self._llm | StrOutputParser()
            except Exception as e:
                logger.error(f"Error initializing LangChain LLM: {e}")
                self._llm = None
        return self._llm

    def _format_error(self, e: Exception) -> str:
        msg = str(e)
        if "402" in msg or "prepayment" in msg.lower() or "credits are depleted" in msg.lower():
            return (
                "⚠️ **Créditos agotados en Google AI Studio (Error 402)**\n\n"
                "Los créditos prepagados del proyecto asociado a tu API Key se han agotado.\n\n"
                "**Soluciones:**\n"
                "1. **Recargar créditos**: Ve a [AI Studio Projects](https://ai.studio/projects) para recargar saldo.\n"
                "2. **Usar un proyecto con cuota gratuita**: Crea un nuevo proyecto en [Google AI Studio](https://aistudio.google.com/app/apikey), genera una API Key gratuita y actualízala en `backend/.env`."
            )
        if "400" in msg or "API_KEY_INVALID" in msg or "API key not valid" in msg:
            return (
                "⚠️ **Clave de Gemini API no válida o revocada (Error 400)**\n\n"
                "Google rechazó la API Key configurada (`API_KEY_INVALID`).\n\n"
                "**Pasos para solucionarlo:**\n"
                "1. Ve a [Google AI Studio](https://aistudio.google.com/app/apikey) y genera una clave.\n"
                "2. Pégala en el archivo `backend/.env`:\n"
                "   ```env\n"
                "   GEMINI_API_KEY=tu_api_key_aqui\n"
                "   ```\n"
                "3. Vuelve a enviar tu mensaje aquí."
            )
        if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower():
            return "⚠️ **Límite de solicitudes alcanzado (429)**: Se ha superado temporalmente la cuota de la API de Gemini. Espera unos momentos antes de volver a consultar."
        return f"⚠️ Error en LangChain / Gemini: {msg}"

    async def analyze_alert(self, alert_data: dict) -> str:
        """Analiza una alerta operacional usando LangChain LCEL."""
        llm = self._get_llm_with_fallbacks()
        if not llm or not self._alert_chain:
            return (
                "⚠️ **Análisis no disponible**: No se ha configurado `GEMINI_API_KEY` en el archivo `backend/.env`.\n"
                "Obtén una clave en [Google AI Studio](https://aistudio.google.com/app/apikey)."
            )

        try:
            response = await self._alert_chain.ainvoke({
                "alert_level": alert_data.get("alert_level", "UNKNOWN"),
                "message": alert_data.get("message", "Sin descripción"),
                "created_at": str(alert_data.get("created_at", "N/A"))
            })
            return response
        except Exception as e:
            logger.error(f"Error in LangChain analyze_alert: {e}")
            return self._format_error(e)

    async def chat(self, user_message: str) -> str:
        """Procesa una consulta del operador a través de la cadena LangChain."""
        llm = self._get_llm_with_fallbacks()
        if not llm or not self._chat_chain:
            return (
                "⚠️ **Asistente no disponible**\n\n"
                "No se ha configurado la variable `GEMINI_API_KEY` en el archivo `backend/.env`.\n\n"
                "Para activarlo:\n"
                "1. Genera una API Key en [Google AI Studio](https://aistudio.google.com/app/apikey).\n"
                "2. Agrégala en `backend/.env`:\n"
                "   ```env\n"
                "   GEMINI_API_KEY=tu_api_key_aqui\n"
                "   ```"
            )

        try:
            response = await self._chat_chain.ainvoke({
                "user_message": user_message
            })
            return response
        except Exception as e:
            logger.error(f"Error in LangChain chat: {e}")
            return self._format_error(e)

gemini_service = GeminiService()
