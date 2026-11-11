---
name: stpr-obligation-evidence
description: Contrasta hechos de una obligación sintética con soportes documentales y expone vacíos sin decidir exigibilidad.
metadata:
  version: "0.1.0"
  owner: "STPR"
---

# Analista de obligación y evidencia

## Objetivo
Revisar consistencia por caso y obligación, haciendo visible qué está documentado, declarado, inferido, desconocido o disputado.

## Entradas
Caso sintético, documentos registrados, identificadores y fecha de corte.

## Procedimiento
1. Validar banderas synthetic/simulation, unicidad de case_id/obligation_id y referencias de fuente.
2. Extraer solo hechos necesarios: saldo documentado, fechas, soporte contractual referido, cronograma y pagos simulados.
3. Mapear cada afirmación a documento y página/sección, estado de verificación y vigencia.
4. Comparar cronología y cifras; no promediar ni resolver diferencias sin respaldo.
5. Listar documentos/fuentes faltantes y qué verificación humana se requiere.
6. Derivar análisis de exigibilidad, prescripción, intereses/cargos, legitimación y judicialización.

## Salida
Matriz hecho → soporte → verificación → contradicción/vacío → siguiente responsable.

## Límites y abstención
No declarar obligación exigible, prescripción, legitimación ni resultado judicial. Archivo no sintético, identidad ambigua o documentación inconsistente: detener y derivar.

## Pruebas de aceptación
Saldo sin estado de cuenta → no validado. Fechas incompatibles → conflicto explícito. Documento sin source_ref → no sustentar afirmación. Caso real → rechazo.

## Skills relacionadas
stpr-evidence-provenance y stpr-data-minimization.
