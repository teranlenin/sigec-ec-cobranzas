---
name: stpr-auditor-evaluator
description: Audita evidencia, privacidad, tono, trazabilidad, límites de simulación y pruebas de entregables STPR.
metadata:
  version: "0.1.0"
  owner: "STPR"
---

# Auditor y evaluador

## Objetivo
Emitir hallazgos reproducibles antes de entregar el resultado; rechazar fallas críticas.

## Entradas
Artefacto, fuentes, políticas, criterios de aceptación, salida de Skills y logs de prueba.

## Procedimiento
1. Confirmar alcance y Skills usadas.
2. Contrastar afirmaciones con fuente, ubicación, fecha, estado y alcance.
3. Buscar PII, mezcla entre obligaciones, falta de etiqueta simulada y efectos externos.
4. Revisar tono por engaño, amenaza, divulgación o presión; revisar patrones por variables prohibidas.
5. Ejecutar pruebas estructurales disponibles y distinguirlas de pruebas funcionales o legales.
6. Reportar cada hallazgo con severidad, evidencia, impacto, corrección y PASS/FAIL/BLOCKED.
7. Rechazar salida con riesgo crítico; no declarar aprobación institucional.

## Salida
Informe de auditoría, lista de pruebas ejecutadas, fallas, límites y pendientes.

## Límites y abstención
Un validador local no certifica cumplimiento legal, calidad de RAG ni seguridad integral.

## Pruebas de aceptación
Cita ausente → FAIL. Borrador sin etiqueta → FAIL. Fixture válido → PASS estructural solamente. Duda jurídica → BLOCKED y derivar.

## Skills relacionadas
stpr-evidence-provenance, stpr-simulation-only y stpr-data-minimization.
