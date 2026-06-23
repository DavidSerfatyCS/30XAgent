"""
Tests de seguridad/guardrails, SIN API ni red.

Verifica, sin key:
- Rate limit: tras RATE_LIMIT_MAX consultas, la siguiente se bloquea (sliding window).
- Tope de longitud: un mensaje gigante se rechaza sin llamar al modelo.
- El system prompt conserva las reglas anti-inyección y anti-uso-como-LLM-general.

Correr desde la raíz:  python tests/test_security.py
"""

import sys
import types
from pathlib import Path

# Stub minimo de gradio (no instalamos la lib para el test).
_g = types.ModuleType("gradio")


class _ChatInterface:
    def __init__(self, fn, **kw):
        self.fn = fn

    def launch(self, *a, **k):
        pass


_g.ChatInterface = _ChatInterface


class _Request:  # placeholder; app solo lo usa en anotaciones (string) y en runtime opcional
    pass


_g.Request = _Request
sys.modules["gradio"] = _g

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import app  # noqa: E402


def test_rate_limit():
    key = "test-ip-1.2.3.4"
    allowed = sum(0 if app._rate_limited(key) else 1 for _ in range(app.RATE_LIMIT_MAX))
    assert allowed == app.RATE_LIMIT_MAX, f"deberian permitirse {app.RATE_LIMIT_MAX}, fueron {allowed}"
    assert app._rate_limited(key) is True, "la consulta extra deberia bloquearse"


def test_input_cap():
    huge = "a" * (app.MAX_INPUT_CHARS + 100)
    out = app.respond(huge, [])
    assert "largo" in out.lower() or "maximo" in out.lower(), out
    # no debe haber intentado llamar al modelo (no hay key ni cliente seteado)


def test_prompt_blocks_general_use():
    sp = (ROOT / "system_prompt.md").read_text(encoding="utf-8").lower()
    assert "asistente" in sp and ("no escribas" in sp or "propósito general" in sp or "proposito general" in sp), \
        "falta el bloqueo de uso como asistente general"
    assert "prompt-injection" in sp or "ignorar los documentos" in sp, "falta el guardrail anti-inyección"


def run():
    test_rate_limit()
    test_input_cap()
    test_prompt_blocks_general_use()
    print("SECURITY_OK | rate-limit, tope de input y bloqueo off-topic verificados")


if __name__ == "__main__":
    run()
