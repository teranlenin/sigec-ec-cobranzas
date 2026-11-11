# Gestor de caso simulado

- **ID:** stpr-sandbox-case-manager
- **Skill:** .agents/skills/stpr-sandbox-case-manager/SKILL.md
- **Objetivo:** validar y registrar eventos sintéticos de forma append-only en pruebas locales.
- **Entradas:** evento con IDs, fuente, fecha, canal y banderas de simulación.
- **Salidas:** recibo de validación, evento aceptado o motivo de rechazo.
- **Límite:** no llama, envía, notifica ni escribe en CRM/ERP o sistemas productivos.
- **Permiso por defecto:** solo sandbox local.
