# Workflow principal de simulación

Solicitud → orquestador clasifica intención/riesgo → puerta de simulación y root → privacidad → RAG/evidencia → cumplimiento → cartera → borrador opcional → evento sandbox si autorizado → auditoría → respuesta con fuentes, vacíos y estado de revisión.

## Traspasos mínimos
Cada agente transfiere solo identificadores sintéticos, referencias de fuente y campos necesarios. Las salidas deben incluir case_id, obligation_id, source_refs, verification_status, simulation=true y next_owner; si hay abstención, también abstention_reason.

## Rutas de excepción
- Identidad/obligación dudosa: detener y pedir verificación; no mezclar expedientes.
- Disputa/reclamo o contradicción: preservar eventos y derivar a revisión humana.
- Fuente no vigente o no primaria: marcar candidata; no usar para conclusión normativa.
- Canal no autorizado o solicitud de contacto real: abstenerse; no hay conectores.
- Actualización de patrón: registrar como propuesta con eventos soporte, confianza y expiración; no inferir emociones.
- Evidencia insuficiente: explicar vacío y evidencia necesaria.
