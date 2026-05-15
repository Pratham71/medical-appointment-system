from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_frontend_api_uses_next_proxy_by_default() -> None:
    api_client = (ROOT / "app" / "frontend" / "lib" / "api.ts").read_text(
        encoding="utf-8"
    )
    next_config = (ROOT / "app" / "frontend" / "next.config.mjs").read_text(
        encoding="utf-8"
    )

    assert 'const BASE = "/api";' in api_client
    assert "BACKEND_API_URL" in next_config
    assert "NEXT_PUBLIC_API_URL" not in next_config


def test_login_page_has_accessible_show_password_toggle() -> None:
    login_page = (ROOT / "app" / "frontend" / "app" / "login" / "page.tsx").read_text(
        encoding="utf-8"
    )

    assert "showPassword" in login_page
    assert 'type={showPassword ? "text" : "password"}' in login_page
    assert 'aria-label={showPassword ? "Hide password" : "Show password"}' in login_page
    assert "setShowPassword" in login_page
