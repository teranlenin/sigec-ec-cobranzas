# Estado inicial

**Corte:** 2026-11-05 (America/Bogota).  
**Fase:** bootstrap y planificación ejecutados; entorno de simulación aislado.

## Preparado
- Estructura de proyecto, reglas locales y límites de simulación.
- Diez definiciones de agentes y diez Skills individuales.
- Tres Skills compartidas: solo simulación, procedencia de evidencia y minimización de datos.
- Flujos de orquestación, ingestión RAG y actualización sandbox.
- Cuatro esquemas de memoria, fuentes normativas candidatas, tres casos y tres eventos sintéticos.
- Matriz de aceptación y validador estructural local.
- Capa de portabilidad: Codex/Gemini CLI usan Skills canónicas; Claude Code tiene espejo; se prepararon paquetes ZIP para carga manual en Gemini Apps.

## No realizado deliberadamente
- No se copiaron ni procesaron documentos reales del directorio padre.
- No se descargaron documentos normativos ni se creó un índice vectorial; primero deben validarse vigencia, alcance, uso y responsable.
- No hubo conexión, envío, llamada, notificación ni escritura productiva.
- No se cargaron Skills en cuentas externas ni se verificó la activación en runtimes de Claude/Gemini instalados.
- No se emitió opinión legal ni se declaró exigible obligación alguna.

## Estado de preparación
El kit de inicio está listo para revisión técnica y pruebas offline con fixtures. El RAG normativo y cualquier regla bancaria operativa quedan condicionados a las entradas de MATRIZ_DECISIONES_PENDIENTES.md.
