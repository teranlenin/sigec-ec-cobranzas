# Paquete sintético de reportería cíclica — v2

> **Versión histórica intermedia, no utilizar.** Fue sucedida por `data/reporting_synthetic_v3/` para alinear la fecha base del aging con el inicio del período simulado. Esta carpeta se conserva para no borrar ni sobrescribir artefactos creados; la aplicación y el CLI oficiales apuntan a v3.

**Rótulo:** SIMULACIÓN — NO USAR EN PRODUCCIÓN  
**Semilla predeterminada:** `20261110` · **Zona del reloj simulado:** `America/Bogota`

## Contenido

- `cases.csv`: 1.000 cuentas ficticias con saldo de apertura, gestor sintético, mora de 1–560 días y tokens de contacto no utilizables.
- `events.jsonl`: libro de eventos ficticios append-only; incluye pagos, compromisos, intentos de canal no enviados, cambios tokenizados, hallazgos y disputas.
- `cycles.jsonl`: metadatos de los ciclos de simulación. El primer lote está fechado como semana inicial y no representa operación real.
- `reports/`: carpeta de salida para reportes semanales locales, si se solicita desde CLI.

## Ejecutar

Desde la raíz del proyecto:

```powershell
python "Gestión de cobranzas efectivas/scripts/generate_reporting_data.py" --mode validate
python "Gestión de cobranzas efectivas/scripts/generate_reporting_data.py" --mode cycle --cycle-id DEMO-CICLO-001
python "Gestión de cobranzas efectivas/scripts/generate_reporting_data.py" --mode weekly --from-date 2026-11-03 --to-date 2026-11-10
```

El bucle cada cinco minutos es explícito y se detiene con `Ctrl+C`; avanza un día de reloj **simulado** por ciclo:

```powershell
python "Gestión de cobranzas efectivas/scripts/generate_reporting_data.py" --mode loop --interval-seconds 300
```

Repetir el mismo `cycle_id` no agrega de nuevo sus eventos. No se crea tarea del sistema operativo ni proceso al iniciar sesión.

## Límites

No incluye datos reales ni direcciones/teléfonos/correos utilizables, no envía comunicaciones y no escribe en CRM/ERP. Los tokens `@example.invalid` y códigos `TEL-SYN-*` son marcadores para demostración. Los canales son registros didácticos de intentos no enviados. Los tramos DPD son categorías de analítica sintética, no estados legales o contables. No usar para decisiones sobre personas reales.
