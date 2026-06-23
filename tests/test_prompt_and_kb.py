"""
Test de invariantes del prompt y la base de conocimiento, SIN API ni red.

Protege contra regresiones: si alguien edita system_prompt.md o knowledge_base.md y borra
sin querer una regla central (abstención, anti-inyección, escalado) o un hecho clave de la KB,
este test falla. Correr desde la raíz:  python tests/test_prompt_and_kb.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run():
    sp = (ROOT / "system_prompt.md").read_text(encoding="utf-8").lower()
    kb = (ROOT / "knowledge_base.md").read_text(encoding="utf-8")

    # --- Reglas que el system prompt NO debe perder ---
    assert "únicamente" in sp or "unicamente" in sp, "falta la regla de responder solo desde la KB (RF-01)"
    assert "prompt-injection" in sp or "ignorar los documentos" in sp, "falta el guardrail anti-inyección"
    assert "chief of staff" in sp, "falta el default de escalado (RF-03)"

    # --- Hechos clave que la KB debe contener (muestra representativa de los 3 docs) ---
    hechos = [
        "Andrés Bilbao",            # Doc1 fundadores
        "Madrid",                   # Doc1 presencia (expansión 2026)
        "Fundraising School",       # Doc2 programas
        "Circle",                   # Doc2 plataformas
        "HubSpot (o Airtable)",     # Doc3 herramientas (ambigüedad a preservar)
        "Chief of Staff",           # Doc3 escalado
        "Head of Talent (Gabriela)",# Doc3 equipo
    ]
    for h in hechos:
        assert h in kb, f"la KB perdió un hecho clave: {h}"

    print("INVARIANTS_OK | reglas del prompt y hechos de la KB presentes")


if __name__ == "__main__":
    run()
