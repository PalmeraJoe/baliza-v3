from pathlib import Path

FORBIDDEN = (
    "fastapi",
    "sqlalchemy",
    "psycopg",
    "alembic",
    "redis",
    "boto",
    "openai",
    "anthropic",
    "authlib",
)


def test_domain_has_no_infrastructure_imports() -> None:
    root = Path(__file__).resolve().parents[1] / "src" / "baliza" / "domain"
    offenders: list[str] = []
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        for token in FORBIDDEN:
            if f"import {token}" in text or f"from {token}" in text:
                offenders.append(f"{path.name}: {token}")
    assert offenders == []
