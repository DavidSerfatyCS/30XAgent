"""
Test de plumbing del agente, SIN API key ni red.

Verifica las tres cosas que importan del cableado:
- RF-02: el historial de la sesión viaja al modelo (memoria).
- RF-01: la base de conocimiento se inyecta en el `system` (fuente de verdad).
- El modelo por defecto es Haiku (configurable por env var MODEL).

Stubea `gradio` (para no instalar la lib) y el cliente Anthropic (para no necesitar key).
Correr desde la raíz del proyecto:  python tests/test_memory.py
"""

import sys
import types
from pathlib import Path

# --- Stub mínimo de gradio: solo necesitamos que `import gradio` no falle ---
# Cubre los componentes de layout que usa la UI (Blocks/Column/HTML/Chatbot/themes)
# para que `import app` funcione sin instalar gradio. NO testea la UI; solo evita
# que el import explote. Las aserciones del test no dependen de esto.
_g = types.ModuleType("gradio")


class _Ctx:
    """No-op que sirve como componente y como context manager (Blocks/Column)."""

    def __init__(self, *a, **k):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _ChatInterface:
    def __init__(self, fn, **kw):
        self.fn = fn

    def launch(self, *a, **k):
        pass


_g.ChatInterface = _ChatInterface
_g.Blocks = _Ctx
_g.Row = _Ctx
_g.Column = _Ctx
_g.HTML = _Ctx
_g.Chatbot = _Ctx
_g.themes = types.SimpleNamespace(
    Base=lambda *a, **k: _Ctx(),
    colors=types.SimpleNamespace(lime="lime", gray="gray"),
)
sys.modules["gradio"] = _g

# Importar app desde la raíz del proyecto (carpeta padre de tests/)
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import app  # noqa: E402

# --- Stub del cliente Anthropic: captura lo enviado y devuelve algo fijo ---
captured = {}


class _Content:
    def __init__(self, text):
        self.text = text


class _Resp:
    content = [_Content("respuesta-de-prueba")]


class _Msgs:
    def create(self, **kw):
        captured.update(kw)
        return _Resp()


class _Client:
    messages = _Msgs()


app.get_client = lambda: _Client()


def run():
    history = [
        {"role": "user", "content": "Soy del área comercial"},
        {"role": "assistant", "content": "Anotado, sos de comercial."},
    ]
    out = app.respond("¿qué herramientas uso?", history)

    msgs = captured["messages"]
    assert out == "respuesta-de-prueba", out
    assert msgs[0]["content"] == "Soy del área comercial", "no reenvió la memoria (RF-02)"
    assert msgs[-1]["content"] == "¿qué herramientas uso?", "no agregó el turno actual"
    assert "BASE DE CONOCIMIENTO" in captured["system"], "la KB no va en el system (RF-01)"
    assert "Chief of Staff" in captured["system"], "falta contenido de la KB"
    assert "haiku" in captured["model"].lower(), captured["model"]
    print("MEMORY_OK | turnos enviados:", len(msgs), "| modelo:", captured["model"])


if __name__ == "__main__":
    run()
