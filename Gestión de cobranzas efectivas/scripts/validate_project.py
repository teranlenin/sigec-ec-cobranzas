#!/usr/bin/env python3
"""Validador estructural offline; no prueba cumplimiento jurídico ni calidad funcional del RAG."""
from pathlib import Path
import json
import sys
import ast
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ERRORS = []
SKILLS = [
    "stpr-orchestrator", "stpr-directory-architect", "stpr-rag-curator",
    "stpr-obligation-evidence", "stpr-ecuador-compliance", "stpr-privacy-data",
    "stpr-portfolio-analyst", "stpr-respectful-communications",
    "stpr-sandbox-case-manager", "stpr-auditor-evaluator",
    "stpr-simulation-only", "stpr-evidence-provenance", "stpr-data-minimization",
]
FORBIDDEN_KEYS = {"phone", "email", "telephone", "national_id", "cedula", "passport", "full_name"}

for name in SKILLS:
    path = ROOT / ".agents" / "skills" / name / "SKILL.md"
    if not path.exists():
        ERRORS.append(f"Falta Skill canónica: {path.relative_to(ROOT)}")
        continue
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or f"\nname: {name}\n" not in text:
        ERRORS.append(f"Frontmatter/nombre no válido: {path.relative_to(ROOT)}")
    if len(text) < 450:
        ERRORS.append(f"Skill demasiado breve: {path.relative_to(ROOT)}")
    mirror = ROOT / ".claude" / "skills" / name / "SKILL.md"
    if not mirror.exists() or mirror.read_bytes() != path.read_bytes():
        ERRORS.append(f"Espejo Claude Code ausente o desfasado: {mirror.relative_to(ROOT)}")

for rel in ("data/synthetic/cases.jsonl", "data/synthetic/events.jsonl"):
    path = ROOT / rel
    if not path.exists():
        ERRORS.append(f"Fixture faltante: {rel}")
        continue
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            item = json.loads(line)
        except Exception as exc:
            ERRORS.append(f"{rel}:{line_no}: JSON inválido: {exc}")
            continue
        if item.get("synthetic") is not True or item.get("simulation") is not True:
            ERRORS.append(f"{rel}:{line_no}: faltan banderas synthetic/simulation")
        if FORBIDDEN_KEYS.intersection({key.lower() for key in item}):
            ERRORS.append(f"{rel}:{line_no}: campo identificativo prohibido")
        if rel.endswith("cases.jsonl"):
            if not 15000 <= item.get("amount_usd", 0) <= 60000:
                ERRORS.append(f"{rel}:{line_no}: monto fuera de fixture")
            if not 120 <= item.get("days_past_due", 0) <= 400:
                ERRORS.append(f"{rel}:{line_no}: mora fuera de fixture")

for rel in (
    "rag/schemas/episodic_event.schema.json",
    "rag/schemas/semantic_case.schema.json",
    "rag/schemas/system_rule.schema.json",
    "rag/schemas/agentic_pattern.schema.json",
    "rag/schemas/reporting_case.schema.json",
    "rag/schemas/reporting_event.schema.json",
):
    try:
        json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as exc:
        ERRORS.append(f"{rel}: JSON inválido: {exc}")

if len(list((ROOT / "agents").glob("*.md"))) != 10:
    ERRORS.append("Se esperan exactamente diez definiciones de agente")

packages = list((ROOT / "dist" / "gemini_apps").glob("*.zip"))
if len(packages) != len(SKILLS):
    ERRORS.append(f"Se esperaban {len(SKILLS)} paquetes Gemini Apps; encontrados {len(packages)}")
for package in packages:
    try:
        with zipfile.ZipFile(package) as archive:
            if "SKILL.md" not in archive.namelist():
                ERRORS.append(f"Paquete sin SKILL.md en raíz: {package.name}")
            else:
                skill_text = archive.read("SKILL.md").decode("utf-8")
                if not skill_text.startswith("---\n"):
                    ERRORS.append(f"Frontmatter ausente en paquete: {package.name}")
    except Exception as exc:
        ERRORS.append(f"ZIP inválido {package.name}: {exc}")

policy = (ROOT / "config" / "simulation_policy.yaml").read_text(encoding="utf-8")
for required in ("external_delivery_enabled: false", "connectors_enabled: false", "write_enabled: false"):
    if required not in policy:
        ERRORS.append(f"Falta control de simulación: {required}")

for script in (ROOT / "scripts").glob("*.py"):
    try:
        ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
    except SyntaxError as exc:
        ERRORS.append(f"Error de sintaxis en {script.name}: {exc}")

for folder in (ROOT / "reporting", ROOT / "tests"):
    for source in folder.glob("*.py") if folder.exists() else []:
        try:
            ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        except SyntaxError as exc:
            ERRORS.append(f"Error de sintaxis en {source.relative_to(ROOT)}: {exc}")

REPORTING_DATA = ROOT / "data" / "reporting_synthetic_v3"
if (REPORTING_DATA / "cases.csv").exists() and (REPORTING_DATA / "events.jsonl").exists():
    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from reporting.simulation import validate_dataset
        summary = validate_dataset(REPORTING_DATA)
        if summary["min_dpd"] != 1 or summary["max_dpd"] != 560:
            ERRORS.append("La reportería sintética no cubre exactamente mora 1–560")
    except Exception as exc:
        ERRORS.append(f"Reportería sintética v3 inválida: {exc}")

if ERRORS:
    print("FAIL")
    print("\n".join(f"- {error}" for error in ERRORS))
    sys.exit(1)

print("PASS: Skills, espejos Claude, paquetes Gemini Apps, agentes, esquemas y fixtures validados estructuralmente.")
print("LÍMITE: no demuestra cumplimiento legal, calidad funcional del RAG ni preparación de producción.")
