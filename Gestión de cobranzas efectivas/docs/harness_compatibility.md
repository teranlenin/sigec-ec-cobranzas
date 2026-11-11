# Compatibilidad entre arneses de modelos

**Requisito del usuario:** poder trabajar este proyecto desde Codex, Claude Code y Gemini.  
**Revisión documental:** 2026-11-05. Las rutas y comandos pueden cambiar; comprobar versión y carga en la sesión antes de dar una Skill por operativa.

## Fuente canónica

- Mantener el contenido fuente de las Skills en .agents/skills/<skill-id>/SKILL.md, con frontmatter estándar, instrucciones neutrales respecto del proveedor y límites/procedimientos/pruebas.
- Las definiciones de agentes y los workflows son especificaciones portables en Markdown/YAML. No depender de que el arnés tenga subagentes, herramientas o APIs particulares.
- Las políticas de simulación viven en AGENTS.md y config/simulation_policy.yaml. Las instrucciones de entrada por arnés solo enlazan o resumen esas reglas; no pueden debilitarlas.

## Matriz

| Arnés | Instrucciones del proyecto | Descubrimiento de Skills | Acción de este bootstrap |
|---|---|---|---|
| Codex | AGENTS.md | .agents/skills/ | Canónico; verificar listado/activación en la sesión |
| Claude Code | CLAUDE.md | .claude/skills/<skill-id>/SKILL.md | Crear espejo desde .agents/skills/ y comprobar paridad |
| Gemini CLI | GEMINI.md | .agents/skills/ (alias de workspace documentado) | Usar fuente canónica; probar /skills list o comando equivalente en la versión local |
| Gemini Apps (web/escritorio) | Instrucciones de la sesión | Importación de Skill por carpeta/archivo/ZIP | El script de exportación genera paquetes individuales; la carga en cuenta es manual |

## Reglas de portabilidad

1. No incrustar nombres de herramientas, llamadas API, variables de entorno o rutas exclusivas del proveedor en el procedimiento común; usar un adaptador por arnés cuando haga falta.
2. Las Skills compartidas se referencian por ID; si un arnés no realiza carga automática, el prompt de sesión debe indicar cuál cargar.
3. Las diferencias de orquestación son adaptadores: una sesión puede ejecutar agentes secuencialmente como roles sin simular subagentes inexistentes.
4. La copia Claude es un derivado; no editarla directamente. Ejecutar scripts/sync_claude_skills.py --write para crear el espejo. El script se niega a sobrescribir diferencias existentes.
5. Validar en cada arnés: reconocimiento de Skills, instrucciones raíz, disponibilidad de archivos de apoyo, salida de abstención y límites de simulación.
6. No instalar Skills globalmente ni cargar contenido a cuentas externas como parte del bootstrap.
7. Para Gemini Apps, generar paquetes locales con scripts/export_gemini_apps_skills.py; la carga a la cuenta queda a cargo del usuario.

## Fuentes oficiales consultadas

- OpenAI, Skills: https://developers.openai.com/plugins/concepts/skills
- Anthropic, Skills de Claude Code: https://code.claude.com/docs/en/skills
- Google, Gemini CLI Skills: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md
- Google, Skills para Gemini Apps: https://support.google.com/gemini/answer/17094296?hl=en
