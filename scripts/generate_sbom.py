#!/usr/bin/env python3
"""
BankingAIPlatform Software Bill of Materials (SBOM) Generator
Generates CycloneDX v1.5 JSON SBOM for backend and frontend components.
"""

import json
import uuid
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def generate_sbom():
    now_iso = datetime.now(timezone.utc).isoformat()
    serial_number = f"urn:uuid:{uuid.uuid4()}"

    sbom = {
        "$schema": "http://cyclonedx.org/schema/bom-1.5.json",
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": serial_number,
        "version": 1,
        "metadata": {
            "timestamp": now_iso,
            "tools": [
                {
                    "vendor": "BankingAIPlatform Engineering",
                    "name": "banking-ai-platform-sbom-generator",
                    "version": "1.0.0"
                }
            ],
            "component": {
                "bom-ref": "pkg:banking-ai-platform/platform@1.0.0",
                "type": "application",
                "name": "BankingAIPlatform Enterprise AI Platform",
                "version": "1.0.0",
                "description": "Enterprise AI Customer Support & Business Intelligence Platform",
                "licenses": [{"license": {"id": "Proprietary"}}]
            }
        },
        "components": []
    }

    # 1. Parse Backend Dependencies from requirements.txt
    req_path = ROOT / "backend" / "requirements.txt"
    if req_path.exists():
        for line in req_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"^([a-zA-Z0-9_\-\[\]]+)\s*([>=<~!]+.*)?$", line)
            if m:
                pkg_name = m.group(1).split("[")[0]
                version = (m.group(2) or "").lstrip(">=<~!") or "1.0.0"
                sbom["components"].append({
                    "bom-ref": f"pkg:pypi/{pkg_name}@{version}",
                    "type": "library",
                    "name": pkg_name,
                    "version": version,
                    "purl": f"pkg:pypi/{pkg_name}",
                    "scope": "required"
                })

    # 2. Parse Frontend Dependencies from package.json
    package_json_path = ROOT / "frontend" / "package.json"
    if package_json_path.exists():
        pkg_data = json.loads(package_json_path.read_text(encoding="utf-8"))
        for name, ver in pkg_data.get("dependencies", {}).items():
            clean_ver = ver.lstrip("^~>=<")
            sbom["components"].append({
                "bom-ref": f"pkg:npm/{name}@{clean_ver}",
                "type": "library",
                "name": name,
                "version": clean_ver,
                "purl": f"pkg:npm/{name}",
                "scope": "required"
            })

    output_dir = ROOT / "engineering" / "compliance"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "sbom.json"
    output_file.write_text(json.dumps(sbom, indent=2), encoding="utf-8")

    print(f"Generated SBOM at {output_file} with {len(sbom['components'])} components.")
    return output_file


if __name__ == "__main__":
    generate_sbom()
