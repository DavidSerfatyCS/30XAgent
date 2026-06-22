"""
Agente de Onboarding 30X - interfaz conversacional.

- RF-01 (grounding): responde solo desde knowledge_base.md via system prompt.
- RF-02 (memoria): Gradio pasa el historial de la sesion en cada turno; se reenvia al modelo.
- RF-03 (escalado): regla en el system prompt.
- RF-04 (interfaz): chat web usable por un no-tecnico, sin instrucciones.

Config por variables de entorno (ver .env.example):
- ANTHROPIC_API_KEY : credencial del modelo (NUNCA se commitea).
- MODEL             : id del modelo. Default: Claude Haiku (barato, suficiente).
- PORT              : puerto del servidor (lo setean hosts como Render). Default 7860.
"""

import os
from pathlib import Path

# Carga un archivo .env si existe y si python-dotenv esta instalado (opcional).
# Si no esta, no pasa nada: la key se toma igual de las variables de entorno del sistema.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

import gradio as gr

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 1024

# --- Carga de la base de conocimiento y el system prompt (la "KB" del agente) ---
SYSTEM_PROMPT = (BASE_DIR / "system_prompt.md").read_text(encoding="utf-8")
KNOWLEDGE_BASE = (BASE_DIR / "knowledge_base.md").read_text(encoding="utf-8")

SYSTEM = (
    f"{SYSTEM_PROMPT}\n\n"
    "===== BASE DE CONOCIMIENTO (unica fuente de verdad) =====\n"
    f"{KNOWLEDGE_BASE}"
)

_client = None


def get_client():
    """Crea el cliente Anthropic de forma perezosa (solo cuando se necesita)."""
    global _client
    if _client is None:
        from anthropic import Anthropic  # import perezoso para poder testear sin la lib

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Falta ANTHROPIC_API_KEY. Copia .env.example a .env y pone tu key, "
                "o exporta la variable de entorno."
            )
        _client = Anthropic(api_key=api_key)
    return _client


def respond(message, history):
    """
    message: texto del usuario en este turno.
    history: lista de dicts {'role', 'content'} de la sesion = memoria (RF-02).
    """
    if not message or not message.strip():
        return "Escribi tu pregunta sobre 30X y te respondo con los documentos de onboarding."

    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    messages.append({"role": "user", "content": message})

    model = os.environ.get("MODEL", DEFAULT_MODEL)
    try:
        client = get_client()
        resp = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            system=SYSTEM,
            messages=messages,
        )
        return resp.content[0].text
    except Exception as exc:  # noqa: BLE001 - el usuario no debe ver un stacktrace (RF-04)
        print(f"[error] fallo al llamar al modelo: {exc}")
        return (
            "Tuve un problema tecnico para responder ahora. Proba de nuevo en unos segundos. "
            "Si el problema persiste, avisa al equipo tecnico de 30X."
        )


demo = gr.ChatInterface(
    fn=respond,
    type="messages",
    title="Agente de Onboarding 30X",
    description=(
        "Preguntá sobre 30X: qué es, el equipo, las herramientas, los programas y tu "
        "primera semana. Responde solo con los documentos internos de onboarding."
    ),
    examples=[
        "¿Qué es 30X y quiénes lo fundaron?",
        "¿Qué herramientas usa el equipo y para qué sirve cada una?",
        "Acabo de entrar, ¿qué se espera de mí esta primera semana?",
        "¿Cómo funciona una cohorte online de principio a fin?",
        "¿A quién le escribo si tengo un bloqueo técnico?",
    ],
)

if __name__ == "__main__":
    # server_name 0.0.0.0 + PORT por env => corre en local y en hosts como Render.
    # (Hugging Face Spaces ejecuta la app sola; estos valores no le molestan.)
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
    )
