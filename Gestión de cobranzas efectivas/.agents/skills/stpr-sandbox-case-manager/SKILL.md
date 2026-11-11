---
name: stpr-sandbox-case-manager
description: Valida y registra eventos sintéticos append-only en sandbox local sin conectarse a sistemas ni canales reales.
metadata:
  version: "0.1.0"
  owner: "STPR"
---

# Gestor de caso simulado

## Objetivo
Mantener una bitácora de prueba consistente, idempotente y auditable.

## Entradas
Evento con ID, case_id, obligation_id, fecha, canal, tipo, resultado, source_ref y synthetic/simulation true.

## Procedimiento
1. Confirmar que se trabaja en root local, sin endpoint, token o dataset productivo.
2. Validar esquema, enumeraciones, referencias y partición cliente/caso/obligación.
3. Rechazar PII innecesaria, atributos sensibles, emoción inferida o datos sin origen.
4. Comprobar event_id duplicado; devolver resultado previo en vez de insertar duplicado.
5. Añadir solo al log local de prueba cuando el flujo lo autorice; conservar el evento original.
6. Rectificar con evento compensatorio, nunca sobreescritura silenciosa.
7. Emitir recibo con ID, resultado de validación y referencias, sin datos sensibles.

## Salida
Aceptado/rechazado, simulation=true, recibo e historial de prueba.

## Límites y abstención
No transmitir SMS, correo, llamada o WhatsApp; no conectar ni escribir en CRM/ERP o producción.

## Pruebas de aceptación
Evento válido → append. ID duplicado → idempotente. synthetic=false → rechazo. Fuente ausente → rechazo. Endpoint real → detener.

## Skills relacionadas
stpr-simulation-only, stpr-data-minimization y stpr-evidence-provenance.
