# Boundaries, data, and errors (sections 8-12)

## Contents

-   [8. Pydantic and data validation](#8-pydantic-and-data-validation)
-   [9. Dependency injection and composition](#9-dependency-injection-and-composition)
-   [10. Database sessions and transactions](#10-database-sessions-and-transactions)
-   [11. Synchronous versus asynchronous code](#11-synchronous-versus-asynchronous-code)
-   [12. Error handling](#12-error-handling)

## 8. Pydantic and data validation

Use Pydantic for parsing and validating untrusted data at boundaries,
especially HTTP requests and external service payloads.

-   Use separate request and response schemas where their contracts
    differ.
-   Use explicit types, constraints, defaults, and examples where
    useful.
-   Prefer strict validation for sensitive identifiers, amounts, and
    enumerated values where compatibility allows.
-   Reject unexpected fields for commands when silently accepting them
    could hide client errors; choose this policy intentionally for each
    contract.
-   Normalize input only when the normalization rule is well-defined.
-   Never treat successful schema validation as proof that a business
    action is permitted.
-   Do not expose internal fields such as password hashes, internal
    flags, or persistence metadata in response schemas.
-   Avoid returning arbitrary dictionaries when a stable response model
    is appropriate.
-   Keep schemas compatible with the project's installed Pydantic major
    version.

Example:

```python
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CreateUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr = Field(max_length=254)
    display_name: str = Field(min_length=1, max_length=120)


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str

    @classmethod
    def from_result(cls, result: CreateUserResult) -> "UserResponse":
        return cls(
            id=result.user_id,
            email=result.email,
            display_name=result.display_name,
        )
```

`EmailStr` requires the `email-validator` package (`pydantic[email]`).
It checks syntax only; it does not verify ownership or deliverability.
The domain `EmailAddress` value object still owns the business meaning
of an email (normalization, allowed domains, and so on).

Keep mapping methods such as `from_result` on the API schema, where the
API layer depends on the application layer—never the reverse.


## 9. Dependency injection and composition

Use dependency injection to provide infrastructure implementations to
use cases.

-   Construct shared resources at the application/composition boundary.
-   Keep constructors explicit about required dependencies.
-   Use FastAPI `Depends` for request-scoped dependency resolution,
    authentication dependencies, and API wiring.
-   Do not call `Depends()` from domain or application code.
-   Do not instantiate database engines, HTTP clients, or repositories
    inside a route.
-   Do not use module-level mutable global state for application
    resources.
-   Make resource lifetime clear: application-scoped clients/engines
    versus request-scoped sessions.
-   Ensure dependencies are replaceable in tests.
-   Prefer explicit wiring over a service locator or a global dependency
    container.

A typical composition path is:

```text
main.py
  -> create_app()
     -> load settings
     -> initialize resource lifecycle
     -> register routers and exception handlers
     -> wire use cases to infrastructure adapters
```

Example wiring:

```python
# app/api/dependencies.py
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session


def get_session(request: Request) -> Iterator[Session]:
    # The session factory is created once in lifespan (section 21).
    with request.app.state.session_factory() as session:
        yield session  # closing the session rolls back anything uncommitted


DbSession = Annotated[Session, Depends(get_session)]


# app/modules/users/api/dependencies.py
def get_create_user_use_case(session: DbSession) -> CreateUserUseCase:
    return CreateUserUseCase(
        users=SqlAlchemyUserRepository(session),
        uow=SqlAlchemyUnitOfWork(session),
    )
```

The repository and unit of work share the same request-scoped session,
so they share the same transaction. Tests replace either dependency
through `app.dependency_overrides` (section 16).


## 10. Database sessions and transactions

-   Create the database engine and connection pool at the appropriate
    application lifecycle boundary.
-   Provide a session per request or unit of work; do not share a
    mutable SQLAlchemy session across concurrent requests or tasks.
-   Close sessions reliably, including on exceptions.
-   Use explicit transaction boundaries.
-   Commit only when the unit of work succeeds; roll back on failure.
-   Do not hold a database transaction open while waiting on slow
    external network calls unless there is a specific, justified reason.
-   For workflows spanning databases and external services, consider an
    outbox pattern, idempotent processing, or a saga rather than
    assuming a distributed transaction.
-   Configure pool sizes and timeouts based on deployment concurrency
    and database capacity.
-   Test important constraints and transactional behavior against the
    actual database engine used in production.

Choose synchronous or asynchronous database access deliberately. Do not
assume `async def` makes synchronous database operations non-blocking.

When using SQLAlchemy `AsyncSession`:

-   Create the session factory with `expire_on_commit=False`; otherwise
    accessing attributes after commit triggers I/O that fails in async
    code.
-   Do not rely on implicit lazy loading. Load relationships explicitly
    (for example, `selectinload`) in the repository query.
-   Never share one `AsyncSession` across concurrently running tasks
    (for example, inside `asyncio.gather`).
-   Enable `pool_pre_ping` (or an equivalent recycle policy) so stale
    pooled connections are detected rather than failing a request.


## 11. Synchronous versus asynchronous code

Use `async def` when the endpoint or dependency needs to await
non-blocking I/O, such as an async database driver or async HTTP client.

-   Do not call blocking network clients or expensive blocking
    operations directly from an async endpoint.
-   Use synchronous `def` endpoints when the underlying work is
    synchronous and that is the clearer model; FastAPI can run
    synchronous path operations in a thread pool.
-   Do not mix sync and async database sessions casually.
-   Use an async-compatible driver and client stack when adopting async
    I/O end to end.
-   Move CPU-heavy or long-running tasks to an appropriate
    worker/process system.
-   Do not create untracked background tasks for work that must not be
    lost.
-   Apply concurrency limits and timeouts to outbound calls.
-   Remember that sync `def` endpoints *and* sync dependencies share a
    bounded thread pool (AnyIO's default is 40 threads). Slow blocking
    work can exhaust it and stall unrelated requests; size it
    deliberately or move the work elsewhere.
-   FastAPI `BackgroundTasks` run in the same process after the response
    is sent. Use them only for best-effort work that may be lost on a
    crash or restart; use a durable queue for anything else (section
    18).

Choose based on actual workload and library support, not fashion.

### In-process models and other heavy shared resources

-   Load the resource once in lifespan, keep it on `app.state`, and report
    readiness only after it loads. `/health/live` stays up while it loads.
-   When the library is not thread-safe, guard each call with a
    `threading.Lock` inside the adapter. Lock per call, not per request, so
    concurrent requests interleave instead of queueing whole batches.
-   Sync routes plus a lock serialize the work; that is the correct trade-off
    for one local model. Scale with replicas, not threads.
-   Keep the heavy dependency imported only in infrastructure, and give tests
    a deterministic `mock` backend so they never load weights.
-   Choose the backend with a setting (`local` or `hosted`) behind one
    adapter surface, so routes, use cases, and tests do not change.


## 12. Error handling

Use a consistent error taxonomy.

| Error category | Example | Typical handling |
|---|---|---|
| Request validation | Missing or malformed field | 422 (FastAPI default, unless the contract differs) |
| Authentication | Missing or invalid credentials | 401 |
| Authorization | Authenticated but not permitted | 403, or 404 when a deliberate resource-hiding policy applies |
| Missing resource | User or invoice not found | 404 |
| Business conflict | Duplicate operation or invalid state transition | 409 |
| Business rejection | Rule does not permit the action | Documented 4xx (commonly 409 or 422), chosen per contract |
| Dependency unavailable | Required database or upstream service unavailable | 503, or 502/504 for gateway failures |
| Unexpected defect | Programming error or unknown failure | 500 |

Rules:

-   Define domain/application exceptions without HTTP status codes.
-   Map known exceptions to HTTP responses at the API boundary.
-   Use stable, documented error response shapes.
-   Include a correlation/request ID where available.
-   Log unexpected exceptions with diagnostic context, but never expose
    stack traces, secrets, SQL credentials, or internal implementation
    details to clients.
-   Do not catch `Exception` just to return `{"success": false}` with
    status 200.
-   Do not use exceptions for ordinary branching when an explicit result
    type is clearer.
-   Avoid returning raw database or upstream error messages to clients.
-   Prefer a standard error shape such as RFC 9457 Problem Details
    (`application/problem+json`) over an ad-hoc format.
-   Give each domain error a stable, machine-readable `code` and a
    client-safe message. Clients branch on the code, never on message
    text.

Example boundary mapping:

```python
# app/api/errors.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

STATUS_BY_ERROR: dict[type[DomainError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
    BusinessRuleViolation: status.HTTP_422_UNPROCESSABLE_ENTITY,
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        code = next(
            (s for cls, s in STATUS_BY_ERROR.items() if isinstance(exc, cls)),
            status.HTTP_400_BAD_REQUEST,
        )
        return JSONResponse(
            status_code=code,
            media_type="application/problem+json",
            content={
                "type": f"https://errors.example.com/{exc.code}",
                "title": exc.title,
                "status": code,
                "detail": exc.public_message,
                "request_id": getattr(request.state, "request_id", None),
            },
        )
```

Register a separate handler for unexpected exceptions that logs the full
error with the request ID and returns a generic 500 body.
