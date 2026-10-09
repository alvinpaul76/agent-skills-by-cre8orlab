# Operations, quality, and delivery (sections 13-22)

## Contents

-   [13. Configuration and secrets](#13-configuration-and-secrets)
-   [14. Authentication, authorization, and security](#14-authentication-authorization-and-security)
-   [15. Logging, observability, and health](#15-logging-observability-and-health)
-   [16. Testing strategy](#16-testing-strategy)
-   [17. API design and versioning](#17-api-design-and-versioning)
-   [18. Background jobs and messaging](#18-background-jobs-and-messaging)
-   [19. Performance and scalability](#19-performance-and-scalability)
-   [20. Code style and type safety](#20-code-style-and-type-safety)
-   [21. Application lifecycle and deployment](#21-application-lifecycle-and-deployment)
-   [22. Dependency and tooling baseline](#22-dependency-and-tooling-baseline)

## 13. Configuration and secrets

-   Use a typed settings class, such as Pydantic Settings.
-   Read configuration from environment variables or a managed secrets
    system.
-   Keep `.env` files out of version control; commit `.env.example` with
    placeholder values only.
-   Validate required settings at startup.
-   Separate development, testing, staging, and production
    configuration.
-   Never hardcode API keys, passwords, signing secrets, or database
    credentials.
-   Do not let business logic read settings directly; pass relevant
    configuration or policy values into the appropriate layer.
-   Document safe defaults and required production settings.
-   Avoid logging full settings objects because they may contain
    secrets.

Configuration should describe deployment behavior, not conceal business
rules in environment variables.


## 14. Authentication, authorization, and security

-   Require authentication on protected endpoints.
-   Enforce authorization on every relevant operation, not just in the
    frontend.
-   Check resource ownership and tenant boundaries in the
    application/use-case path.
-   Use established password hashing and token-validation libraries; do
    not invent cryptography.
-   Validate token issuer, audience, expiration, and relevant claims.
-   Apply least privilege to database users, service credentials, and
    deployment identities.
-   Restrict CORS to known origins in production; CORS is not
    authentication.
-   Set request size limits and sensible timeouts.
-   Rate-limit sensitive or abuse-prone endpoints at an appropriate
    layer.
-   Avoid leaking whether sensitive accounts or records exist when that
    distinction matters.
-   Keep dependencies patched and scan dependencies and container
    images.
-   Redact personal data and secrets from logs.
-   Do not trust forwarded headers unless they come from configured
    trusted proxies.
-   Use HTTPS in production and configure secure cookie attributes when
    cookies are used.
-   Disable or protect the interactive docs and schema (`/docs`,
    `/redoc`, `/openapi.json`) in production unless the API is
    intentionally public.
-   Validate file uploads by size, content type, and content—not by
    filename extension alone—and never use client-supplied filenames as
    storage paths.

Security decisions must be enforced server-side and covered by tests.


## 15. Logging, observability, and health

-   Use structured logs with consistent fields such as timestamp, level,
    service, environment, request ID, and operation.
-   Use module-level loggers; avoid `print()` for application logging.
-   Include useful context, but redact secrets and unnecessary personal
    data.
-   Propagate correlation IDs across service boundaries when
    appropriate.
-   Measure request latency, error rates, throughput, and dependency
    failures.
-   Use tracing when request flows cross services or queues.
-   Keep health endpoints separate from business endpoints.
-   Provide a liveness check for process health and a readiness check
    for whether the service can accept traffic.
-   Avoid exposing internal dependency details publicly through health
    endpoints.
-   Do not log every successful low-value event at warning/error level.

Observability should help diagnose failures without changing business
outcomes.


## 16. Testing strategy

Tests should follow the architecture.

### Unit tests

-   Test domain entities, value objects, policies, and use cases without
    FastAPI or a real database.
-   Use fakes or mocks for ports where appropriate.
-   Cover valid cases, invalid cases, boundaries, and important business
    invariants.
-   Prefer asserting observable behavior over private implementation
    details.

### Integration tests

-   Test repository implementations against a real test database of the
    same engine family as production where practical.
-   Test migrations, constraints, transaction behavior, and query
    correctness.
-   Test external adapters with controlled responses or a local test
    server.

### API tests

-   Use FastAPI's test client or async test tools consistent with the
    app's I/O model.
-   Test status codes, request validation, response schemas,
    authentication, authorization, and error mapping.
-   Override dependencies to isolate API behavior.
-   Ensure tests do not rely on production services or real credentials.

```python
@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_app(Settings(_env_file=".env.test"))
    app.dependency_overrides[get_create_user_use_case] = lambda: CreateUserUseCase(
        users=InMemoryUserRepository(),
        uow=FakeUnitOfWork(),
    )
    with TestClient(app) as client:  # the context manager runs lifespan
        yield client


def test_create_user_returns_201(client: TestClient) -> None:
    response = client.post(
        "/api/v1/users", json={"email": "a@example.com", "display_name": "A"}
    )
    assert response.status_code == 201
```

Building a fresh app per test (through `create_app`) avoids overrides
leaking between tests.

### Test naming and structure

Name tests after behavior:

```text
test_create_user_rejects_duplicate_email
test_approval_fails_when_limit_is_exceeded
test_get_user_returns_404_when_user_does_not_exist
```

Do not test only the happy path. Business rules should have direct unit
tests independent of route tests.


## 17. API design and versioning

-   Use resource-oriented URLs and consistent HTTP methods.
-   Use appropriate status codes and stable response shapes.
-   Define pagination, sorting, and filtering conventions consistently,
    with a server-enforced maximum page size (for example,
    `limit: Annotated[int, Query(ge=1, le=100)] = 50`).
-   Use explicit request and response models.
-   Avoid leaking ORM models or internal domain objects into OpenAPI
    schemas.
-   Version public APIs deliberately, for example `/api/v1`.
-   Maintain backward compatibility for existing consumers or document
    breaking changes.
-   Use idempotency for operations where clients may retry requests and
    duplicate effects would be harmful.
-   Define date/time formats, timezone expectations, decimal precision,
    and enum behavior explicitly.
-   Do not use a successful HTTP response to conceal a business failure.


## 18. Background jobs and messaging

Background tasks, scheduled jobs, and message consumers should call the
same application use cases as HTTP routes.

```text
HTTP route ---------+
Scheduled job ------+--> Application use case --> Domain rules
Message consumer ---+
CLI command --------+
```

-   Do not duplicate business rules in workers or event handlers.
-   Validate message payloads at the boundary.
-   Assume messages may be delivered more than once.
-   Make handlers idempotent where possible.
-   Define retry, backoff, dead-letter, and failure-monitoring policies.
-   Distinguish event publication from transaction commit.
-   Use an outbox or another reliable delivery pattern when losing an
    event after a database commit would be unacceptable.
-   Do not rely on an in-process background task for durable work.


## 19. Performance and scalability

-   Measure before optimizing.
-   Avoid N+1 database access and unbounded result sets.
-   Paginate list endpoints.
-   Add indexes based on query patterns and measured plans.
-   Set timeouts for database and outbound network operations.
-   Reuse long-lived connection pools and HTTP clients where
    appropriate.
-   Avoid expensive CPU-bound work on the event loop.
-   Use caching only with explicit invalidation and correctness rules.
-   Apply limits to concurrency, payload sizes, file uploads, and batch
    processing.
-   Do not add caching or distributed infrastructure before the need is
    established.
-   Use load tests for critical paths and expected concurrency.


## 20. Code style and type safety

-   Use a supported Python version and pin compatible dependency ranges.
-   Add type annotations to public functions, use cases, interfaces, and
    return values.
-   Use a formatter and linter consistently (for example, Ruff).
-   Run static type checking where it provides value (for example, mypy
    or Pyright).
-   Keep functions focused and avoid excessive nesting.
-   Prefer explicit names over abbreviations.
-   Avoid mutable default arguments.
-   Avoid `Any` unless justified and isolated at a boundary.
-   Avoid circular imports; fix architectural boundaries instead of
    hiding cycles.
-   Keep comments focused on why a non-obvious decision exists, not on
    restating the code.
-   Use docstrings for public APIs and complex business behavior.
-   Keep dependencies minimal and remove unused packages.


## 21. Application lifecycle and deployment

-   Use an application factory (`create_app`) when it improves
    testability and configuration.
-   Initialize and close shared resources using FastAPI lifespan
    handling.
-   Do not open database connections or start workers as import-time
    side effects.
-   Run database migrations as a controlled deployment step.
-   Configure trusted hosts, proxy headers, TLS termination, and allowed
    origins appropriately for the deployment.
-   Run the application as a non-root user in containers.
-   Use graceful shutdown and sensible worker/time limits.
-   Store logs on standard output/error for containerized deployments.
-   Separate web process scaling from background worker scaling.
-   Document how to run locally, test, migrate, and deploy.
-   Test the exact startup command used in production.
-   Behind a reverse proxy, enable proxy headers only for the proxy's
    address (for example, Uvicorn's `--proxy-headers
    --forwarded-allow-ips=<proxy-ip>`), never `*` on a publicly
    reachable port.

Example factory and lifespan:

```python
# app/main.py
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    app.state.session_factory = sessionmaker(engine, expire_on_commit=False)
    app.state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(10.0, connect=5.0)
    )
    try:
        yield
    finally:
        await app.state.http_client.aclose()
        engine.dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(
        lifespan=lifespan,
        docs_url="/docs" if settings.expose_docs else None,
        redoc_url=None,
    )
    app.state.settings = settings
    register_exception_handlers(app)
    app.include_router(api_router, prefix="/api")
    return app


app = create_app()
```

Shared resources live on `app.state` and are created inside lifespan,
not at import time, so tests can build an app with different settings.


## 22. Dependency and tooling baseline

Select versions compatible with the supported Python runtime and pin
them through a lockfile or reproducible dependency workflow.

A typical stack may include:

-   **FastAPI** — HTTP framework
-   **Pydantic / Pydantic Settings** — validation and configuration
-   **SQLAlchemy** — ORM and database toolkit, if a relational
    database is used
-   **Alembic** — schema migrations
-   **PostgreSQL** — relational database, when appropriate
-   **HTTPX** — HTTP client and testing support
-   **Pytest** — testing
-   **Ruff** — linting and formatting
-   **mypy or Pyright** — optional static type checking
-   **asgi-lifespan** — useful for testing lifespan-dependent
    applications
-   **OpenTelemetry** — optional tracing and metrics instrumentation

Do not install every tool by default. Choose based on the application,
runtime, and operational requirements.
