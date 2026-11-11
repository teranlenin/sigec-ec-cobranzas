---
name: stpr-rag-curator
description: Registra, prepara y evalúa fuentes autorizadas para RAG con citas, procedencia, versión y vigencia.
metadata:
  version: "0.1.0"
  owner: "STPR"
---

# Curador documental y RAG

## Objetivo
Diseñar e implementar ingestión controlada para fuentes autorizadas, con recuperación verificable y abstención.

## Entradas
Fuente/origen, URL, jurisdicción, versión/fecha, alcance, autorización de uso y aprobador.

## Procedimiento
1. Comprobar que la fuente esté registrada; verificar autoridad primaria, integridad, fecha, reformas y ámbito.
2. Rechazar o poner en cuarentena fuentes sin procedencia, con datos personales no autorizados o versiones ambiguas.
3. Mantener original inalterado; cuando haya ingestión, registrar hash, fecha de captura y responsable.
4. Extraer texto conservando página, artículo, sección y estructura; marcar contenido ilegible u OCR incierto.
5. Fragmentar por unidad documental y enlazar cada fragmento a fuente y ubicación exactas.
6. Recuperar con filtros de jurisdicción, vigencia y tipo de fuente; exponer contradicciones.
7. Responder solo con respaldo localizable. Registrar versión del índice y probar citas/abstención.

## Salida
Metadatos, fragmentos citables, estado de revisión, vacíos y reporte de QA.

## Límites y abstención
No elevar una fuente secundaria o antigua a norma vigente. No indexar contratos/cartera reales sin aprobación, minimización y anonimización. Si falta fuente primaria suficiente, abstenerse.

## Pruebas de aceptación
Fuente sin fecha → cuarentena. Cita sin ubicación → falla. Pregunta sin soporte → abstención. Dos versiones incompatibles → mostrar conflicto y derivar.

## Skills relacionadas
stpr-evidence-provenance y stpr-data-minimization.
