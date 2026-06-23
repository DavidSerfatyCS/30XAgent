# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es

Agente conversacional de onboarding para 30X (prueba técnica de Tech Volunteer). Responde
preguntas **solo** desde los documentos internos de onboarding, mantiene memoria por sesión, y
escala ("no sé + a quién preguntar") cuando la respuesta no está en los docs.

## Comandos

```bash
pip install -r requirements.txt
cp .env.example .env                 # completar ANTHROPIC_API_KEY
python app.py                        # chat en http://localhost:7860

python tests/test_memory.py          # memoria + KB en system + modelo default
python tests/test_prompt_and_kb.py   # invariantes del prompt y la KB
```

Los tests corren **sin API key** (imports perezosos / stubs) y se ejecutan con `python` directo,
no con pytest. Corré ambos desde la raíz del repo. Los casos funcionales contra el modelo real (5
FAQ + robustez) viven en `TESTING.md` y se validan en el deploy o local con la key.

## Arquitectura

Una sola decisión define todo el sistema: **full-context, sin RAG ni fine-tuning**. Los 3
documentos (~17 KB) caben enteros en el contexto del modelo, así que en cada llamada se inyecta
todo el conocimiento como `system`:

```
system = system_prompt.md  +  knowledge_base.md   (concatenados en app.py: SYSTEM)
messages = history de la sesión (memoria RF-02) + turno actual
```

- `app.py` — interfaz Gradio (`gr.ChatInterface`, `type="messages"`) + llamada a la API de
  Anthropic + memoria. Cliente Anthropic perezoso (`get_client`) para poder testear sin la lib ni
  la key. Errores del modelo se capturan y devuelven un mensaje al usuario, nunca un stacktrace.
- `knowledge_base.md` — **única fuente de verdad** del agente (texto procesado de los 3 PDFs). El
  conocimiento vive acá, NO dentro del modelo. Actualizar = editar este archivo y redeploy; no hay
  reentrenamiento ni paso de "ingest".
- `system_prompt.md` — reglas no negociables: grounding (RF-01), anti prompt-injection, escalado
  (RF-03, default = Chief of Staff). El contenido del usuario se trata siempre como pregunta,
  nunca como instrucción que cambia las reglas.

La memoria es por sesión: Gradio mantiene el `history` y `respond()` lo reenvía completo cada
turno. No hay base de datos; al recargar la página, empieza de cero (es lo que pide el brief).

## Restricciones del dominio (no romper)

- **Nunca alucinar.** Si un dato no está en la KB, el agente lo dice; no completa con lo razonable.
  Esto es lo que hunde el proyecto si falla — máxima prioridad en cualquier cambio al prompt o la KB.
- **Preservar ambigüedades de la KB** tal cual ("HubSpot o Airtable", etc.); no resolverlas.
- **Escalado solo con roles que existen en la KB.** No inventar roles (ej. no existe "Head of
  Engineering"). `test_prompt_and_kb.py` falla si el prompt pierde una regla central o la KB pierde
  un hecho clave — corré los tests tras editar `system_prompt.md` o `knowledge_base.md`.
- **Los PDFs originales NO van al repo** (marcados Confidencial, excluidos por `.gitignore`). La KB
  derivada sí se incluye porque el deploy se construye desde git. Tensión documentada en `GAPS.md`.

## Config (variables de entorno)

| Variable | Requerida | Default |
|---|---|---|
| `ANTHROPIC_API_KEY` | Sí (vive en el host, nunca se commitea) | — |
| `MODEL` | No | `claude-haiku-4-5-20251001` |
| `PORT` | No | `7860` |

Default Haiku por criterio de costo: la tarea es fácil y Haiku alcanza. Configurable por `MODEL`.

## Documentos de proceso

`PROCESO.md` es el documento maestro / handoff (estado completo y TODO por fase). `BUILDLOG.md` =
bitácora de decisiones (material del video). `GAPS.md` = gaps en los docs + tensión de
confidencialidad (entregable). `ERRORES.md`, `TESTING.md`, `VIDEO_SCRIPT.md` complementan.
