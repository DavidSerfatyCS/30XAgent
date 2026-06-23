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
