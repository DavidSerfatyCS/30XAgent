# PROCESO — Agente de Onboarding 30X (Tech Volunteer)

> Documento maestro y handoff. Quien retome esto (chat nuevo, Codex, o yo) debe poder
> entender el estado completo leyendo solo este archivo. Se actualiza en CADA paso.

**Última actualización:** 2026-06-23 — fin de fase de análisis, arrancando setup.

---

## 1. Qué estamos construyendo

Un agente conversacional de onboarding para 30X. Responde preguntas de gente nueva en el
equipo basándose **exclusivamente** en 3 PDFs de onboarding. Mantiene memoria dentro de la
sesión y escala (dice "no sé + a quién preguntar") cuando la respuesta no está en los docs.

**Plazo:** prueba técnica de 48h. **Fuente de verdad:** los 4 PDFs. El brief manda sobre todo.

## 2. Entregables (lo que se evalúa)

1. Agente funcionando y accesible sin instalar nada (deploy público o Colab).
2. Repo GitHub: commits progresivos, README completo, sin credenciales.
3. **Video de proceso 5–10 min (el entregable más pesado)** — formato humano, creativo y
   entendible. Muestra: decisiones de arquitectura y por qué, uso de AI, qué falló y cómo se
   resolvió, cómo se actualiza la KB, y gaps de los docs.
4. Entrega: un Google Doc con los 3 links (todos accesibles sin pedir permiso) → Tally.

## 3. Decisiones bloqueadas (no se rediscuten sin motivo)

| Decisión | Elección | Por qué (1 línea) |
|---|---|---|
| Retrieval | **Full-context** (3 docs enteros en el prompt, sin RAG) | ~17 KB caben de sobra; RAG sería sobre-ingeniería y bajaría precisión |
| UI / deploy | **Gradio o Streamlit** en host gratuito | "Usable por no-técnico sin instalar nada" con mínimo esfuerzo (RF-04) |
| Modelo LLM | Claude o ChatGPT (API) | Es el stack de AI que el Doc3 dice que usa 30X |
| Tracking | PROCESO.md + ERRORES.md + BUILDLOG.md | Proceso/handoff/video sin sprawl de archivos |
| Modelo | API comercial, default **Haiku** (env var MODEL) | Tarea fácil; Haiku alcanza; criterio de costo |
| Confidencialidad | PDFs fuera del repo (.gitignore); KB sí se incluye | Deploy se construye desde git; tensión documentada en GAPS |
| Injertos del plan alt. | anti prompt-injection + TESTING.md + GAPS.md | Lo mejor del plan RAG/Next.js sin su sobre-ingeniería |

## 4. Criterios que HUNDEN el proyecto si fallan (foco máximo)

- El agente alucina o responde fuera de los docs (RF-01). → blindar grounding + abstención.
- Cualquiera de los 3 links no abre sin pedir permiso. → checkpoint de accesibilidad al final.
- No hay video, o es un tutorial de uso en vez de un video de proceso.

## 5. Estructura de archivos (estado objetivo)

```
Tech X/
├── 30X_Brief_TechVolunteer_v4.pdf      (input, autoridad máxima)
├── 30X_Doc1_Organizacion.pdf           (fuente de verdad del agente)
├── 30X_Doc2_Programas_Operacion.pdf    (fuente de verdad del agente)
├── 30X_Doc3_Equipo_Herramientas.pdf    (fuente de verdad del agente)
├── PROCESO.md                          (este archivo — handoff)
├── ERRORES.md                          (log de fallos y soluciones)
├── BUILDLOG.md                         (material para el video)
└── [app por crear: código del agente + README]   ← Fase 1+
```

## 6. TODO LIST por prioridad / fase (se actualiza cada paso)

Estados: [ ] pendiente · [~] en progreso · [x] hecho · [!] bloqueado

### Fase 0 — Análisis y setup
- [x] Leer y verificar extracción de los 4 PDFs
- [x] Tabla de requisitos, criterios, arquitectura, riesgos, gaps, plan (aprobado)
- [x] Crear archivos de tracking (PROCESO / ERRORES / BUILDLOG)
- [x] Decisión sobre las 2 preguntas: Amo las manda a 30X; seguimos con defaults en paralelo

### Fase 1 — Núcleo de grounding  → CHECKPOINT 2 (mostrar respuestas antes de UI)
- [x] Preparar los 3 docs como contexto estructurado (knowledge_base.md, tablas conservadas)
- [x] System prompt con reglas de RF-01 (solo docs + abstención) y RF-03 (escalado) → system_prompt.md
- [x] Probar las 5 FAQ + 3 preguntas out-of-scope (DRY-RUN de lógica OK; validación con API real pendiente)
- [x] Checkpoint 2 mostrado y aprobado por Amo

### Fase 2 — Memoria + interfaz  → CHECKPOINT 3
- [x] Historial de sesión (RF-02) — app.py reenvía history al modelo; verificado con test stub
- [x] Envolver en Gradio (RF-04) — gr.ChatInterface; elegido sobre Streamlit por chat+memoria built-in
- [x] Archivos de soporte: requirements.txt, .env.example, .gitignore (key fuera del repo)
- [x] Verificación: py_compile + test_memory (memoria, KB en system, default Haiku)
- [x] Pasar preview a Amo (Checkpoint 3 mostrado)

### Fase 2.5 — Injertos del plan alternativo (adoptados tras comparar)
- [x] Guardrail anti prompt-injection en system_prompt.md (+ verificado presente)
- [x] TESTING.md con tabla de casos (FAQ + memoria + no-aluc. + ambigüedad + inyección)
- [x] tests/test_memory.py como archivo del repo (QA reproducible, pasa)
- [x] GAPS.md como entregable + tensión confidencialidad documentada
- [x] .gitignore excluye PDFs originales (no redistribuir confidencial)
- [ ] PENDIENTE EXTERNO: API key para validar casos en vivo + deploy (Fase 3)  ← ESTAMOS AQUÍ

**Decisiones registradas:** API + contexto sin entrenamiento; modelo default Haiku (env var MODEL);
PDFs fuera del repo; adoptados anti-injection/TESTING/GAPS del plan alternativo, rechazados
RAG/Next.js/escalado-por-keywords por sobre-ingeniería. Ver BUILDLOG.

### Fase 3 — Deploy + accesibilidad  → CHECKPOINT 4
- [ ] Deploy a host gratuito
- [ ] Verificar acceso sin instalar nada / desde otra cuenta
- [ ] PARAR y pasar link público

### Fase 4 — README + repo + commits  → CHECKPOINT 5
- [ ] README con: cómo corre, cómo se actualiza la KB, qué credenciales necesita (RF-05)
- [ ] Repo público, cero credenciales, commits progresivos
- [ ] PARAR y revisar

### Fase 5 — Video de proceso (humano/creativo)  → CHECKPOINT 6
- [ ] Guion desde BUILDLOG (5 buckets)
- [ ] Grabar / revisar antes de entregar

### Fase 6 — Empaquetado final  → CHECKPOINT 7
- [ ] Google Doc con los 3 links, todos accesibles sin permiso
- [ ] PARAR antes de subir al Tally

## 7. Cómo correr (se completa en Fase 1–3)

_Pendiente._

## 8. Preguntas abiertas / pendientes de decisión

1. **Escalado técnico:** los docs solo nombran al Chief of Staff como default para preguntas
   no documentadas; no hay dueño técnico explícito para "bloqueos técnicos" (FAQ #5).
   Pendiente: ¿preguntamos a 30X o usamos el default documentado? (Amo dijo: sin recordatorio).
2. **API key del LLM:** ¿la pone 30X o el candidato? Afecta RF-05 y el deploy público.
   Probable: la ponemos nosotros para la demo y lo documentamos.
