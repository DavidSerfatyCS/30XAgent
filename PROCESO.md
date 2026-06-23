# PROCESO — Agente de Onboarding 30X (Tech Volunteer)

> Documento maestro y handoff. Quien retome esto (chat nuevo, Codex, o yo) debe poder
> entender el estado completo leyendo solo este archivo. Se actualiza en CADA paso.

**Última actualización:** 2026-06-23 (noche) — validación en vivo 11/11 (Claude Code), fixes de
gradio y .env. Pendiente principal: ejecutar el deploy + grabar video.

---

## 1. Qué estamos construyendo

Un agente conversacional de onboarding para 30X. Responde preguntas de gente nueva basándose
**exclusivamente** en 3 PDFs de onboarding. Mantiene memoria dentro de la sesión y escala (dice
"no sé + a quién preguntar") cuando la respuesta no está en los docs.

**Plazo:** prueba técnica de 48h. **Fuente de verdad:** los 4 PDFs. El brief manda sobre todo.

## 2. Entregables (lo que se evalúa)

1. Agente funcionando, accesible sin instalar nada (deploy público).  → **validado en vivo 11/11; falta ejecutar el deploy**
2. Repo GitHub con commits progresivos, README, sin credenciales.     → **repo creado y pusheado; README listo**
3. **Video de proceso 5–10 min (el más pesado)**, humano/creativo.    → **guión borrador listo (VIDEO_SCRIPT.md)**
4. Google Doc con los 3 links accesibles sin permiso → Tally.          → **pendiente (al final)**

## 3. Decisiones bloqueadas (no se rediscuten sin motivo)

| Decisión | Elección | Por qué (1 línea) |
|---|---|---|
| Retrieval | Full-context (3 docs enteros, sin RAG) | ~17 KB caben; RAG sería sobre-ingeniería y bajaría precisión |
| Entrenamiento | Ninguno; API + contexto | La inteligencia ya viene en el modelo; actualizar = cambiar texto |
| Modelo | API comercial, default **Haiku** (env var MODEL) | Tarea fácil; Haiku alcanza; criterio de costo |
| UI / deploy | Gradio + HF Spaces o Render | Chat+memoria casi gratis; deploy sin instalar nada |
| Confidencialidad | PDFs fuera del repo (.gitignore); KB sí se incluye | Deploy se construye desde git; tensión documentada en GAPS |
| Injertos del plan alt. | anti prompt-injection + TESTING.md + GAPS.md | Lo mejor del plan RAG/Next.js sin su sobre-ingeniería |
| Tracking | PROCESO + ERRORES + BUILDLOG | Proceso/handoff/video sin sprawl |

## 4. Criterios que HUNDEN el proyecto si fallan (foco máximo)

- El agente alucina o responde fuera de los docs (RF-01).
- Cualquiera de los 3 links no abre sin pedir permiso.
- No hay video, o es un tutorial de uso en vez de un video de proceso.

## 5. Estructura de archivos (estado actual)

```
Tech X/
├── 30X_*.pdf                  (inputs; FUERA del repo por .gitignore)
├── app.py                     interfaz Gradio + modelo + memoria (prod-ready)
├── knowledge_base.md          KB = fuente de verdad del agente
├── system_prompt.md           reglas: grounding, escalado, anti-injection
├── requirements.txt
├── .env.example / .gitignore
├── render.yaml                deploy en Render
├── tests/
│   ├── test_memory.py             memoria + KB en system + modelo default
│   └── test_prompt_and_kb.py      invariantes del prompt y la KB
├── README.md                  handoff técnico (RF-05) — completo
├── TESTING.md                 casos de prueba
├── GAPS.md                    gaps + tensión confidencialidad (entregable)
├── BUILDLOG.md                bitácora de decisiones (material del video)
├── VIDEO_SCRIPT.md            guión borrador del video
└── PROCESO.md                 este archivo
```

## 6. TODO LIST por fase (se actualiza cada paso)

Estados: [ ] pendiente · [~] en progreso · [x] hecho · [!] bloqueado

### Fase 0 — Análisis y setup — [x]
### Fase 1 — Núcleo de grounding — [x]  (dry-run de las 8 preguntas OK; Checkpoint 2 aprobado)
### Fase 2 — Memoria + interfaz — [x]  (Gradio + history; test de memoria pasa; Checkpoint 3 mostrado)
### Fase 2.5 — Injertos del plan alternativo — [x]  (anti-injection + TESTING.md + GAPS.md + tests)
### Fase 2.6 — Seguridad / guardrails — [x]
- [x] app.py: tope de input + rate limit por IP/sesión (env-configurable) + bloqueo off-topic en prompt
- [x] tests/test_security.py (rate-limit, input cap, reglas del prompt) — pasa
- [x] Reparado system_prompt.md (estaba truncado: faltaban Estilo y "Qué NO haces")
- [x] Batería adversarial S1–S8 documentada en TESTING.md
- [ ] Red-team en vivo (20–30 preguntas) contra el Space — pendiente, lo corre Claude vía gradio_client

### Fase 3 — Deploy — [~] (preparado; falta ejecutar)
- [x] app.py prod-ready: manejo de errores (no stacktrace al usuario), guarda input vacío, server 0.0.0.0 + PORT
- [x] render.yaml + instrucciones de HF Spaces en README
- [x] Validación en vivo: 11/11 casos de TESTING.md contra el modelo real (Claude Code, 2026-06-23)
- [x] Fix: pin gradio>=5,<6 (6.x rompía ChatInterface type=); rename .env.txt -> .env real
- [ ] Deploy real en host (elegir HF Spaces vs Render) + cargar key en el host
- [ ] Verificar acceso sin instalar nada desde otra cuenta

### Fase 4 — README + repo + commits — [x] (en gran parte)
- [x] README completo (RF-05: cómo corre, cómo se actualiza la KB, credenciales, deploy, testing, limitaciones)
- [x] Repo creado y pusheado por Amo; .gitignore deja PDFs y .env afuera
- [ ] Commit/push de los archivos nuevos de esta sesión (README, tests, render.yaml, VIDEO_SCRIPT, docs)

### Fase 5 — Video — [~]
- [x] Guión borrador humano/creativo (VIDEO_SCRIPT.md), 5 demos marcados
- [ ] Grabar (requiere agente deployado)

### Fase 6 — Empaquetado final — [ ]
- [ ] Google Doc con los 3 links accesibles sin permiso → Tally

## 7. Cómo correr / actualizar / deployar

Todo documentado en `README.md`. Resumen: `pip install -r requirements.txt`, key en `.env`,
`python app.py`. Actualizar KB = editar `knowledge_base.md` y redeploy (sin reentrenar).

## 8. Qué necesito de David para destrabar (en orden)

1. **API key de Anthropic** cargada en el host (no en el repo) — destraba deploy y test en vivo.
2. **Elegir host:** Hugging Face Spaces (recomendado para Gradio) o Render (hay render.yaml).
3. **Commit/push** de los archivos nuevos de esta sesión (ver comandos que paso aparte).
   - Re-subir al Space (cambiaron desde la última subida): app.py, requirements.txt, system_prompt.md.
   - En el README del Space: sdk_version: 6.5.1.
4. Respuesta de 30X a las 2 preguntas (Amo las envía): dueño de escalado técnico + quién pone la key.

## 9. Estado de los tests (todos offline, sin API)

- `tests/test_memory.py` → MEMORY_OK (memoria RF-02 + KB en system RF-01 + default Haiku).
- `tests/test_prompt_and_kb.py` → INVARIANTS_OK (reglas del prompt + hechos clave de la KB).
- Casos contra el modelo real (F1–F5 + R1–R6) en TESTING.md: **validados en vivo 11/11** (Claude Code, 2026-06-23).
