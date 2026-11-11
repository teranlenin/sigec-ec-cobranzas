# Prompt maestro: evolución sintética de cartera, reportería cíclica y dashboard de cobranza

**Versión:** 1.0 · **Corte de preparación:** 2026-11-10 · **Proyecto:** STPR — Gestión de cobranzas efectivas  
**Modo obligatorio:** simulación aislada, datos sintéticos, sin efectos externos ni productivos.

## Rol y misión

Actúa como un equipo sénior de ingeniería de datos, analítica financiera, desarrollo de producto, privacidad y QA, coordinado por el agente `stpr-orchestrator`. Debes inspeccionar el sistema existente antes de cambiarlo y construir, dentro de la raíz confirmada del proyecto, una extensión local para generar eventos sintéticos de evolución de cartera, producir reportería cíclica y mostrarla en una interfaz dinámica para entrenamiento.

El resultado debe permitir ensayar, con datos ficticios y trazabilidad, cambios de saldo por pagos totales o parciales; compromisos de pago y su estado; cambios simulados de datos de contacto; uso de canales; y hallazgos de investigación ficticios. La interfaz debe servir a supervisores y gestores de entrenamiento. **No es un sistema de cobranza productivo, no contacta personas y no debe conectarse a una plataforma real.**

## Contexto y alcance semántico

Separa expresamente tres conceptos que no son intercambiables:

1. **Ciclo técnico de simulación:** generación o consolidación de un lote sintético cada cinco minutos, con identificador de ciclo, reloj de simulación configurable, reproducibilidad e idempotencia.
2. **Reporte de entrenamiento:** consulta dinámica de cambios desde el ciclo anterior y reportes ejecutivos/por gestor. Permite comparar períodos sin atribuir los datos a una operación real.
3. **Uso humano semanal:** el equipo puede revisar una síntesis semanal como ejercicio de capacitación. Esto no autoriza importar datos reales, sincronizar una plataforma ni recomendar acciones sobre clientes reales.

La nueva población debe cubrir días de mora de **1 a 560**, ambos incluidos. Esos tramos son etiquetas analíticas de antigüedad, no categorías legales, contables ni de exigibilidad. Para no confundirlos con los buckets antiguos, crea una nomenclatura versionada distinta, por ejemplo: `DPD_001_030`, `DPD_031_060`, `DPD_061_090`, `DPD_091_120`, `DPD_121_180`, `DPD_181_360`, `DPD_361_560`.

## Inspección inicial obligatoria (solo lectura)

Antes de escribir:

1. Confirma el directorio de trabajo y lee `AGENTS.md`, `README.md`, `00_CONTROL/ESTADO.md`, `00_CONTROL/PLAN_IMPLEMENTACION.md`, `00_CONTROL/MATRIZ_DECISIONES_PENDIENTES.md`, `config/simulation_policy.yaml`, `01_ARQUITECTURA/`, `rag/memory_policy.md`, los esquemas y las Skills relevantes.
2. Inventaría cada raíz Git encontrada: ruta, rama, HEAD, estado limpio/sucio, cambios no confirmados y relación entre ramas. No mezcles un worktree o rama de auditoría con la rama principal ni descartes cambios preexistentes. No hagas `checkout`, `reset`, `clean`, `rebase`, commit ni push.
3. Inspecciona `app_cobranzas.py`, sus dependencias, rutas de datos y módulos existentes. Identifica qué está implementado, qué estático o codificado a mano, qué persiste y qué falta. No confundas capturas, documentos de auditoría, fixtures o planes con funcionalidades ejecutables.
4. Revisa el esquema y perfil de la cartera sintética heredada, pero no la sobrescribas ni copies campos innecesarios. Mantén aislados los datos y resultados del nuevo ejercicio.
5. Si existen `public/`, `vercel.json`, exportadores JSON o configuración de hosting, revísalos como una superficie distinta. No publiques, despliegues, hagas `push` ni asumas control de acceso; comprueba que ningún dato o guion de gestión quede expuesto y que no haya enlaces/servicios de comunicación externa.
6. Registra hallazgos verificables, inferencias y pendientes por separado. Si algo no se puede comprobar en el código o en una prueba, márcalo como no verificado.

Si ya existe una salida con el nombre previsto, no la reemplaces: versiona el archivo o elige un nombre nuevo y documenta la decisión.

## Subagentes y Skills

Usa las Skills canónicas en `.agents/skills/`. Si el arnés permite subagentes, delega en paralelo solo trabajos independientes y limita cada transferencia a contexto mínimo, archivos pertinentes y criterios de aceptación. Si no permite subagentes, conserva estos roles como listas de revisión y no afirmes que fueron ejecutados.

| Rol / subagente | Skill canónica | Responsabilidad y salida |
|---|---|---|
| Orquestador | `stpr-orchestrator` | Secuencia fases, aplica puertas de control y mantiene la lista de pendientes. |
| Arquitectura y repositorio | `stpr-directory-architect` | Mapea repositorios, código, dependencias, rutas e integración no destructiva. |
| Analista de cartera/reportes | `stpr-portfolio-analyst` | Define métricas, fórmulas, cohortes y visualizaciones reproducibles; evita atributos sensibles. |
| Gestor de eventos sintéticos | `stpr-sandbox-case-manager` | Diseña eventos, transiciones de estado, reloj de simulación, append-only e idempotencia. |
| Privacidad/minimización | `stpr-privacy-data` + `stpr-data-minimization` | Revisa datos permitidos, minimización, riesgos de reidentificación y datos de contacto ficticios. |
| Evidencia y procedencia | `stpr-evidence-provenance` + `stpr-obligation-evidence` | Exige `source_ref`, estado de verificación, vínculo caso/obligación y consistencia temporal. |
| Cumplimiento Ecuador | `stpr-ecuador-compliance` | Identifica riesgos o cuestiones pendientes; no añade afirmaciones legales ni reglas no verificadas. |
| Curador RAG (condicional) | `stpr-rag-curator` | Interviene solo si una fuente documental aprobada resulta necesaria; no crea índice ni ingiere normas por iniciativa propia. |
| Auditor/evaluador independiente | `stpr-auditor-evaluator` | Ejecuta pruebas de esquema, invariantes, idempotencia, métricas, privacidad y calidad del informe. |
| Simulación únicamente | `stpr-simulation-only` | Comprueba aislamiento local, banderas sintéticas y ausencia de efectos externos. |
| Comunicación respetuosa (solo si aplica) | `stpr-respectful-communications` | Verifica que los eventos de canal sean registros ficticios; no redacta ni envía mensajes reales. |

El subagente auditor debe revisar los resultados sin aceptar como prueba el resumen del agente implementador. El agente principal conserva responsabilidad de integrar, resolver discrepancias y comunicar limitaciones.

## Contrato de datos y reglas de simulación

Diseña un modelo versionado de casos, eventos, snapshots e informes. Reutiliza los esquemas existentes solo si sus rangos y semántica son compatibles; no cambies silenciosamente los fixtures STPR actuales, que tienen otra cobertura de mora.

### Población sintética

- Como base inicial, usa una cohorte configurable de **1.000 casos sintéticos** solo si la inspección confirma que es viable; configura semilla aleatoria fija y permite variar el tamaño sin editar código.
- Genera identificadores opacos nuevos (por ejemplo `CASE-SYN-RPT-*`, `OBL-SYN-RPT-*`, `EVT-SYN-RPT-*`) y marca cada fila/evento `synthetic=true`, `simulation=true` y una etiqueta visible de simulación.
- Distribuye casos en los siete tramos `DPD_*`, incluye valores de 1 y 560 días, y valida la cobertura. No fabriques nombres, cédulas, domicilios reales ni datos de contacto utilizables.
- Si se necesita demostrar una actualización de domicilio, teléfono o correo, guarda tokens ficticios no enrutable/no entregables (p. ej. `ADDR-SYN-001-v2`, `TEL-SYN-001-v2`, `EMAIL-SYN-001-v2@example.invalid`). La base no contendrá datos personales reales ni números marcables.
- No uses edad, género, etnia, salud, emociones, supuestos rasgos psicológicos, “neuroperfiles”, vulnerabilidad ni proxies sensibles. No reutilices score de solvencia, “probabilidad calibrada” o estrategias de presión del paquete legado para priorizar gestores.

### Eventos y estados

Cada evento debe contener, como mínimo: `event_id`, `case_id`, `obligation_id`, `cycle_id`, `occurred_at` (reloj simulado con zona horaria), `event_type`, `source_ref`, `verification_status`, `actor_simulated`, `synthetic`, `simulation` y versión de esquema. El log es append-only; una corrección agrega un evento compensatorio, nunca reescribe el original. La repetición de un ciclo no debe duplicar eventos.

Incluye tipos controlados y documentados para:

- pago total o parcial, con monto positivo, fecha simulada y asignación transparente a componentes del saldo;
- compromiso creado, aceptado, pendiente, cumplido, incumplido, cancelado o reprogramado, distinguiendo estados observados/declarados/simulados y sin marcar como incumplido antes de vencer;
- intento de canal simulado y resultado (p. ej. borrador generado/no enviado, respuesta ficticia o sin respuesta simulada), claramente distinto de una comunicación efectivamente entregada;
- cambio/hallazgo de dato de contacto por campo, con valor tokenizado, procedencia y estado de verificación;
- nuevo hallazgo de investigación ficticio, indicando origen simulado y evidencia de soporte, sin convertir una declaración en hecho verificado;
- apertura/cierre de disputa y revisión interna, aplicando una bandera de abstención a cualquier sugerencia de contacto.

Valida invariantes financieras: montos no negativos; pagos no mayores al saldo aplicable; saldo final nunca negativo; componentes conciliados; reducción por pago separada de ajustes hipotéticos; ningún cargo, condonación o quita aparece como autorizado sin un evento explícito de escenario. No infieras efecto contable, jurídico o de exigibilidad.

## Métricas y reportería

Documenta definición, numerador, denominador, ventana temporal, filtros y limitaciones para cada KPI. Como mínimo incluye:

- saldo inicial/final y reducción, separados por principal, interés y otros componentes cuando la fuente sintética los permita;
- monto y número de pagos totales/parciales; recuperación del período y tasa de recuperación con denominador explícito;
- compromisos creados, vencidos, pendientes, cumplidos e incumplidos; tasa de cumplimiento solo sobre compromisos vencidos y resolubles, excluyendo pendientes;
- casos con cambios/hallazgos de contacto, por campo y estado de verificación;
- distribución de intentos **simulados** por canal y resultado, sin confundir intentos con entregas ni aperturas con pagos;
- saldo y casos por tramo DPD, cambios entre cortes y casos que salen/entran de tramo; define denominadores y ventana de observación;
- calidad de datos, eventos sin procedencia, disputas y errores de conciliación.

Presenta dos vistas: (a) **supervisión**, con resumen de cartera, evolución, conciliación, mezcla de canales simulados y alertas de calidad; (b) **gestor en entrenamiento**, con cartera ficticia asignada, eventos del período y detalle de compromisos. Permite filtros por corte, período, tramo DPD, gestor sintético y canal simulado. No generes ranking punitivo ni recomendaciones de presión. Si no hay evidencia suficiente, muestra “dato no disponible” y no sustituyas por ceros.

Genera reportes del ciclo de cinco minutos y una vista semanal seleccionable (zona horaria `America/Bogota`). Muestra fecha de corte, rango cubierto, hora de generación, versión del generador/esquema, semilla, cobertura, conteos de advertencias y etiqueta **SIMULACIÓN — NO USAR EN PRODUCCIÓN**. Separa acumulados, variaciones del período y valores de corte. Exportaciones locales CSV/JSON/Markdown deben conservar la etiqueta y no contener secretos.

## Arquitectura e implementación

- Extiende el panel existente de Streamlit de forma modular; no dupliques el dashboard ni rompas sus siete módulos existentes. Ubica el código y los datos nuevos tras inspeccionar la estructura real.
- La SPA estática y su configuración de hosting, si existen, no son equivalentes a la reportería dinámica local. No publiques ni expongas JSON de cartera, perfiles, guiones o datos de gestión; no uses enlaces de WhatsApp/SMS/correo/llamada ni recursos externos en una ruta que se presenta como sandbox.
- Conserva Python/pandas/Streamlit si ya son compatibles. No migres base de datos, agregues proveedor cloud ni elijas un motor RAG por inferencia. Usa almacenamiento local de simulación claramente separado; justifica cualquier dependencia nueva.
- Separa generador, validación, agregación de reportes y presentación. Admite modo `--once`/ejecución manual para prueba y un modo de intervalo de 300 segundos explícito. El ciclo recurrente debe estar desactivado por defecto, sin servicio de fondo, inicio automático, tarea programada del sistema operativo ni llamadas de red.
- Define el reloj/semilla de simulación para producir los mismos resultados con la misma configuración. Distingue `simulation_time` de la hora real de generación.
- No añadas conectores, credenciales, telemetría externa, escritura en CRM/ERP, ni llamadas a SMS, teléfono, WhatsApp, correo u otros canales. La palabra “canal” representa exclusivamente un evento ficticio en sandbox.
- Mantén intactos CSV, XLSX, PDFs, documentos, prompts y respaldos existentes. Crea nuevos artefactos con nombres versionados en la carpeta más adecuada del proyecto.

## Plan de trabajo obligatorio

1. **Diagnóstico:** entrega mapa de repositorios/memorias, estado del código, contratos actuales, divergencias y riesgos.
2. **Diseño:** presenta diccionario de eventos/KPIs, esquema nuevo, estrategia de versionado, almacenamiento y decisiones técnicas. Conserva sin cambios el baseline histórico.
3. **Generación:** crea una población sintética reproducible y eventos con todos los estados relevantes; guarda muestras legibles y etiqueta cada salida.
4. **Consolidación:** implementa cálculo idempotente de snapshots por ciclo y reportes semanales sin reescritura del log.
5. **Interfaz:** integra las vistas para supervisor y gestor de entrenamiento con filtros, series temporales, exportación y estados vacíos/errores visibles.
6. **Validación independiente:** ejecuta validadores existentes y nuevos tests; compara CSV/eventos/snapshots con cálculos manuales reproducibles.
7. **Cierre:** informa artefactos exactos, comandos de ejecución, pruebas ejecutadas, hallazgos, limitaciones, estado Git y decisiones que siguen pendientes. No hagas commit ni despliegue salvo petición expresa.

## Pruebas de aceptación mínimas

- La cartera sintética cubre mora mínima 1 y máxima 560, todos los tramos, y ninguna fila está fuera de rango.
- JSON/CSV cumplen esquemas y tienen marcadores sintéticos; escaneo de campos/valores confirma ausencia de PII utilizable, credenciales y datos reales.
- Pagos, saldos, estados de compromisos y agregados cuadran en casos de prueba de control (sin evento, pago parcial, pago total, compromiso pendiente/cumplido/incumplido, dato hallado sin verificar y disputa abierta).
- Ejecutar dos veces el mismo `cycle_id` no duplica eventos ni altera el resultado del reporte.
- Un evento de corrección conserva el valor previo y la procedencia; un dato no verificado no aparece como verificado.
- “Intento de canal simulado” nunca se cuenta como mensaje/llamada entregada.
- El reporte de cinco minutos y el semanal muestran ventanas diferentes, zona horaria y denominadores; métricas vacías se muestran como no disponibles.
- El dashboard no consume campos prohibidos ni ejecuta efectos externos. Las rutas nuevas permanecen separadas de las bases heredadas.
- Ejecuta `python scripts/validate_project.py` y los nuevos tests pertinentes. Un PASS estructural no se presenta como aprobación jurídica, institucional ni de producción.

## Criterio de detención y entrega

Si para implementar hiciera falta un dato real, credencial, política institucional, interpretación jurídica o conexión productiva, no lo simules como hecho ni lo solicites para seguir con la parte local: crea un pendiente y continúa lo independiente. Ante contradicción, falta de procedencia, disputa o error financiero, marca el dato y abstente de presentar una conclusión.

Al finalizar entrega una nota breve con: **qué se verificó**, **qué se creó**, **qué pruebas pasaron/fallaron**, **qué quedó sin hacer** y **por qué**. Distingue siempre prototipo, fixture, resultado calculado y validación aprobada. No digas que el sistema está listo para producción.
