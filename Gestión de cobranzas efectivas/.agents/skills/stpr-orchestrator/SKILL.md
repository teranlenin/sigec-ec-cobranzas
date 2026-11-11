---
name: stpr-orchestrator
description: Coordina tareas STPR, selecciona agentes y aplica puertas de control para simulación de cobranzas.
metadata:
  version: "0.1.0"
  owner: "STPR"
---

# Orquestador STPR

## Objetivo
Dirigir la solicitud por el flujo mínimo seguro y entregar resultado, evidencia, vacíos y siguiente responsable.

## Activación y entradas
Usar al iniciar una tarea STPR o consolidar salidas. Requiere intención, alcance, fecha de corte y, si aplica, case_id y obligation_id sintéticos.

## Procedimiento
1. Clasificar la tarea: arquitectura, RAG, evidencia, cumplimiento, privacidad, cartera, comunicación, sandbox o auditoría.
2. Identificar datos personales, efectos externos, decisiones jurídicas y permisos faltantes.
3. Enrutar primero a privacidad cuando existan datos; después a evidencia/RAG y compliance; luego analítica o borrador; auditoría antes de entregar.
4. Transferir solo identificadores sintéticos, campos necesarios y referencias, no duplicados de documentos.
5. Verificar en cada respuesta el estado de fuente, verificación, contradicciones y abstenciones.
6. Detenerse ante datos reales no autorizados, petición de contacto/producción, falta de evidencia crítica o riesgo no resuelto.
7. Informar plan seguido, resultado, límites y pendientes.

## Salida
Resumen estructurado, agentes/Skills usados, puertas satisfechas o fallidas, source_refs, vacíos y simulation=true.

## Límites y abstención
No ejecutar llamadas, envíos ni escrituras productivas; no asumir aprobación humana; no ocultar conflictos; no convertir sugerencias en hechos. Si una tarea requiere acción externa, proponer solo alternativa simulada.

## Pruebas de aceptación
- Pedido de envío real: detener, no transmitir y ofrecer borrador simulado.
- Evidencia contradictoria: derivar, no elegir por intuición.
- Pregunta normativa sin fuente vigente: abstenerse de concluir.

## Skills relacionadas
Cargar stpr-simulation-only siempre; stpr-data-minimization y stpr-evidence-provenance según el caso.
