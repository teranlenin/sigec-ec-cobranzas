# Workflow: ingestión RAG

1. Registrar fuente en rag/source_registry.csv; no indexar directamente desde una conversación.
2. Revisar autoridad primaria, URL oficial, fecha, vigencia, reformas, alcance y permiso de uso.
3. Obtener visto bueno de Jurídico/Compliance para normas y de Privacidad para documentos con datos personales.
4. Después de aprobación, guardar copia inalterada en rag/corpus/approved/ con hash, fecha y responsable.
5. Extraer texto conservando página/sección; excluir o anonimizar PII antes de indexar.
6. Crear fragmentos con metadatos y referencias exactas; no fusionar versiones.
7. Probar recuperación, citas y abstención; documentar QA.
8. Publicar índice local versionado solo después de pasar puertas.

La carpeta del corpus está vacía intencionalmente.
