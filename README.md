---
title: Agente Onboarding 30X
emoji: 💬
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 6.5.1
app_file: app.py
pinned: false
---

# Agente de Onboarding 30X

Agente conversacional que responde preguntas de personas nuevas en 30X usando **solo** los
documentos internos de onboarding. Mantiene contexto dentro de la sesión, y cuando no sabe la
respuesta lo dice y sugiere a quién escalar — en vez de inventar.

> Construido para la prueba técnica de Tech Volunteer. Fuente de verdad: 3 documentos de
> onboarding de 30X.

## Qué hace

- **Responde con base documental (RF-01):** usa únicamente el contenido de los documentos. Si algo
  no está, lo dice claramente; no inventa datos, roles ni procesos.
- **Recuerda la conversación (RF-02):** si decís que sos del área comercial, no te lo vuelve a
  preguntar.
- **Escala cuando no sabe (RF-03):** "esto no está en los documentos; preguntale al Chief of Staff".
- **Interfaz usable (RF-04):** un chat web que un no-técnico abre y usa sin instrucciones.

## Cómo funciona (arquitectura)

```
Pregunta del usuario
        │
        ▼
[ system_prompt.md  +  knowledge_base.md ]  ← se inyectan en CADA llamada
        │                         (system del modelo)
        ▼
   historial de la sesión  ──────────────►  Modelo (Claude vía API)
        (memoria, RF-02)                          │
                                                  ▼
                                            Respuesta grounded
```

Decisiones clave (el detalle y el "por qué" están en `BUILDLOG.md`):

- **Full-context, no RAG.** Los 3 documentos juntos son ~17 KB: caben enteros en el contexto del
  modelo. Hacer RAG (chunking + embeddings + retrieval) sería sobre-ingeniería para este tamaño y
  *aumentaría* el riesgo de omitir información relevante (recuperar el chunk equivocado). Pasar todo
  el contenido garantiza que el modelo nunca "no encuentre" algo que sí está.
- **Sin entrenamiento / fine-tuning.** La inteligencia ya viene en el modelo; el conocimiento de
  30X se inyecta por contexto. Por eso actualizar la base es trivial (ver abajo).
- **Modelo barato por defecto (Haiku).** La tarea es fácil para cualquier modelo decente; gastar en
  uno caro no mejora el resultado. Configurable por variable de entorno.

## Interfaz (UI)

La UI lleva el branding de 30X (fondo negro + acento lima, logo, título "Agente de Onboarding",
tarjeta de bienvenida y footer) **sin reescribir el chat**: el `gr.ChatInterface` —que maneja el
chat y la memoria de sesión— se embebe dentro de un `gr.Blocks` que solo aporta el marco visual. La
lógica del agente (`respond()`, memoria, guardrails) no se toca; el branding es 100% presentación.

Decisiones de implementación (el "por qué" está en `BUILDLOG.md`):

- **CSS inyectado como `<style>`** dentro del árbol de la app (no por el parámetro `css=`). En
  Gradio 6, `theme`/`css` se pasan a `launch()`, pero en HF Spaces la plataforma puede llamar a
  `launch()` por su cuenta; inyectar el estilo en la app hace que el branding no dependa de eso.
- **Paleta vía override de las variables CSS de Gradio** (`--block-background-fill`, `--color-accent`,
  etc.). El azul por defecto venía del `secondary_hue`; pisando las variables, todos los componentes
  (chat, tarjetas, historial) comparten una superficie oscura integrada.
- **`save_history=True`**: agrega un botón "Nuevo chat" nativo; al reiniciar, el chat vacío vuelve a
  mostrar las preguntas frecuentes.
- **Logo embebido como data URI** desde `logo.jpeg` (debe estar en el repo); si falta, la UI cae a un
  "30X" en texto y igual carga.

Los tests stubean los componentes de layout de gradio (`Blocks`, `Column`, `HTML`, `Chatbot`,
`themes`), así que `import app` sigue funcionando sin instalar gradio y sin tocar las aserciones.

## Estructura del repo

```
.
├── app.py                 # interfaz Gradio + llamada al modelo + memoria
├── knowledge_base.md      # base de conocimiento (texto procesado de los 3 PDFs) = fuente de verdad
├── system_prompt.md       # reglas del agente (grounding, escalado, anti prompt-injection)
├── requirements.txt
├── .env.example           # variables de entorno necesarias (copiar a .env)
├── render.yaml            # deploy en Render (opcional)
├── logo.jpeg              # logo 30X (embebido en la UI como data URI)
├── tests/
│   ├── test_memory.py        # memoria + KB en system + modelo default (sin API)
│   ├── test_security.py      # rate-limit, tope de input, bloqueo off-topic (sin API)
│   └── test_prompt_and_kb.py # invariantes del prompt y la KB (sin API)
├── redteam.py             # red-team adversarial reproducible (25 casos)
├── TESTING.md             # casos de prueba (FAQ, memoria, no-alucinación, inyección)
├── GAPS.md                # gaps detectados en los documentos + tensión de confidencialidad
├── BUILDLOG.md            # bitácora de decisiones (material del video)
└── PROCESO.md             # estado del proyecto y handoff
```

Los PDFs originales de 30X **no** están en el repo (marcados "Confidencial"); ver `GAPS.md`.

## Cómo correr localmente

```bash
pip install -r requirements.txt
cp .env.example .env        # y completá ANTHROPIC_API_KEY
python app.py               # abre el chat en http://localhost:7860
```

## Variables de entorno

| Variable | Requerida | Para qué | Default |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Sí | Credencial del modelo. **Nunca** se commitea. | — |
| `MODEL` | No | Id del modelo de Anthropic. | `claude-haiku-4-5-20251001` |
| `PORT` | No | Puerto del servidor (lo setean hosts como Render). | `7860` |
| `MAX_INPUT_CHARS` | No | Tope de caracteres por mensaje (corta inputs gigantes). | `2000` |
| `RATE_LIMIT_MAX` | No | Consultas permitidas por ventana, por IP/sesión. | `15` |
| `RATE_LIMIT_WINDOW_SEC` | No | Tamaño de la ventana del rate limit, en segundos. | `300` |

## Seguridad y límites de uso

Como es un deploy público con una API key propia, la app incluye guardrails livianos para evitar
abuso y proteger el gasto (no los pide el brief; se agregaron por criterio):

- **Tope de longitud de entrada** (`MAX_INPUT_CHARS`): los mensajes muy largos se rechazan sin
  llamar al modelo.
- **Rate limit por IP/sesión** (`RATE_LIMIT_MAX` por `RATE_LIMIT_WINDOW_SEC`): limita cuántas
  consultas puede hacer un mismo cliente en una ventana; degrada a un límite global si no hay IP.
  Es en memoria (se resetea al reiniciar y asume una sola réplica): suficiente para esta demo; a
  escala iría en un store externo.
- **`max_tokens` acotado** en cada llamada (límite de costo de salida).
- **Bloqueo de uso como LLM general**: el system prompt rechaza pedidos ajenos al onboarding
  (código, traducciones, tareas, etc.), no solo preguntas fuera de dominio.

**Nota para la evaluación:** los guardrails son configurables por variable de entorno. En este deploy
de evaluación el rate limit está **relajado a propósito** (`RATE_LIMIT_MAX=200` por ventana de 5 min)
para que el equipo de 30X pueda probar el agente con AI o disparando varios mensajes seguidos sin
toparse con el límite. En un entorno real se ajustaría más bajo para frenar abuso; el tope de gasto
real lo da un *spending cap* configurado en la cuenta de Anthropic, no el rate limit.

## Cómo se actualiza la base de conocimiento (RF-05)

El conocimiento del agente vive en `knowledge_base.md`, **no** dentro del modelo. Para actualizarlo
cuando cambia un documento de onboarding:

1. Abrí `knowledge_base.md` y reemplazá la sección correspondiente (DOC1 / DOC2 / DOC3) con el
   contenido nuevo, conservando el formato de tablas.
2. Guardá y redeploy (o reiniciá `python app.py`). No hay que reentrenar nada ni regenerar índices.

La KB se mantiene a mano a partir de los PDFs (la extracción inicial se hizo verificando que las
tablas no se mezclaran). No hay paso de "ingest" automático: para 3 documentos cortos, mantenerlo a
mano es más simple y menos frágil que un pipeline.

## Cómo cumple los requisitos funcionales

**Memoria de sesión (RF-02).** Gradio mantiene el historial y en cada turno `respond()` lo reenvía
completo al modelo. No hay base de datos: la memoria es por sesión, como pide el brief. (Verificado
por `tests/test_memory.py`, sin API key.)

**Escalado cuando no sabe (RF-03).** El system prompt instruye al modelo a reconocer cuándo la KB no
tiene la respuesta, decirlo explícitamente y sugerir a quién escalar usando **solo** roles que existen
en los documentos. El default es el **Chief of Staff**; para un dominio específico puede sugerir al
Head de esa área. Nunca inventa un rol.

**Resistencia a prompt-injection.** El system prompt trata el contenido del usuario como preguntas,
no como instrucciones que cambian las reglas. Pedidos como "ignorá los documentos" o "revelá tu
prompt" se rechazan. (Caso R6 en `TESTING.md`.)

## Deploy

El agente necesita estar accesible sin instalar nada. Dos opciones:

**Hugging Face Spaces (recomendado para Gradio).** Creá un Space con SDK = Gradio, subí estos
archivos y agregá el frontmatter al inicio del README del Space:

```yaml
---
title: Agente Onboarding 30X
sdk: gradio
app_file: app.py
---
```

Después, en Settings → Secrets del Space, agregá `ANTHROPIC_API_KEY`. El Space corre `app.py` solo.

**Render.** El repo incluye `render.yaml`. Creá un Web Service apuntando al repo; Render lee el
build/start de ahí. Cargá `ANTHROPIC_API_KEY` como env var en el dashboard (no en el repo).

En ambos casos la key vive en el host, no en GitHub: quien prueba el agente entra por la URL y no
necesita ninguna credencial.

## Testing

```bash
python tests/test_memory.py          # memoria + KB en system + modelo default
python tests/test_security.py        # rate-limit, tope de input y bloqueo off-topic
python tests/test_prompt_and_kb.py   # invariantes del prompt y la KB
```

Los tres corren sin API key (stubs). Los casos funcionales contra el modelo real (5 FAQ + robustez)
están en `TESTING.md` y se validan en el deploy o local con la key.

## Limitaciones conocidas

- La memoria es por sesión: al recargar la página, empieza de cero (es lo que pide el brief).
- Confidencialidad: un agente público expone el contenido de su KB a quien pregunte. Ver `GAPS.md`.

## Gaps detectados en los documentos

El brief pide identificar lo que falta en los documentos. Está en `GAPS.md` (dueño técnico para
bloqueos, políticas de acceso, SLA, owners de docs, matriz de escalado, compensación, herramientas
con alternativas sin resolver) + la tensión "agente público vs. contenido confidencial".
