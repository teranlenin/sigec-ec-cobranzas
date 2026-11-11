# Arquitectura objetivo

## Componentes
1. **Interfaz de simulación:** recibe instrucciones y muestra evidencia, vacíos y borradores etiquetados. Sin conectores de envío.
2. **Orquestador:** selecciona agentes/Skills con permisos mínimos y detiene el flujo en puertas de control.
3. **Capa de políticas:** config/simulation_policy.yaml aplica límites de simulación, autorización, canales y revisión humana.
4. **RAG:** ingesta de fuentes autorizadas → extracción → fragmentación → metadatos → recuperación → respuesta citada. Ninguna fuente normativa pasa al índice sin registro y revisión.
5. **Memorias:** episódica (eventos), semántica (hechos de caso), sistémica (reglas versionadas) y agéntica (patrones observables con origen y expiración), separadas por caso y obligación.
6. **Sandbox:** append-only local para pruebas; sin conexión a CRM/ERP o servicios externos.
7. **Evaluación/auditoría:** pruebas de exactitud, procedencia, abstención, privacidad, no coerción y control de efectos.

## Límites de decisión
- La IA puede organizar evidencia, calcular métricas determinísticas y preparar simulaciones.
- La IA no determina por sí sola exigibilidad, prescripción, acción judicial, contacto real, concesión de acuerdos ni afectación de derechos.
- Toda regla normativa o política interna debe incluir fuente, vigencia, responsable, alcance y estado de revisión.
- El patrón individual se limita a eventos observados (canal declarado, respuesta registrada, promesa cumplida/incumplida); no es una etiqueta emocional ni una decisión automática.

## Topología
Solicitud → orquestador → privacidad → RAG/evidencia → compliance → cartera → borrador simulado → sandbox (si aplica) → auditor → respuesta con fuentes y límites.
