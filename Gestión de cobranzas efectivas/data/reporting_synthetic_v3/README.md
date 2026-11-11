# Paquete sintético de reportería cíclica — v3

**Rótulo:** SIMULACIÓN — NO USAR EN PRODUCCIÓN  
**Semilla predeterminada:** `20261110` · **Zona del reloj simulado:** `America/Bogota`

## Contenido

- `cases.csv`: 1.000 cuentas ficticias con saldo de apertura, gestor sintético, mora de 1–560 días y tokens de contacto no utilizables. La fecha de baseline es el inicio de la semana de simulación.
- `events.jsonl`: libro append-only de eventos ficticios con pagos, compromisos, intentos de canal no enviados, cambios tokenizados, hallazgos y disputas.
- `cycles.jsonl`: metadatos de ciclos. Un día simulado avanza por ciclo para acelerar las prácticas semanales.
- `reports/`: reportes semanales locales JSON/Markdown generados a solicitud.
- El módulo 8 del Streamlit vuelve a leer los datos cada cinco minutos mientras la vista está abierta; no genera eventos nuevos sin comando CLI o acción expresa en el botón.

## Ejecutar desde la raíz del proyecto

```powershell
python "Gestión de cobranzas efectivas/scripts/generate_reporting_data.py" --mode validate
python "Gestión de cobranzas efectivas/scripts/generate_reporting_data.py" --mode cycle --cycle-id DEMO-CICLO-001
python "Gestión de cobranzas efectivas/scripts/generate_reporting_data.py" --mode weekly --from-date 2026-11-03 --to-date 2026-11-10
```

El bucle cada cinco minutos es explícito y se detiene con `Ctrl+C`; cada ciclo añade un día **simulado**:

```powershell
python "Gestión de cobranzas efectivas/scripts/generate_reporting_data.py" --mode loop --interval-seconds 300
```

Repetir el mismo `cycle_id` no duplica eventos. No se crea tarea del sistema operativo ni proceso de inicio automático.

## Límites

No contiene datos reales ni direcciones/teléfonos/correos utilizables; no envía comunicaciones ni escribe en CRM/ERP. Los marcadores `@example.invalid` y `TEL-SYN-*` no son contactos. Los canales son intentos didácticos no enviados. Los tramos DPD son analíticos, no categorías jurídicas/contables. No usar para decisiones sobre personas reales.
