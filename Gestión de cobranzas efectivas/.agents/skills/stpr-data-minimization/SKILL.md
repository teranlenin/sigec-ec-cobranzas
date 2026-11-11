---
name: stpr-data-minimization
description: Reduce ingesta, persistencia y exposición de datos al mínimo necesario en flujos STPR.
metadata:
  version: "0.1.0"
  owner: "STPR"
---

# Minimización de datos STPR

## Procedimiento
1. Determinar finalidad y campos indispensables antes de leer o guardar datos.
2. Preferir datos sintéticos, agregados o anonimizados; no mostrar PII ni credenciales innecesarias.
3. Mantener separación de cliente, caso y obligación y controles por rol.
4. No inferir ni almacenar emociones, vulnerabilidades ni atributos sensibles para perfilado de cobranza.
5. Aplicar retención/corrección/eliminación conforme a política validada; si falta, usar solo fixtures y marcar pendiente.
6. Revisar logs, salidas y ejemplos para evitar divulgación accidental.

## Abstención
Datos reales sin finalidad/permiso verificado, mezcla de casos o solicitud de datos de terceros → detener, minimizar y escalar.

## Verificación
Inspeccionar campos, artefactos, logs y ejemplos antes de persistir o publicar.
