# STPR — Gestión de cobranzas efectivas

**STPR:** Especificación técnica del producto requerido. Proyecto de simulación auditable de gestión prejudicial de cartera bancaria ecuatoriana; no es una herramienta operativa de cobro.

## Estado
- Bootstrap local con arquitectura, diez agentes, trece Skills, flujos, esquemas y fixtures sintéticos.
- Sin conexiones a sistemas productivos ni canales de comunicación.
- No se incorporaron documentos ni datos reales de deudores.
- Fuentes normativas registradas como candidatas, pendientes de revisión de vigencia y aplicabilidad.

## Inicio
1. Lee 00_CONTROL/ESTADO.md y 00_CONTROL/PLAN_IMPLEMENTACION.md.
2. Revisa 01_ARQUITECTURA/ y las Skills bajo .agents/skills/.
3. Ejecuta python scripts/validate_project.py para comprobar estructura y fixtures.

## Escenario
Prueba con cartera completamente sintética de micro y pequeñas empresas, USD 15.000–60.000, mora 120–400 días. Toda comunicación es un borrador con la etiqueta **SIMULACIÓN — NO ENVIAR**; los eventos se registran solo en sandbox.

## Pendientes para avanzar
Políticas vigentes de la entidad, revisión jurídica de fuentes, responsable de privacidad y aprobaciones, criterios de evaluación y decisión del stack RAG. Ver matriz en 00_CONTROL/MATRIZ_DECISIONES_PENDIENTES.md.

## Arneses
El contenido común está preparado para Codex, Claude Code y Gemini CLI. Para Claude Code existe una capa espejo de Skills; Gemini Apps requiere importación manual. Consulta docs/harness_compatibility.md y valida la carga en cada versión instalada.

## Reportería sintética de entrenamiento (2026-11-10)
Se añadió el módulo 8 al panel Streamlit principal (`app_cobranzas.py`) y un generador local en `scripts/generate_reporting_data.py`. El conjunto v3 contiene 1.000 cuentas ficticias con mora de 1–560 días, eventos append-only y reportes de ejemplo; no sustituye los fixtures STPR originales ni el CSV heredado.

Desde la raíz del repositorio principal:

```powershell
streamlit run app_cobranzas.py
python "Gestión de cobranzas efectivas/scripts/generate_reporting_data.py" --mode validate
python "Gestión de cobranzas efectivas/scripts/generate_reporting_data.py" --mode weekly
python "Gestión de cobranzas efectivas/scripts/generate_reporting_data.py" --mode loop --interval-seconds 300
```

El modo `loop` solo se ejecuta por invocación explícita y simula un día por ciclo; no crea tareas programadas ni se conecta a sistemas reales. Con el módulo 8 abierto, la vista vuelve a leer los datos cada cinco minutos; la generación sigue siendo explícita. Consulta `00_CONTROL/ESTADO_MEMORIA_Y_REPORTERIA_2026-11-10.md` y `data/reporting_synthetic_v3/README.md` para alcance, definiciones y límites.
