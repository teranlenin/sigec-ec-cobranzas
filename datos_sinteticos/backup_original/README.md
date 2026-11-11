# Paquete didáctico de cobranzas — SIMULACIÓN

- `cartera_demo_1000.csv`: 1.000 casos sintéticos; ID aleatorios, sin nombres, cédulas, teléfonos ni direcciones.
- `prompt_maestro_cobranza.json`: instrucciones para análisis asistido por IA y NotebookLM.

## Límites
Todas las filas, montos, respuestas, etiquetas, fechas y probabilidades son inventados para demostración; no corresponden a clientes ni a resultados observados. Las probabilidades y acciones demostrativas no están calibradas y no sirven para contacto, scoring productivo, decisiones crediticias, reporte a burós ni acciones legales. El CSV no contiene un registro cronológico real: `hist_pagos_12m` es una secuencia didáctica mensual sintética. No se incluye PII. Para uso real: gobernanza, base jurídica, minimización, controles de acceso, evaluación de sesgo, validación y aprobación humana; contrastar toda norma en fuente oficial vigente.

## Diccionario resumido
`id_caso` identificador ficticio; `saldo_usd`, `capital_usd`, `interes_mora_usd` valores simulados; `hist_pagos_12m` arreglo JSON de 12 estados sintéticos; `prob_pago_30d_demo` probabilidad inventada por fórmula heurística; `recuperacion_esperada_30d_usd_demo` saldo x probabilidad; `*_demo`/`*_simulado` campos no validados. `motivo_declarado` es una declaración ficticia, no hecho verificado.
