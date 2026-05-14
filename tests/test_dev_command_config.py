import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_root_npm_dev_starts_backend_and_frontend() -> None:
    package_json = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))

    assert package_json["scripts"]["dev"] == "node scripts/dev.mjs"
    assert package_json["scripts"]["dev:backend"] == (
        "uv run uvicorn app.backend.app.main:app --reload --host 127.0.0.1 --port 8000"
    )
    assert package_json["scripts"]["dev:frontend"] == "npm --prefix app/frontend run dev"
    assert (ROOT / "scripts" / "dev.mjs").exists()

    dev_script = (ROOT / "scripts" / "dev.mjs").read_text(encoding="utf-8")
    assert "BACKEND_API_URL" in dev_script
    assert "NEXT_PUBLIC_API_URL" not in dev_script
    assert 'command: "npm"' in dev_script
    assert "npm.cmd" not in dev_script
    assert "shell: isWindows" in dev_script
