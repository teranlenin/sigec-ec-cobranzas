# Diseño de RAG y memorias

## Memorias
- **Episódica:** eventos cronológicos append-only por caso/obligación, con canal simulado, resultado, fecha, fuente y agente.
- **Semántica:** hechos validados con valor, fuente, fecha, vigencia y estado.
- **Sistémica/procedimental:** políticas y normas versionadas con jurisdicción, vigencia, responsable, alcance y verificación.
- **Agéntica:** resumen temporal de señales observables del caso, con eventos soporte, cantidad, confianza, caducidad y corrección. No guarda emoción ni vulnerabilidad.

## Pipeline RAG
1. Registrar fuente, autoridad, jurisdicción, tipo, versión, alcance, acceso y aprobador.
2. Revisar permiso, vigencia, reformas, datos personales y pertinencia.
3. Conservar original/hash; extraer texto con página/sección.
4. Fragmentar por unidad documental y adjuntar fuente, ubicación y vigencia.
5. Recuperar con filtros de alcance; comparar contradicciones.
6. Responder con citas; abstenerse sin respaldo suficiente.
7. Registrar versión de corpus, consulta, fragmentos y QA.

No existe aún índice vectorial, motor ni corpus cargado. Elegir stack después de D-11 y aprobación de fuentes.
