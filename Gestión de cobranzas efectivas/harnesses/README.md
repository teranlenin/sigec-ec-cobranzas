# Arranque por arnés

## Codex
La raíz del proyecto contiene AGENTS.md. Las Skills canónicas están en .agents/skills/. Verifica que las Skills del workspace aparezcan en el selector/runtime antes de usarlas.

## Claude Code
La raíz contiene CLAUDE.md. El espejo del proyecto está en .claude/skills/. Comprueba paridad ejecutando scripts/sync_claude_skills.py sin --write; el script no sobrescribe diferencias.

## Gemini CLI
La raíz contiene GEMINI.md. La ubicación de workspace .agents/skills/ es la ruta compartida documentada para el CLI. Verifica la carga con el comando /skills list o la utilidad de la versión instalada.

## Gemini Apps
Se generan 13 ZIP locales, uno por Skill, en dist/gemini_apps/. Cada archivo contiene SKILL.md en la raíz del paquete. La importación a una cuenta es manual y no se realiza desde este proyecto.

## Prueba de paridad
El contenido de la Skill debe coincidir con la fuente canónica en Codex/Gemini CLI y con el espejo en Claude Code. Cualquier adaptación específica del arnés debe ser mínima, revisada y no alterar procedimiento ni límites.
