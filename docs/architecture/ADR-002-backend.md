# ADR-002 — Backend

## Status

**ACCEPTED**

## Context

Need a backend that expresses the domain cleanly, supports deterministic rules, async jobs, and an AI gateway — maintainable by a small team.

## Options considered

| Option | Pros | Cons |
|--------|------|------|
| **Python + FastAPI** | Strong data/AI ecosystem; fast to ship; good typing (Pydantic); async | Need packaging discipline |
| Node/NestJS (TypeScript) | End-to-end TS; solid structure | Weaker scientific/AI libs; dual language if AI in Python anyway |
| JVM (Spring) | Enterprise maturity | Heavier for small team / AI glue |
| .NET | Strong typing/tooling | Team/ecosystem fit uncertain |

## Decision

**Python 3.12+ with FastAPI** as the API and worker runtime, shared domain library.

**Version strategy:** Pin `>=3.12,<3.14` (adjust as needed); lock dependencies with a lockfile when implementation starts; prefer LTS-ish FastAPI/Pydantic releases.

## Reason

- Domain + indicators + rules + agents naturally co-locate in Python.
- FastAPI fits OpenAPI-first DSS APIs later without forcing domain into HTTP models.
- Workers (ARQ/Celery-class) share code with API.

## Trade-offs

- Must enforce ports/adapters so SQLAlchemy/HTTP/LLM SDKs stay in `infrastructure`.
- CPU-heavy GIS later may need care (optional native libs).

## Migration / exit

- Domain models as pure Python; swapping FastAPI for another HTTP layer is localized.
- If TS-only team later: keep Python for rules/AI workers; not required now.

## References

- ADR-001, ADR-006, ADR-007
