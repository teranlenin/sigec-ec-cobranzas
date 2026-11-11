# Plan de implementación

| Fase | Resultado | Estado | Puerta de control |
|---|---|---|---|
| 0. Aislamiento | Raíz STPR separada de archivos preexistentes | Hecha | Confirmar artefactos creados |
| 1. Arquitectura y portabilidad | Agentes, Skills, RAG, memorias, flujos, política sandbox y adaptadores Codex/Claude/Gemini | Hecha como borrador técnico | Revisión técnica y smoke test por arnés |
| 2. Fuentes y política | Fuentes oficiales y políticas institucionales con vigencia y aprobador | Pendiente | Jurídico/Compliance |
| 3. Corpus RAG | Ingestión autorizada, metadatos, versionado y citas | Pendiente | Validar cada fuente |
| 4. Prototipo offline | Recuperación sobre fuentes revisadas y fixtures sintéticos | Pendiente | Sin datos reales ni conectores |
| 5. Evaluación | Pruebas de citas, abstención, privacidad, sesgo y consistencia | Pendiente | Aprobar umbrales |
| 6. Simulación de casos | Recorridos sintéticos y registro sandbox | Pendiente | Revisión humana |
| 7. Preparación institucional | Informe de riesgos y controles antes de considerar cualquier otra fase | Pendiente | Aprobación separada |

Las Skills son portables a nivel de contenido, no se presume sincronización automática entre cuentas/herramientas. Consultar docs/harness_compatibility.md.

Completar decisiones normativas, de privacidad y de política interna antes de formar un corpus operativo. Un test aprobado no autoriza contacto externo ni producción.
