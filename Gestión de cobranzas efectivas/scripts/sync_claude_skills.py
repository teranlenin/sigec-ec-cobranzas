#!/usr/bin/env python3
"""Crea/verifica el espejo Claude Code desde las Skills canónicas del proyecto."""
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".agents" / "skills"
TARGET = ROOT / ".claude" / "skills"

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Crear archivos faltantes; nunca sobrescribe diferencias.")
    args = parser.parse_args()
    failed = []
    copied = []
    for src in sorted(SOURCE.glob("*/SKILL.md")):
        dst = TARGET / src.parent.name / "SKILL.md"
        if not dst.exists():
            if args.write:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(src.read_bytes())
                copied.append(dst.relative_to(ROOT))
            else:
                failed.append(f"Falta espejo: {dst.relative_to(ROOT)}")
        elif dst.read_bytes() != src.read_bytes():
            failed.append(f"Desfase; no sobrescrito: {dst.relative_to(ROOT)}")
    if copied:
        print(f"Espejos nuevos: {len(copied)}")
    if failed:
        print("\n".join(f"- {item}" for item in failed))
        return 1
    print("PASS: espejo Claude Code en paridad con las Skills canónicas.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
