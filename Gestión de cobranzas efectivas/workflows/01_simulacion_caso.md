# Workflow: caso simulado

**Entrada:** identificadores sintéticos, obligación y eventos de prueba, fecha de corte y fuentes registradas.  
**Salida:** resumen con hechos, fuentes, vacíos y, si procede, borrador **SIMULACIÓN — NO ENVIAR**.

1. Orquestador clasifica solicitud y confirma alcance simulado.
2. Privacidad valida que el caso esté marcado sintético y no contenga PII.
3. RAG recupera fuentes registradas y entrega ubicación y estado.
4. Analista de evidencia mapea hechos a soporte y muestra discrepancias.
5. Compliance marca reglas candidatas y escalamiento necesario.
6. Analista de cartera calcula métricas según fecha de corte.
7. Comunicaciones prepara borrador opcional, neutral y no coercitivo.
8. Gestor registra evento append-only solo en sandbox.
9. Auditor revisa etiqueta, fuentes, exactitud, tono y trazabilidad.
10. Orquestador entrega resultado y pendientes.

**Detenerse:** caso no sintético, identidad ambigua, fuente insuficiente, conflicto, dato sensible innecesario, pedido de contacto real o regla legal no verificada.
