from __future__ import annotations

import json
import subprocess
import sys

DENIED_FRAGMENTS = (
    "AGPL",
    "CDDL",
    "SSPL",
    "BUSL",
    "Commons Clause",
    "EPL",
    "GPL",
    "LGPL",
    "MPL",
    "PolyForm",
    "RSAL",
)

APPROVED_EXCEPTIONS = {
    "certifi": "MPL-2.0 CA certificate bundle used by development/audit tooling",
}


def main() -> int:
    result = subprocess.run(
        [sys.executable, "-m", "piplicenses", "--format=json", "--with-system"],
        check=True,
        capture_output=True,
        text=True,
    )
    packages = json.loads(result.stdout)
    violations: list[str] = []

    for package in packages:
        name = str(package.get("Name", "UNKNOWN"))
        if name.startswith("openvend-"):
            continue
        license_name = str(package.get("License", "UNKNOWN"))
        if any(fragment.lower() in license_name.lower() for fragment in DENIED_FRAGMENTS):
            if name in APPROVED_EXCEPTIONS:
                continue
            violations.append(f"{name}: {license_name}")

    if violations:
        print("Python dependency license policy violations:", file=sys.stderr)
        for violation in violations:
            print(f"- {violation}", file=sys.stderr)
        return 1

    print(f"Python dependency license check passed for {len(packages)} packages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
