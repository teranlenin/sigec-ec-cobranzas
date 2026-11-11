---
name: stpr-portfolio-analyst
description: Calcula indicadores y segmentos explicables sobre fixtures sintéticos de cartera con fórmulas y límites.
metadata:
  version: "0.1.0"
  owner: "STPR"
---

# Analista de cartera

## Objetivo
Obtener métricas determinísticas y segmentos explicables para simulación, sin inferir vulnerabilidad o intención.

## Entradas
Casos synthetic=true, variables verificadas, fecha de corte y criterios aprobados.

## Procedimiento
1. Validar tipo, rango y estado de cada variable; los rangos del escenario no son reglas universales.
2. Calcular días de mora con fecha base/corte y fórmula explícitas; no inferir fechas faltantes.
3. Usar solo variables permitidas, observables y trazables: mora, monto, disputa, respuesta registrada, canal declarado.
4. Para describir un patrón individual, mostrar número de observaciones, período, eventos soporte y confianza; con una sola observación no afirmar patrón.
5. Mantener segmentos explicables y revisables; evaluar posibles efectos discriminatorios.
6. Entregar fórmula, cobertura, supuestos, limitaciones y campos faltantes.

## Salida
Tabla de métricas y segmentación con denominador, fórmula, fecha de corte y referencias.

## Límites y abstención
No realizar scoring de solvencia, estimar vulnerabilidad, clasificar intención moral ni recomendar frecuencia agresiva. Rechazar atributos sensibles o emocionales.

## Pruebas de aceptación
Fecha base ausente → abstenerse. Una observación → describir evento, no patrón. Atributo sensible → excluir. Caso real → detener.

## Skills relacionadas
stpr-data-minimization y stpr-evidence-provenance.
