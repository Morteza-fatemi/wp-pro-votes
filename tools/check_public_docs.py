"""Validate a public documentation-only project without exposing private material."""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
documents = {"README.md": 650, "ARCHITECTURE.md": 1100, "ROADMAP.md": 350}
failures = []
for name, minimum in documents.items():
    path = root / name
    if not path.is_file():
        failures.append(f"missing {name}")
        continue
    text = path.read_text(encoding="utf-8")
    if len(text) < minimum:
        failures.append(f"{name} is too short")
    for target in re.findall(r"\]\(([^)]+)\)", text):
        path_only = target.strip().split("#", 1)[0]
        if path_only and not path_only.startswith(("https://", "http://", "mailto:")):
            local = (root / path_only).resolve()
            if not local.is_relative_to(root.resolve()) or not local.is_file():
                failures.append(f"{name}: broken relative link {target}")
    if re.search(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----", text):
        failures.append(f"{name}: unexpected private key")
architecture = (root / "ARCHITECTURE.md")
if architecture.is_file() and "mermaid" not in architecture.read_text(encoding="utf-8"):
    failures.append("architecture must include a reference diagram")
if failures:
    print("\n".join("FAIL: " + issue for issue in failures), file=sys.stderr)
    sys.exit(1)
print("PASS: public project documents, links, diagram and basic secret hygiene")
