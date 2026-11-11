---
name: stpr-directory-architect
description: Analiza y estructura el directorio STPR, crea artefactos locales no destructivos dentro de la raíz autorizada.
metadata:
  version: "0.1.0"
  owner: "STPR"
---

# Analista de directorio y arquitectura

## Objetivo
Inspeccionar el proyecto, definir su arquitectura y preparar artefactos únicamente dentro de la raíz STPR confirmada.

## Entradas y precondiciones
Ruta absoluta, alcance, AGENTS.md u otras instrucciones locales. Si se analiza una carpeta existente, iniciar en solo lectura.

## Procedimiento
1. Confirmar ruta real y que el destino sea la raíz de STPR; no suponer carpetas por nombre.
2. Leer instrucciones locales y observar nombres/tipos/tamaños sin volcar secretos o PII.
3. Distinguir artefactos STPR de documentación/cartera real ajena al proyecto y excluir esta última.
4. Proponer árbol y dependencias; marcar incógnitas en vez de inventarlas.
5. Con autorización explícita de ejecución local, crear archivos nuevos de alcance dentro del root.
6. Antes de cada escritura, revisar colisión; nunca sobrescribir, mover o eliminar originales.
7. Ejecutar validadores pertinentes y reportar rutas, pruebas, conflictos y pendientes.

## Salida
Inventario breve, arquitectura, manifiesto de cambios y resultado de QA.

## Límites y abstención
No acceder a rutas ajenas al root, seguir enlaces fuera del root, copiar expedientes, revelar credenciales o hacer modificaciones destructivas. Ruta ambigua o destino ocupado con contenido distinto: detener escritura y reportar.

## Pruebas de aceptación
- Root no confirmado: no escribir.
- Archivo existente: preservar y reportar colisión.
- Root correcto: crear solo artefactos nuevos del alcance y validar estructura.

## Skills relacionadas
stpr-simulation-only y stpr-data-minimization.
