#!/usr/bin/env python3
"""Empaqueta una Skill por ZIP para importación manual en Gemini Apps."""
from pathlib import Path
import argparse
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".agents" / "skills"
DEST = ROOT / "dist" / "gemini_apps"

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Crear paquetes ZIP locales.")
    args = parser.parse_args()
    skills = sorted(SOURCE.glob("*/SKILL.md"))
    if not skills:
        print("No se encontraron Skills canónicas.")
        return 1
    pending = []
    for skill_file in skills:
        archive = DEST / f"{skill_file.parent.name}.zip"
        if archive.exists():
            with zipfile.ZipFile(archive) as zf:
                existing = zf.read("SKILL.md") if "SKILL.md" in zf.namelist() else None
            if existing != skill_file.read_bytes():
                pending.append(f"Paquete existente distinto; no sobrescrito: {archive.relative_to(ROOT)}")
            continue
        if args.write:
            DEST.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.write(skill_file, arcname="SKILL.md")
        else:
            pending.append(f"Falta paquete: {archive.relative_to(ROOT)}")
    if pending:
        print("\n".join(f"- {item}" for item in pending))
        return 1
    print(f"PASS: {len(skills)} Skills empaquetadas individualmente para carga manual.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
