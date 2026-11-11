# Workflow: actualización de memoria en sandbox

1. Recibir evento observado o declarado con source_ref.
2. Validar synthetic=true, simulation=true, IDs, fecha, canal y esquema.
3. Distinguir declaración, observación e inferencia; rechazar atributos sensibles o emociones inferidas.
4. Proponer actualización semántica/agéntica con evento soporte, confianza, ventana y expiración.
5. Validar event_id e idempotencia; no sobrescribir evento original.
6. En pruebas autorizadas, añadir evento al log local de fixtures.
7. Auditar origen, estado anterior/nuevo, regla y ausencia de PII.

No hay almacenamiento en tiempo real conectado. Nunca se actualizan bases productivas.
