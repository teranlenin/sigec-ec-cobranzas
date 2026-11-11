---
name: stpr-simulation-only
description: Mantiene todos los flujos STPR en simulación local e impide contactos, envíos e integraciones productivas.
metadata:
  version: "0.1.0"
  owner: "STPR"
---

# Solo simulación STPR

## Alcance
Obligatoria en todos los agentes y workflows.

## Procedimiento de control
1. Confirmar que dataset y caso llevan synthetic=true y simulation=true.
2. Confirmar que el destino es el sandbox local bajo la raíz del proyecto.
3. Confirmar que no se invocarán conectores, URLs de entrega, CRM/ERP, telefonía, correo ni canales de mensajería.
4. Marcar cualquier borrador como “SIMULACIÓN — NO ENVIAR”.
5. Registrar cambios de prueba de forma append-only y auditable.

## Límites
No contactar, enviar, programar, notificar, pagar, alterar producción ni inferir que un test autoriza operación real.

## Abstención
Credenciales, endpoint productivo, contacto real, escritura externa o datos no sintéticos → detener, no ejecutar y explicar alternativa segura.

## Verificación
Comprobar banderas, root, ausencia de conector y etiqueta; reportar límites de cualquier prueba.
