# GAPS — Información que debería estar en los documentos y no está

> El brief pide explícitamente identificar gaps en los documentos provistos y explicarlos.
> Todo esto sale SOLO de leer los 3 PDFs de onboarding; no se asume nada externo sobre 30X.
> Formato: qué falta · por qué importa · qué pregunta del agente queda coja · a quién preguntar.

## 1. Dueño técnico para bloqueos técnicos
- **Qué falta:** Existe el rol "Tech Volunteer(s)" pero no se dice a quién escribe alguien con un
  problema técnico. Solo hay un default genérico (líder de área) y el global (Chief of Staff).
- **Por qué importa:** Es una de las 5 FAQ centrales del brief (FAQ 5).
- **Pregunta coja:** "¿A quién escribo si tengo un bloqueo técnico?" → el agente solo da el default.
- **A quién preguntar:** Chief of Staff.

## 2. Política / proceso de acceso a herramientas
- **Qué falta:** Se dice "pide acceso a tu líder de área" pero no quién aprueba, cómo, ni en cuánto.
- **Por qué importa:** El onboarding real gira en torno a obtener accesos (Día 1).
- **Pregunta coja:** "¿Cómo consigo acceso a HubSpot / Circle?"
- **A quién preguntar:** Head of Talent (Gabriela) / Chief of Staff.

## 3. SLA y canal oficial de soporte
- **Qué falta:** No hay tiempos de respuesta ni canal definido (¿WhatsApp? ¿Notion?).
- **Por qué importa:** Fija expectativas del nuevo miembro.
- **Pregunta coja:** "¿En cuánto me responden si pregunto algo?"
- **A quién preguntar:** Chief of Staff.

## 4. Owners de los documentos de onboarding
- **Qué falta:** No se sabe quién mantiene cada doc ni cada cuánto se actualiza.
- **Por qué importa:** RF-05 pide saber cómo se actualiza la KB; sin owner el proceso queda a medias.
- **Pregunta coja:** "¿Quién actualiza esta info / a quién aviso que está desactualizada?"
- **A quién preguntar:** Chief of Staff (el doc dice "propónla para agregarse").

## 5. Matriz de escalado tema → persona
- **Qué falta:** Solo existe el default (Chief of Staff); no hay un mapa por tema.
- **Por qué importa:** RF-03 depende de esto; hoy el agente solo puede dar el default.
- **Pregunta coja:** Cualquier "¿a quién le pregunto sobre [tema X]?" fuera de lo cubierto.
- **A quién preguntar:** Chief of Staff.

## 6. Detalle de compensación de roles voluntarios
- **Qué falta:** Doc1 dice "aprendizaje, red y experiencia"; sin horas esperadas, duración ni si hay estipendio.
- **Por qué importa:** Pregunta natural de quien entra como voluntario.
- **Pregunta coja:** "¿Cuántas horas se esperan de mí? ¿Es remunerado?"
- **A quién preguntar:** Head of Talent / Chief of Staff.

## 7. Herramientas con alternativas sin resolver
- **Qué falta:** "HubSpot o Airtable", "Brevo/Sendinblue o similar", "Stripe o equivalente regional".
- **Por qué importa:** El agente no puede dar respuesta definitiva sobre el stack real.
- **Pregunta coja:** "¿Qué CRM / pasarela usamos exactamente?"
- **A quién preguntar:** Head of Sales / Tech Volunteer.

---

## Tensión de diseño detectada (no es un gap del doc, es del problema)

**Agente público vs. contenido confidencial.** Los PDFs están marcados "Confidencial", pero el
brief pide (a) un repositorio **público** y (b) un agente accesible **sin login** (RF-04: usable
por un no-técnico sin instrucciones). Esos dos requisitos son incompatibles con confidencialidad
real: cualquier agente accesible sin autenticación expone el contenido de su base de conocimiento
a quien le pregunte. Decisión que tomamos y por qué:
- **No** commiteamos los PDFs originales al repo (no redistribuimos los archivos de 30X).
- **Sí** incluimos `knowledge_base.md` (texto procesado) porque el deploy se construye desde el
  repo y el agente lo necesita para funcionar.
- Lo dejamos documentado como tensión: lograr confidencialidad real exigiría auth, que el brief
  pide NO construir. Si 30X quisiera proteger el contenido, el siguiente paso sería un login o
  una allowlist — fuera del alcance de esta prueba.
