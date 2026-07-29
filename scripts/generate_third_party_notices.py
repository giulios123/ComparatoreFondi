from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import sysconfig


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = PROJECT_ROOT / "THIRD_PARTY_NOTICES.txt"

ALLOWED_LICENSES = {
    "3-Clause BSD License",
    "Apache License 2.0",
    "Apache Software License",
    "Apache Software License; BSD License",
    "Apache-2.0",
    "Apache-2.0 OR BSD-2-Clause",
    "BSD License",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0",
    "MIT",
    "MIT License",
    "MIT (identified from bundled license text)",
    "MIT-0",
    "MIT-CMU",
    "Mozilla Public License 2.0 (MPL 2.0)",
    "PSF-2.0",
}
PYINSTALLER_EXCEPTIONS = {"pyinstaller", "pyinstaller-hooks-contrib"}


def collect_packages() -> list[dict[str, str]]:
    command = [
        sys.executable,
        "-m",
        "piplicenses",
        "--format=json",
        "--with-license-file",
        "--with-notice-file",
        "--no-license-path",
        "--with-urls",
        "--from=mixed",
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    packages = json.loads(result.stdout)
    for package in packages:
        license_name = package.get("License", "").strip()
        license_text = package.get("LicenseText", "")
        if license_name.upper() == "UNKNOWN" and all(
            marker in license_text
            for marker in (
                "Permission is hereby granted, free of charge",
                'THE SOFTWARE IS PROVIDED "AS IS"',
            )
        ):
            package["License"] = "MIT (identified from bundled license text)"
    return sorted(packages, key=lambda row: row["Name"].lower())


def audit(packages: list[dict[str, str]]) -> None:
    failures = []
    for package in packages:
        name = package["Name"].lower()
        license_name = package.get("License", "").strip()
        if not license_name or license_name.upper() == "UNKNOWN":
            failures.append(f"{package['Name']}: licenza sconosciuta")
            continue
        if name in PYINSTALLER_EXCEPTIONS:
            continue
        if license_name not in ALLOWED_LICENSES:
            failures.append(f"{package['Name']}: {license_name}")
    if failures:
        details = "\n".join(f"- {failure}" for failure in failures)
        raise SystemExit(f"Licenze non approvate:\n{details}")


def python_license() -> str:
    candidates = [
        Path(sysconfig.get_path("stdlib")) / "LICENSE.txt",
        Path(sys.base_prefix) / "LICENSE.txt",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.read_text(encoding="utf-8")
    raise SystemExit("Licenza del runtime Python non trovata")


def render(packages: list[dict[str, str]]) -> str:
    parts = [
        "Comparatore Fondi - Third-Party Notices",
        "=" * 39,
        "",
        "This file is generated from the distributions installed for the desktop",
        "build. Source code for each component is available at the URL shown in",
        "its section. The project itself is licensed under Apache-2.0; see LICENSE.",
        "",
        "Python runtime",
        "--------------",
        f"Version: {sys.version.split()[0]}",
        "Source: https://www.python.org/downloads/source/",
        "",
        python_license().rstrip(),
    ]
    for package in packages:
        title = f"{package['Name']} {package['Version']}"
        parts.extend(
            [
                "",
                "=" * 79,
                title,
                "-" * len(title),
                f"License: {package['License']}",
                f"Source: {package.get('URL') or 'not declared'}",
                "",
                package["LicenseText"].rstrip(),
            ]
        )
        notice = package.get("NoticeText", "").strip()
        if notice:
            parts.extend(["", "Additional notice:", "", notice])
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check", action="store_true", help="audit only; do not write the notice"
    )
    args = parser.parse_args()

    packages = collect_packages()
    audit(packages)
    if not args.check:
        OUTPUT.write_text(render(packages), encoding="utf-8")
        print(f"Wrote {OUTPUT} ({len(packages)} packages)")
    else:
        print(f"License audit passed ({len(packages)} packages)")


if __name__ == "__main__":
    main()