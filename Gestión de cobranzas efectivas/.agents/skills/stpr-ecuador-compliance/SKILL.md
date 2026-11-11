---
name: stpr-ecuador-compliance
description: Mapea fuentes primarias ecuatorianas, vigencia y alcance de reglas para revisión humana de cumplimiento.
metadata:
  version: "0.1.0"
  owner: "STPR"
---

# Revisor de cumplimiento Ecuador

## Objetivo
Identificar normas/políticas que deben verificarse y documentar incertidumbre sin sustituir un dictamen jurídico.

## Entradas
Pregunta delimitada, tipo de entidad/operación, fecha relevante y fuentes oficiales registradas.

## Procedimiento
1. Precisar jurisdicción, entidad, producto, acto y fecha; si falta alguno, marcar alcance no determinado.
2. Priorizar Registro Oficial, organismo de control y fuentes primarias consolidadas.
3. Comprobar publicación, reformas, vigencia temporal, jerarquía y ámbito material.
4. Separar texto fuente, resumen operativo, interpretación provisional y punto no resuelto.
5. Mantener estado candidate, checked o approved_by_human; solo el último puede alimentar una regla interna final.
6. Escalar conflictos, prescripción, exigibilidad, judicialización e interpretación controvertida.

## Salida
Matriz fuente/regla/fecha/alcance/estado/limitación/revisor con citas localizables.

## Límites y abstención
No inventar artículos ni generalizar reglas de concesión digital a toda entidad bancaria. No emitir opinión legal concluyente. Fuente antigua, parcial o secundaria: marcar no verificada.

## Pruebas de aceptación
Fuente antigua → vigencia pendiente. Alcance sectorial no coincide → no aplicar. Fuentes en conflicto → derivar. Sin texto primario → no presentarlo como verificado.

## Skills relacionadas
stpr-evidence-provenance y stpr-simulation-only.
