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
-   Keep `.env` out of version control; commit `.env.example` (rules in
    the `docker-compose-standards` skill).
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

### Settings patterns

-   Wrap secrets in `SecretStr` so they do not appear in `repr()` or logs;
    call `get_secret_value()` only where the secret is used.
-   Name inbound and outbound credentials differently. A key clients send to
    this service (`CLIENT_API_KEYS`) and a key this service sends to a
    vendor (`VENDOR_API_KEY`) are unrelated; one shared name causes
    misconfiguration. Say which is which in `.env.example` and the README.
-   Parse a list from one environment variable with
    `Annotated[list[SecretStr], NoDecode]` and a `field_validator(mode="before")`
    that splits on commas, strips whitespace, and drops empties. `NoDecode`
    stops pydantic-settings from expecting JSON.
-   Validate secret strength in the settings class (for example, at least 32
    characters), so a weak value fails at startup.
-   Make required-in-production settings fail closed. Check in `create_app`
    (not in `Settings.__init__`, so unit tests can still construct
    `Settings`), and raise `RuntimeError` naming the variable.
-   Give every safety switch (such as `AUTH_ENABLED`) a secure default, log a
    WARNING at startup when it is off, and say in the README that it is for
    local development only.
-   Keep one definition of each variable: `config.py`, `.env.example`, the
    compose file, and the README list the same names and defaults, and a test
    fails when `config.py` and `.env.example` drift apart.
-   Under Docker secrets, accept a `<NAME>_FILE` path (for example
    `DATABASE_PASSWORD_FILE`) and read the value from the file when it is set;
    build connection strings from parts in the settings class and never log
    them.
-   Provide a `make_settings(**overrides)` test helper that sets
    `_env_file=None`, so a developer's real `.env` never leaks into tests.


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
-   Keep dependencies patched and scan them; image scanning is in the
    `fastapi-docker` skill.
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

### Static API-key authentication

Use this for service-to-service or internal APIs where callers are known and
a full token system is more than the risk calls for.

-   Read the key from one header (`X-API-Key`) through
    `APIKeyHeader(name="X-API-Key", auto_error=False)`. This also adds the
    Authorize button to the interactive docs.
-   Protect a whole version with one router-level dependency
    (`APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])`), so
    new routes are protected without per-route code. Mount health endpoints
    outside that router so probes work without a key.
-   Accept a list of keys so a key can be rotated: add the new key, move
    callers over, then remove the old one.
-   Compare with `secrets.compare_digest` against every configured key without
    an early exit, so timing does not reveal which key came close.
-   Return the same 401 for a missing and a wrong key, with a
    `WWW-Authenticate` header and a stable error `code`. Authentication is a
    transport concern: raise an API-layer `Unauthorized`, not a `DomainError`.
-   Log rejections with the request id and client address, and never log the
    presented key.
-   Check the key before body validation, so unauthenticated callers learn
    nothing about the request schema.
-   Fail closed at startup when auth is enabled and no keys are configured.
-   Test: missing key, wrong key (identical response), valid key, each key in
    a rotation list, auth before validation, open health endpoints, startup
    failure with no keys, and the auth-disabled path.

#### Settings for the pattern

| Variable | Default | Behavior |
|---|---|---|
| `<PREFIX>_CLIENT_API_KEYS` | empty | Comma-separated keys that callers send in `X-API-Key`. Each key is at least 32 characters. Required while auth is enabled. |
| `<PREFIX>_AUTH_ENABLED` | `true` | `false` turns the key check off so `/api/v1/*` accepts any request. Local development only. |

-   `AUTH_ENABLED=true`: `create_app` raises `RuntimeError` naming
    `CLIENT_API_KEYS` when the list is empty.
-   `AUTH_ENABLED=false`: keys become optional, `require_api_key` returns
    immediately, and `create_app` logs a WARNING that the API is open. Body
    validation and every other check still run.
-   Put the toggle check inside `require_api_key` (and the startup check),
    so the routes and the router stay identical in both modes.
-   Pass both through the compose file with `:-` defaults
    (`${<PREFIX>_AUTH_ENABLED:-true}`, `${<PREFIX>_CLIENT_API_KEYS:-}`) and let
    the app's startup check enforce the keys (see `docker-compose-standards`).
-   Document both in `.env.example` with a command to generate a key
    (`python -c "import secrets; print(secrets.token_urlsafe(32))"`).
-   With auth off the interactive docs still show the Authorize button
    (the security scheme stays in the OpenAPI schema), so say that the key is
    ignored.

Out of scope for this pattern: rate limiting, per-key quotas, and hashed key
storage. Add them when keys move into a database or callers become untrusted.


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
-   Test hosted-API adapters with `httpx.MockTransport` (inject the
    `httpx.Client`): assert the wire format (path, auth header, body) and
    that 401, 429, and 500 become the application error.
-   Verify a hosted integration once by hand with a real key, and say in the
    PR that automated tests never call it.

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
    app = create_app(make_settings())  # section 13: never reads a real .env
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

### Batch endpoints

-   Cap the batch size in the request schema (`Field(min_length=1, max_length=N)`)
    and in the domain, and cap each text field.
-   Require a client-supplied `id` per item, reject duplicates, and return
    results in input order keyed by that id.
-   Validate the whole batch before doing any work. Choose all-or-nothing
    (one 422 or 503 for the request) unless callers need per-item outcomes;
    when they do, return a per-item status and keep the HTTP status 200.
-   Estimate worst-case latency (items x per-item time) against the client
    and proxy timeouts. When it will not fit, move the work to an async job
    with a job id (section 18).
-   Reject output-only fields (scores, status, computed totals) in the
    request with `extra="forbid"`, so callers cannot supply values the
    service is meant to compute.
-   Give the port a `process_many`-style method so an adapter can later
    parallelize without changing the use case.
-   Replacing a response shape is a breaking change: add a new version, or
    state in the PR that no consumer depends on the old shape.


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

N+1 queries, pagination, timeouts and CPU work on the event loop are
covered in sections 7, 11 and 17. Beyond those:

-   Measure before optimizing; load-test critical paths at expected
    concurrency.
-   Add indexes from query patterns and measured plans.
-   Reuse long-lived connection pools and HTTP clients.
-   Add caching only when measured, with explicit invalidation rules.


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
-   Do not create `app = create_app()` at module level when startup
    validates configuration (for example, fail-closed keys): importing the
    module would crash. Run uvicorn with `--factory` and a `main()` script
    entry (`uvicorn.run("pkg.main:create_app", factory=True, ...)`).
-   When docs are exposed, redirect `/` to `/docs` (excluded from the
    schema and open without auth); when they are not, leave `/` as a 404.
-   Log to standard output; scale web processes and background workers
    separately.
-   Test the exact startup command used in production.
-   Containers, migrations as a deploy step, proxy headers, non-root users
    and graceful shutdown are in the `fastapi-docker` skill.

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
        openapi_url="/openapi.json" if settings.expose_docs else None,  # the schema leaks too
    )
    app.state.settings = settings
    register_exception_handlers(app)
    app.include_router(api_router, prefix="/api")
    return app
```

There is no module-level `app = create_app()`: startup validation would run
on import. Start it with `uvicorn app.main:create_app --factory`. Shared
resources live on `app.state` and are created inside lifespan, so tests can
build an app with different settings.


## 22. Dependency and tooling baseline

Pin versions through a lock file (`uv.lock`). A typical stack: FastAPI,
Pydantic and pydantic-settings, SQLAlchemy and Alembic (with a relational
database), HTTPX, pytest, Ruff, and optionally mypy or Pyright and
OpenTelemetry. Add a tool when the project needs it, not by default.
