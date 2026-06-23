# BUILDLOG — Material para el video de proceso

> El video (5–10 min) es el entregable más pesado y debe ser **humano, creativo y entendible**:
> no un tutorial de uso, sino una ventana a cómo pensamos y construimos.
> Estos 5 buckets son los que el brief pide explícitamente. El guión armado está en VIDEO_SCRIPT.md.

---

## 1. Decisiones de arquitectura y por qué

- **Retrieval: full-context, NO RAG.** Los 3 docs juntos son ~17 KB / ~2.500 palabras: caben
  enteros en el contexto. Medimos antes de elegir. RAG (embeddings + vector store) habría añadido
  infra, riesgo de recuperar el chunk equivocado y de partir tablas rompiendo la asociación
  rol→responsabilidad. Elegir lo simple y defendible > lo sofisticado.

- **Sin entrenamiento / sin fine-tuning: API + contexto.** La inteligencia ya viene en el modelo
  preentrenado. El conocimiento de 30X NO va en los pesos: se inyecta por contexto (system_prompt.md
  + knowledge_base.md). Consecuencia para RF-05: actualizar un documento = reemplazar texto, no
  re-entrenar.

- **Modelo: API comercial, default Claude Haiku (por costo), configurable por env var.** El brief
  exige deploy público "sin instalar nada" y pide documentar credenciales (RF-05) — una API comercial
  da máxima capacidad con mínimo esfuerzo de infra. Haiku alcanza para grounding sobre 17 KB; elegir
  el modelo barato a propósito demuestra criterio de costo. Key y modelo por variable de entorno.

- **Por qué Haiku y no un modelo aún más barato (ej. Gemini Flash-Lite) ni una capa multi-proveedor.**
  Para la demo el costo es despreciable (centavos), así que la diferencia de precio entre modelos no
  decide nada acá; prioricé confiabilidad y seguimiento de instrucciones en español, donde Haiku ya
  validó 11/11. Un modelo más barato tiene sentido a escala/producción, no en una prueba evaluada.
  Y NO construí una capa de abstracción multi-proveedor (switch Anthropic/Gemini): nadie la pidió y
  sería flexibilidad especulativa — la misma trampa de over-engineering que RAG/Next.js. La
  portabilidad ya está dada gratis: la llamada al modelo está aislada en `get_client()` y `respond()`
  (app.py), así que cambiar de proveedor sería un cambio acotado a esas funciones + re-testear, sin
  reescribir grounding, memoria ni escalado.
  _(Ángulo video: la jugada senior no es construir el switch a Gemini, es NO construirlo y explicar
  por qué. Ojo: cualquier frase tipo "elegí RAG" sería falsa — usamos full-context.)_

- **Interfaz: Gradio (ChatInterface) sobre Next.js.** Gradio trae chat + memoria de sesión + estados
  de carga casi gratis (RF-02, RF-04). Next.js/TS habría gastado ~10 h en plumbing de UI que el brief
  dice que no necesita ser linda; ese tiempo va al video.

- **Guardrails livianos para un deploy público (más de lo que pide el brief, por criterio).** Como
  el Space corre con una API key propia, agregamos tope de longitud de entrada, rate limit por
  IP/sesión (en memoria, degradable a global) y un bloqueo explícito de uso como LLM general. NO
  pusimos auth/Redis/CAPTCHA: sería sobre-ingeniería para una demo. Umbrales por env var para poder
  relajarlos durante el red-team.
  _(Ángulo video: pensar los vectores de abuso —agotar la API, usar el bot como ChatGPT gratis— y
  mitigarlos con lo mínimo razonable, sin sobre-construir.)_

## 2. Cómo usamos AI para construir

- **Comparamos nuestro plan contra un plan alternativo generado con ChatGPT** (RAG + Next.js/TS +
  Vercel) y decidimos por criterio, no por moda. Adoptamos lo mejor del alternativo: guardrail
  anti prompt-injection (+ test), TESTING.md y GAPS.md como entregables, y la observación de
  confidencialidad (PDFs "Confidencial" vs repo público + agente sin login). Rechazamos su núcleo:
  RAG/chunking (sobre-ingeniería para 17 KB; introduce falsos "no sé" por omisión de chunks —
  rompe la FAQ2 "listá TODAS las herramientas"), Next.js/TS (gasta ~10 h en plumbing de UI) y el
  escalado por keywords (`question.includes(...)` es frágil ante sinónimos).
  _(Ángulo video: usar AI no es aceptar lo que sugiere; es comparar dos diseños y defender por qué
  el más simple gana para esta tarea.)_

## 3. Qué no funcionó y cómo lo resolvimos

(Detalle completo en ERRORES.md.)
- **Git rooteó en la carpeta equivocada** y quería subir los PDFs confidenciales (aparecían con
  `../` en `git status`). Lo detectamos mirando el status y re-inicializamos en la carpeta correcta.
  _(Ángulo video: leer el síntoma — el `../` — en vez de pelear con el `.gitignore`.)_
- **El entorno de edición truncaba app.py** a la mitad. Pasamos a escribir el archivo por shell y
  agregamos `tests/test_prompt_and_kb.py`, que falla si el prompt o la KB pierden algo.
  _(Ángulo video: los tests de invariantes te avisan cuando algo se rompe sin que lo notes.)_
- **gradio 6.x rompía el arranque** (la 6.x eliminó `type=` en ChatInterface). Lo pineamos a
  `gradio>=5,<6`. Lo detectamos levantando la app de verdad — el smoke test del sandbox no lo agarró.
- **Windows guardó el `.env` como `.env.txt`**, así que `load_dotenv()` no encontraba la key; un
  rename al `.env` real lo resolvió.
- **Validación en vivo:** los 11 casos de TESTING.md (F1–F5, R1–R6) pasaron **11/11** contra el
  modelo real (Claude Code). El "pendiente API" quedó cerrado.
  _(Ángulo video: el bug de gradio solo apareció al correr la app de verdad, no en los tests
  offline; por eso la validación en vivo importa.)_

## 4. Cómo se actualiza el sistema si cambia un documento

- El conocimiento vive en `knowledge_base.md`, no en el modelo. Para actualizar: abrir el archivo,
  reemplazar la sección del doc que cambió (DOC1/DOC2/DOC3) conservando las tablas, guardar y
  redeploy (o reiniciar `python app.py`). No se reentrena nada ni se regeneran índices.
- La API key vive en el host (Secrets de HF Spaces / env var de Render), nunca en el repo.
- Está documentado en el README (sección "Cómo se actualiza la base de conocimiento").

## 5. Gaps encontrados en los documentos (del análisis)

(Detalle entregable en GAPS.md.)
1. **Sin dueño técnico para bloqueos técnicos** — choca con la FAQ #5. Solo hay default genérico.
2. **Sin políticas de acceso a herramientas** (quién aprueba, SLA).
3. **Sin SLA ni canal de soporte definido.**
4. **Sin owners de los documentos de onboarding** (RF-05 queda a medias).
5. **Sin matriz de escalado tema→persona** (solo el default CoS).
6. **Compensación de roles voluntarios sin detalle** (horas, duración, estipendio).
7. **Herramientas con alternativas sin resolver:** HubSpot/Airtable, Brevo/similar, Stripe/equivalente.
- **Tensión de diseño:** agente público vs. contenido confidencial. Repo público + agente sin login
  (RF-04) son incompatibles con confidencialidad real. Documentado, no fingido como resuelto.
