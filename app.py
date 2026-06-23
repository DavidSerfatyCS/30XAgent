"""
Agente de Onboarding 30X - interfaz conversacional.

- RF-01 (grounding): responde solo desde knowledge_base.md via system prompt.
- RF-02 (memoria): Gradio pasa el historial de la sesion en cada turno; se reenvia al modelo.
- RF-03 (escalado): regla en el system prompt.
- RF-04 (interfaz): chat web usable por un no-tecnico, sin instrucciones.

Guardrails (deploy publico con key propia -> protegen el gasto y evitan abuso):
- Tope de longitud de entrada (MAX_INPUT_CHARS).
- Rate limit por IP/sesion (RATE_LIMIT_MAX por RATE_LIMIT_WINDOW_SEC); degrada a global si no hay IP.
- max_tokens acota el costo de salida por llamada.

Config por variables de entorno (ver .env.example):
- ANTHROPIC_API_KEY     : credencial del modelo (NUNCA se commitea).
- MODEL                 : id del modelo. Default: Claude Haiku.
- PORT                  : puerto del servidor. Default 7860.
- MAX_INPUT_CHARS       : tope de caracteres por mensaje. Default 2000.
- RATE_LIMIT_MAX        : consultas permitidas por ventana. Default 15.
- RATE_LIMIT_WINDOW_SEC : ventana del rate limit en segundos. Default 300.
"""

from __future__ import annotations

import base64
import os
import time
from collections import defaultdict, deque
from pathlib import Path

# Carga un archivo .env si existe y si python-dotenv esta instalado (opcional).
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

import gradio as gr

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 1024

MAX_INPUT_CHARS = int(os.environ.get("MAX_INPUT_CHARS", "2000"))
RATE_LIMIT_MAX = int(os.environ.get("RATE_LIMIT_MAX", "15"))
RATE_LIMIT_WINDOW_SEC = int(os.environ.get("RATE_LIMIT_WINDOW_SEC", "300"))

# --- Carga de la base de conocimiento y el system prompt (la "KB" del agente) ---
SYSTEM_PROMPT = (BASE_DIR / "system_prompt.md").read_text(encoding="utf-8")
KNOWLEDGE_BASE = (BASE_DIR / "knowledge_base.md").read_text(encoding="utf-8")

SYSTEM = (
    f"{SYSTEM_PROMPT}\n\n"
    "===== BASE DE CONOCIMIENTO (unica fuente de verdad) =====\n"
    f"{KNOWLEDGE_BASE}"
)

_client = None
_request_log: dict[str, deque] = defaultdict(deque)


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


def _rate_limited(key: str) -> bool:
    """True si 'key' ya supero RATE_LIMIT_MAX consultas en la ventana (sliding window)."""
    now = time.time()
    dq = _request_log[key]
    while dq and now - dq[0] > RATE_LIMIT_WINDOW_SEC:
        dq.popleft()
    if len(dq) >= RATE_LIMIT_MAX:
        return True
    dq.append(now)
    return False


def _client_key(request: gr.Request | None) -> str:
    """Clave para el rate limit: IP del cliente si esta disponible, si no la sesion, si no global."""
    if request is not None:
        host = getattr(getattr(request, "client", None), "host", None)
        if host:
            return host
        sh = getattr(request, "session_hash", None)
        if sh:
            return sh
    return "global"


def respond(message, history, request: gr.Request = None):
    """
    message: texto del usuario en este turno.
    history: lista de dicts {'role', 'content'} de la sesion = memoria (RF-02).
    request: lo inyecta Gradio si esta disponible; se usa para el rate limit por IP.
    """
    if not message or not message.strip():
        return "Escribi tu pregunta sobre 30X y te respondo con los documentos de onboarding."

    if len(message) > MAX_INPUT_CHARS:
        return (
            f"Tu mensaje es muy largo (maximo {MAX_INPUT_CHARS} caracteres). "
            "Resumi tu pregunta sobre 30X y te respondo."
        )

    if _rate_limited(_client_key(request)):
        return (
            "Recibi muchas consultas en poco tiempo. Espera un momento e intenta de nuevo. "
            "(Limite para proteger el servicio.)"
        )

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


# ============================================================================
# Interfaz (UI). SOLO presentacion: no cambia respond(), la memoria ni los
# guardrails. El gr.ChatInterface sigue manejando el chat y la memoria de
# sesion; se embebe dentro de un gr.Blocks que aporta el branding 30X.
# Paleta integrada (negro + lima): se sobreescriben las variables CSS de
# Gradio para que todos los componentes (chat, tarjetas, historial) compartan
# el mismo fondo oscuro y el azul por defecto desaparezca. El CSS va como
# <style> (robusto en HF Spaces, sin depender de quien llame a launch()).
# ============================================================================

HEADER_TITLE = "Agente de Onboarding"

EXAMPLES = [
    "¿Qué es 30X y quiénes lo fundaron?",
    "¿Qué herramientas usa el equipo y para qué sirve cada una?",
    "Acabo de entrar, ¿qué se espera de mí esta primera semana?",
    "¿Cómo funciona una cohorte online de principio a fin?",
    "¿A quién le escribo si tengo un bloqueo técnico?",
]

ACCENT = "#c6f432"


def _logo_data_uri() -> str:
    """Logo 30X como data URI; si falta el archivo, la UI igual carga."""
    try:
        raw = (BASE_DIR / "logo.jpeg").read_bytes()
        return "data:image/jpeg;base64," + base64.b64encode(raw).decode()
    except Exception:  # noqa: BLE001
        return ""


LOGO_URI = _logo_data_uri()
LOGO_PATH = str(BASE_DIR / "logo.jpeg") if LOGO_URI else None

CSS = """
:root {
  --ob-bg:#0a0a0a; --ob-panel:#161616; --ob-border:#262626;
  --ob-acc:__ACCENT__; --ob-text:#f0f0f0; --ob-muted:#a3a3a3;
}

/* Paleta integrada: pisa las variables de Gradio para que nada quede azul
   y todo comparta el fondo oscuro con acento lima. */
gradio-app, .gradio-container, .dark {
  --background-fill-primary:#0a0a0a !important;
  --background-fill-secondary:#121212 !important;
  --body-background-fill:#0a0a0a !important;
  --block-background-fill:#121212 !important;
  --panel-background-fill:#121212 !important;
  --border-color-primary:#262626 !important;
  --border-color-accent:#2c2c2c !important;
  --input-background-fill:#141414 !important;
  --input-background-fill-focus:#171717 !important;
  --color-accent:__ACCENT__ !important;
  --color-accent-soft:#1d1f17 !important;
  --button-primary-background-fill:__ACCENT__ !important;
  --button-primary-background-fill-hover:#b6e62f !important;
  --button-primary-text-color:#000 !important;
}

gradio-app, .gradio-container {
  background:var(--ob-bg) !important; color:var(--ob-text) !important;
  max-width:100% !important; padding:0 !important; font-size:16px !important;
}
footer { display:none !important; }

#ob-topbar {
  display:flex; align-items:center; justify-content:flex-start;
  padding:16px 28px; border-bottom:1px solid var(--ob-border); background:#000;
}
#ob-topbar .ob-brand { display:flex; align-items:center; gap:16px; }
#ob-topbar img.ob-logo { height:40px; display:block; }
#ob-topbar span.ob-logo { font-weight:800; font-size:30px; letter-spacing:1px; }
#ob-topbar span.ob-logo b { color:var(--ob-acc); }
#ob-topbar .ob-title {
  font-size:19px; font-weight:600; color:var(--ob-text); letter-spacing:.3px;
  padding-left:16px; border-left:1px solid var(--ob-border);
}

#ob-main { max-width:960px; margin:0 auto; padding:22px 20px 40px; }

.ob-welcome {
  background:var(--ob-panel); border:1px solid var(--ob-border);
  border-radius:16px; padding:24px 26px; margin:6px 0 14px;
}
.ob-welcome h2 { margin:0 0 8px; font-size:25px; font-weight:700; color:var(--ob-text); }
.ob-welcome p { margin:6px 0; font-size:16px; color:#e2e2e2; }
.ob-welcome ul { list-style:none; padding:0; margin:14px 0 4px; }
.ob-welcome li {
  padding:6px 0 6px 28px; position:relative; font-size:16px; font-weight:500; color:#e2e2e2;
}
.ob-welcome li::before {
  content:"✓"; color:var(--ob-acc); position:absolute; left:0; font-weight:800; font-size:17px;
}
.ob-welcome .ob-muted { color:var(--ob-muted); font-size:14.5px; margin-top:12px; }

/* Texto del chat un poco mas grande y vivo (selectores conservadores) */
#ob-main .message, #ob-main .bubble, #ob-main .message-row,
#ob-main [data-testid="bot"], #ob-main [data-testid="user"] {
  font-size:15.5px !important; line-height:1.6 !important;
}

#ob-main textarea, #ob-main input[type=text] {
  color:var(--ob-text) !important; border-radius:12px !important; font-size:15.5px !important;
}
#ob-main button.primary, #ob-main .primary {
  background:var(--ob-acc) !important; color:#000 !important;
  border:none !important; font-weight:600 !important;
}
#ob-main .examples button, #ob-main .example {
  background:var(--ob-panel) !important; border:1px solid var(--ob-border) !important;
  color:var(--ob-text) !important; border-radius:14px !important; text-align:left !important;
  font-size:15px !important; font-weight:500 !important;
}
#ob-main .examples button:hover, #ob-main .example:hover {
  border-color:var(--ob-acc) !important;
}

#ob-footer {
  text-align:center; color:var(--ob-muted); font-size:13px;
  padding:18px; border-top:1px solid var(--ob-border);
}
#ob-footer b { color:var(--ob-text); }
""".replace("__ACCENT__", ACCENT)

if LOGO_URI:
    _brand_inner = f'<img class="ob-logo" src="{LOGO_URI}" alt="30X">'
else:
    _brand_inner = '<span class="ob-logo">30<b>X</b></span>'
TOPBAR = (
    '<div id="ob-topbar"><div class="ob-brand">'
    f"{_brand_inner}"
    f'<span class="ob-title">{HEADER_TITLE}</span>'
    "</div></div>"
)

WELCOME = (
    '<div class="ob-welcome">'
    "<h2>Bienvenido al equipo de 30X \U0001f44b</h2>"
    "<p>Soy tu agente de onboarding. Te ayudo a entender cómo funciona 30X desde el día uno:</p>"
    "<ul>"
    "<li>La organización y cómo trabajamos.</li>"
    "<li>Las herramientas que usás cada día.</li>"
    "<li>Los programas y qué esperar en tu primera semana.</li>"
    "</ul>"
    '<p class="ob-muted">Probá una de las preguntas frecuentes o escribime lo que necesites.</p>'
    "</div>"
)

FOOTER = (
    '<div id="ob-footer"><b>30X</b> · onboarding interno · '
    "responde solo con documentos internos</div>"
)

THEME = gr.themes.Base(
    primary_hue=gr.themes.colors.lime,
    secondary_hue=gr.themes.colors.gray,
    neutral_hue=gr.themes.colors.gray,
)

with gr.Blocks(title="Agente de Onboarding 30X") as demo:
    gr.HTML(f"<style>{CSS}</style>")
    gr.HTML(TOPBAR)
    with gr.Column(elem_id="ob-main"):
        gr.HTML(WELCOME)
        chatbot = gr.Chatbot(
            height=460,
            show_label=False,
            avatar_images=(None, LOGO_PATH),
        )
        gr.ChatInterface(
            fn=respond,
            chatbot=chatbot,
            examples=EXAMPLES,
            save_history=True,
            autofocus=False,
        )
    gr.HTML(FOOTER)

if __name__ == "__main__":
    # server_name 0.0.0.0 + PORT por env => corre en local y en hosts como Render.
    # theme/css van en launch() (Gradio 6 los movio ahi); el CSS ademas va como
    # <style> arriba, asi el branding no depende de quien llame a launch().
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
        theme=THEME,
        css=CSS,
    )
