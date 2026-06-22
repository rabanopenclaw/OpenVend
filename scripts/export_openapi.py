from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SERVICES = {
    "authorization-adapter": ROOT / "services" / "authorization-adapter",
    "contacts": ROOT / "services" / "contacts",
}


def clear_app_modules() -> None:
    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            del sys.modules[module_name]


def load_app(service_path: Path):
    clear_app_modules()
    sys.path.insert(0, str(service_path))
    try:
        from app.main import app  # noqa: PLC0415

        return app
    finally:
        sys.path.remove(str(service_path))


def main() -> None:
    output_dir = ROOT / "openapi"
    output_dir.mkdir(parents=True, exist_ok=True)

    for service_name, service_path in SERVICES.items():
        app = load_app(service_path)
        output = output_dir / f"{service_name}.json"
        output.write_text(
            json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
