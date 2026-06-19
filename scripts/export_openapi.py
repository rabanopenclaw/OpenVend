from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SERVICE_PATH = ROOT / "services" / "authorization-adapter"
OUTPUT = ROOT / "openapi" / "authorization-adapter.json"

sys.path.insert(0, str(SERVICE_PATH))

from app.main import app  # noqa: E402


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
