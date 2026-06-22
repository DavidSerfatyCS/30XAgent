# BUILDLOG — Material para el video de proceso

> El video (5–10 min) es el entregable más pesado y debe ser **humano, creativo y entendible**:
> no un tutorial de uso, sino una ventana a cómo pensamos y construimos.
> Estos 5 buckets son los que el brief pide explícitamente. Los llenamos EN EL MOMENTO
> (la razón de una decisión es vívida hoy y se olvida en 36h). En la Fase 5, el guion sale de acá.

---

## 1. Decisiones de arquitectura y por qué

- **Retrieval: full-context, NO RAG.** Los 3 docs juntos son ~17 KB / ~2.500 palabras: caben
  enteros en el contexto. Medimos antes de elegir. RAG (embeddings + vector store) habría
  añadido infra, riesgo de recuperar el chunk equivocado y de partir tablas rompiendo la
  asociación rol→responsabilidad. Elegir lo simple y defendible > lo sofisticado.
  _(Ángulo para el video: mostrar que la decisión de NO usar RAG es criterio, no pereza.)_

- **Sin entrenamiento / sin fine-tuning: API + contexto.** La inteligencia (lenguaje,
  razonamiento, seguir instrucciones) ya viene en el modelo preentrenado. El conocimiento de 30X
  NO va en los pesos del modelo: lo inyectamos por contexto (system_prompt.md + knowledge_base.md).
  Consecuencia clave para RF-05: actualizar un documento = reemplazar texto en la KB, no
  re-entrenar. Entrenar habría costado tiempo/plata/cómputo y roto la facilidad de actualización.
  _(Ángulo video: "no entrenamos un modelo porque la inteligencia ya viene en el modelo; el
  conocimiento lo inyectamos por contexto, y por eso actualizar la base es trivial".)_

- **Modelo: API comercial, default Claude Haiku (por costo), configurable por variable de entorno.**
  Por qué API y no open-source self-hosted: el brief exige un deploy público "sin instalar nada"
  (Entregable 1) y pide documentar credenciales (RF-05) — una API comercial da máxima capacidad
  con mínimo esfuerzo de infra. Por qué Haiku y no Opus: la tarea (grounding sobre ~17 KB) es
  fácil; hasta Haiku la resuelve bien. Elegir el modelo barato a propósito demuestra criterio de
  costo ("velocidad con criterio, MVP primero", valor de 30X), no falta de recursos. El modelo y
  la API key son variables de entorno: la demo corre con nuestra key; quien clone el repo puede
  enchufar la suya. Pendiente de confirmar con 30X: quién pone la key (pregunta enviada).
  _(Ángulo video: la diferencia Opus vs Haiku no se nota en "buscá en estos docs y si no está,
  decilo"; gastar en Opus sería un cañón para una mosca.)_

## 2. Cómo usamos AI para construir

- **Comparamos nuestro plan contra un plan alternativo generado con ChatGPT** (RAG + Next.js/TS +
  Vercel) y decidimos por criterio, no por moda. Adoptamos lo mejor del alternativo: guardrail
  anti prompt-injection (+ test), TESTING.md y GAPS.md como entregables, y la observación de
  confidencialidad (PDFs "Confidencial" vs repo público + agente sin login). Rechazamos su núcleo:
  RAG/chunking (sobre-ingeniería para 17 KB; introduce falsos "no sé" por omisión de chunks —
  rompe la FAQ2 "listá TODAS las herramientas"), Next.js/TS (gasta ~10 h en plumbing de UI que el
  brief dice que no necesita ser linda; ese tiempo va al video) y el escalado por keywords
  (`question.includes(...)` es frágil ante sinónimos; el prompt es más flexible).
  _(Ángulo video: usar AI no es aceptar lo que sugiere; es comparar dos diseños y defender por qué
  el más simple gana para esta tarea.)_

- _(pendiente: capturar prompts clave concretos, dónde AI aceleró, dónde nos hizo perder tiempo)_

## 3. Qué no funcionó y cómo lo resolvimos

- _(pendiente — se cruza con ERRORES.md; acá va la versión "narrable")_

## 4. Cómo se actualiza el sistema si cambia un documento

- _(pendiente: el proceso de reemplazar la KB; debe coincidir con el README / RF-05)_

## 5. Gaps encontrados en los documentos (del análisis)

1. **Sin dueño técnico para bloqueos técnicos.** Hay "Tech Volunteer(s)" pero no se dice a
   quién escribe alguien con un problema técnico. Choca con la FAQ #5. Solo hay default genérico
   (líder de área) y el global (Chief of Staff). → preguntar al Chief of Staff.
2. **Sin políticas de acceso a herramientas.** "Pide acceso a tu líder de área" pero no quién
   aprueba ni SLA. El onboarding real gira en torno a accesos (Día 1).
3. **Sin SLA ni canal de soporte definido.** No hay tiempos de respuesta ni canal oficial.
4. **Sin owners de los documentos de onboarding.** RF-05 pide saber cómo se actualiza la KB;
   sin owner el proceso queda incompleto.
5. **Sin matriz de escalado tema→persona.** Solo existe el default (CoS); RF-03 depende de esto.
6. **Compensación de roles voluntarios sin detalle** (horas esperadas, duración, estipendio).
7. **Herramientas con alternativas sin resolver:** HubSpot *o* Airtable, Brevo *o similar*,
   Stripe *o equivalente regional*. El agente no puede dar respuesta definitiva del stack.
