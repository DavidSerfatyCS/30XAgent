# ERRORES — Log de fallos y soluciones

> Cada vez que intentamos algo que falló y tuvimos que cambiar de approach, queda acá.
> No es para esconder errores: es material directo para el bucket "qué no funcionó" del video
> y para que un handoff no repita el mismo callejón sin salida.

**Formato de cada entrada:**

```
### [fecha] — Título corto del fallo
- **Qué intentábamos:** ...
- **Qué falló / síntoma:** ...
- **Causa raíz:** ...
- **Cómo lo resolvimos / nuevo approach:** ...
- **Aprendizaje:** ...
```

---

### 2026-06-23 — Git se inicializó en la carpeta equivocada y quería subir los PDFs confidenciales
- **Qué intentábamos:** Inicializar el repo y verificar que el `.gitignore` excluyera los PDFs.
- **Qué falló / síntoma:** En `git status` los PDFs aparecían como `../30X_*.pdf` (con `../`), o sea
  que el repo había quedado rooteado una carpeta más arriba del proyecto. El `.gitignore` del
  proyecto no los cubría porque estaban fuera de su subárbol.
- **Causa raíz:** El `git init` efectivo quedó en `...\playground\Tech X` (carpeta padre), no en
  `...\Tech X\Tech X` (proyecto). La estructura de carpetas anidadas con el mismo nombre confundió.
- **Cómo lo resolvimos:** Borrar el `.git` de la carpeta padre y re-inicializar dentro de la carpeta
  del proyecto, donde vive el `.gitignore` correcto. Verificado con `git check-ignore`.
- **Aprendizaje:** Confirmar siempre `git rev-parse --show-toplevel` antes de commitear; el `../` en
  `git status` es la señal de que la raíz del repo no es la que creés.

### 2026-06-23 — El entorno de edición truncaba app.py
- **Qué intentábamos:** Editar `app.py` (manejo de errores + launch para deploy) con el editor.
- **Qué falló / síntoma:** El archivo quedaba cortado a la mitad (unterminated string literal). Dos
  intentos de reescritura completa también quedaron truncados a ~80-86 líneas.
- **Causa raíz:** Problema de sincronización al escribir el archivo a través del entorno de build;
  la escritura se cortaba antes de completar.
- **Cómo lo resolvimos:** Escribir el archivo por otra vía (heredoc en shell), que sí persiste el
  contenido completo. Confirmado con `py_compile` + los tests pasando.
- **Aprendizaje:** Para archivos de código en este entorno, escribir por shell y verificar con
  `py_compile`/tests inmediatamente después. Los tests de invariantes atrapan truncamientos.

### 2026-06-23 — gradio 6.x rompía el arranque de la app
- **Qué intentábamos:** Levantar app.py en el entorno real (Windows) para validar en vivo.
- **Qué falló / síntoma:** Crash al arrancar; gradio 6.x eliminó el parámetro `type=` de ChatInterface.
- **Causa raíz:** requirements pedía `gradio>=4.0`, que resolvía a 6.x; la API cambió entre majors.
- **Cómo lo resolvimos:** Pin `gradio>=5,<6`. Verificado con launch real + HTTP 200 (Claude Code).
- **Aprendizaje:** Acotar rangos cuando una API puede romper entre majors; un smoke test sin arranque
  real no lo agarra.

### 2026-06-23 — Windows guardó el .env como .env.txt (load_dotenv no veía la key)
- **Qué intentábamos:** Que app.py tomara la key desde el archivo .env.
- **Qué falló / síntoma:** `load_dotenv()` no encontraba la key; el archivo real era `.env.txt`.
- **Causa raíz:** El editor de Windows le agregó `.txt` al guardar "como .env".
- **Cómo lo resolvimos:** Rename al `.env` real (sin extensión). Tras eso queda ignorado por git y
  `load_dotenv` lo carga.
- **Aprendizaje:** En Windows, activar "ver extensiones de archivo"; `.env` no debe terminar en `.txt`.

### 2026-06-23 — HF Spaces fuerza gradio 6.5.1 (no acepta 5.x): adaptamos el código a v6
- **Qué intentábamos:** Deployar en Hugging Face Spaces. Habíamos pineado `gradio>=5,<6` porque la
  6.x eliminó `type=` en ChatInterface.
- **Qué falló / síntoma:** (1) El build de HF instala `gradio==6.5.1` (su default) y choca con
  `gradio<6` → ResolutionImpossible. (2) Setear `sdk_version: 5.50.1` en el Space dio "Gradio
  version does not exist": HF solo acepta versiones de su lista curada, distinta de PyPI.
- **Causa raíz:** En HF la versión de Gradio la fija `sdk_version` del README del Space, no
  requirements; y su lista de versiones soportadas es acotada.
- **Cómo lo resolvimos:** En vez de pelear por una 5.x soportada, adaptamos a gradio 6 (la que HF ya
  eligió): quitamos `type="messages"` de ChatInterface (en v6 el formato messages es el default) y
  pusimos `gradio>=6,<7`. Verificado en sandbox: v6 pasa el historial como `{"role","content"}`,
  idéntico a lo que `respond()` ya espera; py_compile + tests OK.
- **Aprendizaje:** En HF Spaces, alinear el código con la `sdk_version` soportada por la plataforma
  en vez de imponer una versión por requirements.

### 2026-06-23 — system_prompt.md estaba truncado en disco (faltaban Estilo y "Qué NO haces")
- **Qué intentábamos:** Endurecer el system prompt contra uso como LLM general.
- **Qué falló / síntoma:** Al editar, el archivo terminaba en "## Es": faltaban las secciones
  Estilo y "Qué NO haces" (las reglas de grounding, anti-inyección y escalado SÍ estaban).
- **Causa raíz:** El mismo truncamiento de escritura del entorno que ya nos pasó con app.py,
  ocurrido en alguna edición previa sin que se notara.
- **Cómo lo resolvimos:** Reescribir el prompt completo por shell (heredoc) con todas las secciones
  + el endurecimiento nuevo. `test_prompt_and_kb.py` y `test_security.py` confirman invariantes.
- **Aprendizaje:** Los tests de invariantes del prompt deberían chequear TODAS las secciones clave,
  no solo algunas; un archivo de prompt truncado es un fallo silencioso peligroso.

### 2026-06-23 — No pude correr el red-team contra el Space desde el sandbox (403 / egress)
- **Qué intentábamos:** Manejar el Space con `gradio_client` desde el entorno de Claude para
  dispararle ~25 preguntas adversariales.
- **Qué falló / síntoma:** `403 Forbidden` contra `*.hf.space` (la página se lee por GET, pero las
  llamadas de API se bloquean). No hay navegador Chrome conectado a la cuenta.
- **Causa raíz:** Egress restringido del entorno automatizado hacia el endpoint de la app.
- **Cómo lo resolvimos:** Red-team por dos vías alternativas: (a) `redteam.py`, script local que
  corre el usuario con su key (mismo system + KB + modelo que el deploy) y guarda las respuestas;
  (b) extensión Claude in Chrome para manejar el navegador. El veredicto de cada respuesta lo pone
  Claude (comparando contra la KB).
- **Aprendizaje:** Un entorno automatizado no siempre puede salir a servicios externos; tener un
  script de prueba reproducible que corra el usuario es un buen fallback.

### 2026-06-23 — Gradio 6 movió `theme` y `css` del constructor de Blocks a `launch()`
- **Qué intentábamos:** Aplicar tema oscuro + CSS de branding 30X pasándolos a `gr.Blocks(theme=, css=)`.
- **Qué falló / síntoma:** Warning de Gradio 6 ("parameters moved to launch()") y riesgo de que el
  branding no se aplicara en HF Spaces, donde la plataforma puede llamar a `launch()` por su cuenta
  e ignorar nuestros kwargs.
- **Causa raíz:** Cambio de API en Gradio 6; `theme`/`css` ya no van en el constructor.
- **Cómo lo resolvimos:** El CSS se inyecta como `<style>` vía `gr.HTML` dentro del Blocks (se
  renderiza pase lo que pase, verificado en el config), y además se pasa `theme`/`css` a `launch()`
  para el arranque local. Doble vía = el look no depende de quién llame a launch().
- **Aprendizaje:** En HF Spaces, no asumir que tu `launch()` corre con tus argumentos; meter el
  estilo en el árbol de la app lo hace robusto al entorno de deploy.

### 2026-06-23 — `example_icons` con emojis renderizaba imágenes rotas
- **Qué intentábamos:** Ponerle un ícono a cada tarjeta de pregunta con `example_icons=[emoji, ...]`.
- **Qué falló / síntoma:** Las tarjetas mostraban el ícono de "imagen rota" + texto cortado.
- **Causa raíz:** `example_icons` espera rutas/URLs de imagen, no caracteres emoji; Gradio los trata
  como `src` y falla la carga.
- **Cómo lo resolvimos:** Quitar `example_icons` (el usuario pidió no complicarse). Tarjetas con solo
  texto, limpias.
- **Aprendizaje:** Confirmar el tipo que espera un parámetro de UI antes de asumir que acepta emojis;
  "ícono" no siempre significa glifo.

### 2026-06-23 — El sandbox corrompió el índice de git al commitear en la carpeta montada
- **Qué intentábamos:** Hacer los commits de la UI desde el shell del entorno, sobre la carpeta del
  repo montada desde Windows.
- **Qué falló / síntoma:** El primer commit (logo) entró, pero después: `Operation not permitted` al
  tocar `.git/objects` y los locks, `index file corrupt`, y un `index.lock`/`HEAD.lock` que el
  sandbox no podía borrar.
- **Causa raíz:** El shell del entorno no tiene permisos completos sobre `.git` en la carpeta montada;
  escribir objetos/locks de git a través del mount falla a mitad y deja el índice inconsistente.
- **Cómo lo resolvimos:** No commitear git desde el sandbox. David recupera desde Windows
  (`del .git\index.lock .git\HEAD.lock .git\index` → `git reset`) y hace los `git add`/`commit` él.
  El código en disco quedó intacto; era solo metadata de git.
- **Aprendizaje:** Las operaciones de git sobre la carpeta montada se hacen del lado del usuario
  (Windows), no desde el sandbox. El entorno escribe archivos de código bien, pero no `.git`.

### 2026-06-23 — `http://0.0.0.0:7860` no abre en el navegador (ERR_ADDRESS_INVALID)
- **Qué intentábamos:** Abrir la app local tras `python app.py`.
- **Qué falló / síntoma:** "Hmmm... can't reach this page" en `http://0.0.0.0:7860/`.
- **Causa raíz:** `0.0.0.0` es la dirección de *escucha* del server (correcta para el deploy), pero
  no es una dirección navegable desde el cliente.
- **Cómo lo resolvimos:** Entrar por `http://localhost:7860` (o `127.0.0.1`). No es un bug del código.
- **Aprendizaje:** `server_name="0.0.0.0"` se queda (lo necesita Render/Spaces); en local se navega
  por localhost.
