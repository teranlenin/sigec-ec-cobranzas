# Corte de estado: repositorios, memorias y reportería sintética

**Fecha de corte:** 2026-11-10 (America/Bogota)  
**Naturaleza:** inventario local y avance técnico; no es aprobación jurídica, institucional ni de producción.

## 1. Repositorios Git inspeccionados

| Ubicación | Rama / HEAD al inspeccionar | Estado antes del trabajo | Estado al cerrar este corte |
|---|---|---|---|
| Raíz `D:\MEGA\2026\LIDERAZGO\diplomado cobranzas` | Al inicio: `master` / `254755f`, limpia. Al cierre observado: `master` / `397ba41` (= `origin/master`). | Limpia al inicio. | Durante el trabajo apareció el commit `397ba41` (“feat: add Vercel static web edition…”), junto con `d7fc088` previo. No ejecuté manualmente `git commit` ni `git push`. Al cierre quedan cambios locales no confirmados en `.gitignore`, esta nota, el prompt maestro, `reporting/dashboard.py`, `reporting/metrics.py` y `tests/test_reporting.py`. |
| Worktree `D:\MEGA\2026\LIDERAZGO\diplomado cobranzas\.claude\worktrees\audit-collections-system-d0d0b6` | `claude/audit-collections-system-d0d0b6` / `68d421f` | Tenía el archivo no rastreado `AUDITORIA_SISTEMA_COBRANZAS.md`. | Sin cambios realizados en este worktree; el informe sigue no rastreado y no se considera código aprobado ni estado de la rama principal. |

No ejecuté manualmente `commit`, `push`, `reset`, `checkout`, `clean` ni integración de ramas. El worktree de auditoría no fue modificado por esta tarea.

## 2. Estado de memorias STPR y RAG

- El diseño documenta cuatro clases: episódica (eventos), semántica (hechos validados), sistémica/procedimental (reglas versionadas) y agéntica (patrones observables con fuente y caducidad).
- Existen cuatro esquemas JSON para esas memorias. El corpus RAG está vacío; no hay índice vectorial ni motor RAG configurado.
- Los fixtures STPR originales son pequeños ejemplos estructurales (tres casos y tres eventos), con mora definida en otro rango. No equivalen a memoria productiva ni se ampliaron con datos reales.
- La política local prescribe partición por caso/obligación, eventos append-only, correcciones compensatorias, ausencia de emociones/perfiles sensibles y uso solo sintético. La retención definitiva y varias decisiones institucionales continúan pendientes.
- El nuevo `events.jsonl` de reportería es un fixture temporal de entrenamiento, no una memoria agéntica, no se conecta a un usuario ni actualiza el corpus RAG.
- La validación estructural de Skills/espejos/paquetes/esquemas/fixtures STPR pasa localmente. Esto no prueba descubrimiento/activación de Skills en cuentas externas ni calidad funcional del RAG.

## 3. Estado del sistema y datos preexistentes

- `app_cobranzas.py` era un panel Streamlit con siete módulos, alimentado por una cartera estática en `datos_sinteticos/cartera_calibrada_multidimensional_1000.csv`; carga 1.000 filas, 62 columnas y un único corte visible (`2026-10-29`).
- En esa cartera heredada, `dias_mora` va de 1 a 1.071; no cubre el límite máximo de 560 solicitado como universo del nuevo ejercicio. No se modificó ni sobrescribió el CSV ni su XLSX.
- El módulo nuevo se agregó como opción 8. Los siete módulos anteriores permanecen sin refactor ni certificación en esta tarea. Sus etiquetas/perfiles y contenido normativo heredado no deben tomarse como aprobados para uso real.
- El HEAD observado también contiene una SPA estática en `public/`, un `vercel.json` y `public/data/cartera.json` (1.000 filas, 66 campos). Aunque el JSON está rotulado sintético y no contiene columnas de teléfono/correo/dirección, incluye edad, género autodeclarado, perfil neurocognitivo/cortisol, guiones, saldos y datos de gestión. El JS incluye un deep link a WhatsApp y carga Tailwind/Plotly desde CDN. Es una superficie pública potencial, distinta del módulo 8; no se verificó despliegue externo ni configuración de acceso. **No desplegar ni usar/publicar estos datos** sin revisión de privacidad/seguridad y autorización explícita.

## 4. Extensión sintética creada

- El conjunto vigente está en `data/reporting_synthetic_v3/`: 1.000 casos, 3.231 eventos, 20 gestores ficticios y mora cubierta de 1 a 560 días. El aging se referencia al inicio de la semana simulada.
- Incluye pagos totales/parciales, estados de compromisos, intentos de canal etiquetados como no enviados, cambios de contacto mediante tokens no enrutables, hallazgos ficticios y eventos de disputa/revisión.
- El log es append-only e idempotente por `cycle_id`. La semilla predeterminada es `20261110`; cada ciclo agrega una fecha al reloj simulado. El modo CLI de bucle está desactivado por defecto y se invoca explícitamente cada 300 segundos; no se instaló un servicio ni tarea programada.
- La reportería ofrece corte/período, indicadores financieros definidos, cumplimiento de compromisos, actividad de canal simulada, cambios de datos, tramos DPD y vistas de supervisión/gestor de entrenamiento. El módulo 8 vuelve a leer datos cada cinco minutos mientras está abierto; generar eventos requiere comando explícito o botón.
- Hay reportes semanales JSON/Markdown de ejemplo en `data/reporting_synthetic_v3/reports/`.
- `data/reporting_synthetic_v1/` y `data/reporting_synthetic_v2/` son artefactos intermedios conservados sin uso; sus README los marcan expresamente como **no utilizar**. La aplicación y los comandos oficiales apuntan a v3.

## 5. Pruebas ejecutadas y límites

- `python -m unittest discover -s "Gestión de cobranzas efectivas/tests" -v`: 5 pruebas PASS (tramos DPD, conciliación/tokenización, ciclo idempotente, fórmulas del reporte y JSON Schema).
- `scripts/generate_reporting_data.py --mode validate`: PASS; 1.000 casos, 3.231 eventos, DPD 1–560, pagos acumulados y asignación a componentes conciliados.
- Validación con JSON Schema 2020-12: PASS para 1.000 casos y 3.231 eventos.
- `scripts/validate_project.py`: PASS estructural (incluye Skills, espejos Claude, paquetes Gemini, fixtures y esquemas). Su propio aviso indica que no valida derecho, calidad del RAG ni producción.
- Prueba Streamlit `AppTest`: PASS; el panel principal carga sin excepciones y muestra el módulo 8 sin excepciones.
- No se mantuvo un bucle CLI activo durante cinco minutos (se verificó ciclo manual e idempotencia), no se probó la activación en Claude/Gemini, no se creó integración productiva, y no se ejecutaron tests con datos reales.
- El commit de SPA/Vercel está en `origin/master`; no se confirmó si un proveedor de despliegue está conectado. La presencia de `vercel.json` no prueba que la aplicación esté publicada.

## 6. Puertas pendientes

Continúan pendientes las políticas institucionales, aprobación de privacidad/retención, revisión de vigencia y alcance normativo, umbrales de aceptación, decisiones de responsables y cualquier autorización externa. La reportería construida es únicamente demostrativa y sintética; no debe utilizarse para asignar tareas o tomar decisiones sobre una cartera real.
