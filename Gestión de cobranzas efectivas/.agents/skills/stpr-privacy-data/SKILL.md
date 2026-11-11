---
name: stpr-privacy-data
description: Evalúa finalidad, minimización, permisos, retención y riesgos antes de procesar datos de STPR.
metadata:
  version: "0.1.0"
  owner: "STPR"
---

# Responsable de privacidad y datos

## Objetivo
Determinar si los datos son aptos para la tarea simulada y reducir exposición antes de análisis, memoria, RAG o reporte.

## Entradas
Dataset/origen, finalidad declarada, clasificación, permisos/base validados, audiencia y retención prevista.

## Procedimiento
1. Clasificar material como sintético, público, confidencial o personal; no reproducir PII en el informe.
2. Comprobar necesidad de cada campo respecto de la finalidad; minimizar o anonimizar antes del uso.
3. No presuponer que una relación contractual o consentimiento genérico permite todo uso, perfilado o finalidad ulterior.
4. Revisar acceso, transferencia, retención, corrección, supresión y posibles decisiones automatizadas; señalar reglas por confirmar.
5. Permitir solo fixtures sintéticos locales hasta que la base y la finalidad de datos reales hayan sido verificadas por responsables.
6. Documentar hallazgos y derivar a Privacidad/Jurídico/Seguridad.

## Salida
Apto/no apto/condicionado, campos minimizados, riesgos, base/finalidad por verificar y aprobador.

## Límites y abstención
No emitir conclusión legal de licitud. No almacenar emociones, vulnerabilidades, salud u otros atributos sensibles en memoria agéntica.

## Pruebas de aceptación
Fixture sintético sin PII → continuar. Teléfono/correo real → cuarentena. Propósito indefinido → detener. Acceso no autorizado → escalar.

## Skills relacionadas
stpr-data-minimization.
