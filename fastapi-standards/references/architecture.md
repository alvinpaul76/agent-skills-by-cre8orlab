# Architecture and layers (sections 1-7)

## Contents

-   [1. Architectural principles](#1-architectural-principles)
-   [2. Recommended project structure](#2-recommended-project-structure)
-   [3. Responsibilities by layer](#3-responsibilities-by-layer)
-   [4. Keep routes thin](#4-keep-routes-thin)
-   [5. Domain layer: business truth](#5-domain-layer-business-truth)
-   [6. Application layer: use cases](#6-application-layer-use-cases)
-   [7. Repository and infrastructure rules](#7-repository-and-infrastructure-rules)

## 1. Architectural principles

Every application should follow these principles:

1.  **Separation of concerns:** Each module has one clear
    responsibility.
2.  **Business logic independence:** Business rules must not depend on
    FastAPI, HTTP, SQLAlchemy, Pydantic transport schemas, or vendor
    SDKs.
3.  **Dependency inversion:** High-level business policies depend on
    abstractions, not concrete infrastructure implementations.
4.  **Explicit boundaries:** Validate data at system boundaries and
    convert it into types appropriate for the next layer.
5.  **Thin API layer:** Routes handle HTTP concerns and delegate work to
    application use cases.
6.  **Single source of truth:** Each business rule should have one
    authoritative implementation.
7.  **Testability by design:** Business rules can be tested without a
    web server, database, network, or external service.
8.  **Prefer simple solutions:** Add abstractions when they protect a
    boundary or simplify change—not merely to follow a pattern.
9.  **Fail explicitly:** Do not silently swallow errors or return fake
    success responses.
10. **Secure by default:** Authentication, authorization, validation,
    secrets management, and safe logging are part of the design.

### Dependency direction

Dependencies point inward:

```text
HTTP / FastAPI
     |
     v
Application use cases
     |
     v
Domain model and business rules

Infrastructure adapters ---> implement interfaces required by the inner layers
```

A more concrete view:

```text
API routes
   |-- request/response schemas
   |-- authentication and HTTP mapping
   v
Application use cases
   |-- orchestration
   |-- transaction boundary coordination
   |-- interfaces/ports
   v
Domain
   |-- entities and value objects
   |-- business policies
   |-- invariants and domain errors

Infrastructure
   |-- SQLAlchemy repositories
   |-- database session and transactions
   |-- external APIs
   |-- queues, email, file storage
   |
   +---- implements interfaces consumed by Application/Domain
```

**Rule:** The domain must never import FastAPI, SQLAlchemy, a database
driver, an HTTP client, or a vendor SDK. The application layer should
not depend on infrastructure implementations.


## 2. Recommended project structure

Use a feature-oriented structure with clear architectural layers. This
example uses a `users` feature; adapt the feature names to the product.

```text
app/
├── main.py                     # App factory / ASGI entry point
├── config.py                   # Environment-backed settings
├── lifespan.py                 # Startup and shutdown resources
├── api/
│   ├── router.py               # Root API router
│   ├── dependencies.py         # HTTP/API dependency wiring
│   ├── errors.py               # HTTP exception mapping
│   └── v1/
│       └── router.py           # Versioned API routes
├── modules/
│   └── users/
│       ├── domain/
│       │   ├── entities.py     # Business entities
│       │   ├── value_objects.py
│       │   ├── policies.py     # Business decisions and rules
│       │   ├── errors.py       # Domain-specific errors
│       │   └── repositories.py # Repository ports (Protocols)
│       ├── application/
│       │   ├── dto.py          # Use-case input/output models
│       │   ├── ports.py        # Non-repository ports: unit of work, email, payments, clock
│       │   ├── use_cases/
│       │   │   ├── create_user.py
│       │   │   └── get_user.py
│       │   └── services.py     # Application orchestration, if needed
│       ├── infrastructure/
│       │   ├── db_models.py    # SQLAlchemy mappings
│       │   ├── repositories.py # Repository implementations
│       │   └── mappers.py      # ORM/domain mapping
│       └── api/
│           ├── routes.py       # FastAPI endpoints
│           ├── schemas.py      # HTTP request/response schemas
│           └── dependencies.py # Feature-specific wiring, if needed
├── infrastructure/
│   ├── database/
│   │   ├── session.py
│   │   └── transaction.py
│   ├── clients/                # External service clients
│   ├── logging.py
│   └── telemetry.py
└── shared/
    ├── types.py                # Truly shared, domain-neutral types
    └── errors.py               # Cross-cutting technical errors

tests/
├── unit/
│   └── modules/
│       └── users/
│           ├── test_policies.py
│           └── test_create_user.py
├── integration/
│   └── modules/
│       └── users/
├── api/
│   └── test_users_routes.py
└── conftest.py

migrations/                      # Alembic migrations
pyproject.toml
.env.example
README.md
```

### Structure guidelines

-   Group code by **business capability or feature**, not only by
    technical type.
-   Keep a feature's domain, application, infrastructure, and API code
    together.
-   Keep shared modules small. Do not turn `shared/` into a
    miscellaneous dumping ground.
-   A small service does not need every directory on day one. Add layers
    when the complexity justifies them, but preserve the dependency
    rules.
-   Avoid generic names such as `helpers.py`, `utils.py`, `common.py`,
    or `manager.py` when a precise name is possible.
-   Do not create a repository, service, factory, or abstraction for
    every class automatically.
-   Keep API versioning at the HTTP boundary; do not duplicate domain
    rules for each API version.
-   **Where ports live:** repository ports go in `domain/repositories.py`
    because they speak in domain types. Ports for other side effects
    (unit of work, email, payment gateway, clock) go in
    `application/ports.py`. Implementations of both live in
    `infrastructure/`.


## 3. Responsibilities by layer

| Layer | Owns | Must not own |
|---|---|---|
| API / presentation | HTTP routes, status codes, request parsing, response schemas, auth integration, error-to-HTTP mapping | Business decisions, SQL queries, transaction logic |
| Application | Use cases, workflow orchestration, authorization checks, transaction coordination, non-repository ports | HTTP request/response objects, ORM-specific behavior |
| Domain | Entities, value objects, invariants, business policies, domain errors, repository ports | FastAPI, SQLAlchemy, network calls, environment variables |
| Infrastructure | Database access, ORM mappings, port implementations, external clients, file storage, queue adapters | Independent business policy decisions |
| Composition root | Building the app and wiring implementations to ports | Business rules |

### The business decision rule

Ask: **"Would this decision still be required if the application were
called from a CLI, scheduled job, message consumer, or another API?"**

-   If yes, it is likely a domain rule or application use case.
-   If it decides *what is allowed, required, eligible, or valid in the
    business*, it belongs in the domain.
-   If it coordinates steps to achieve a business goal, it belongs in
    the application layer.
-   If it translates HTTP, SQL, SDK, or queue behavior, it belongs at
    the corresponding boundary.

For example, a discount eligibility rule belongs in a domain policy.
Applying that policy while creating an order is part of an application
use case. Reading an order from PostgreSQL belongs in an infrastructure
repository. Returning HTTP 201 belongs in the API layer.


## 4. Keep routes thin

A route should:

1.  Accept and validate HTTP input.
2.  Obtain dependencies through FastAPI dependency injection.
3.  Call one application use case.
4.  Translate the result into an HTTP response.
5.  Map known application/domain errors to suitable HTTP errors.

A route should **not**:

-   Make business decisions.
-   Execute raw SQL or use an ORM session directly.
-   Call several external services to implement a business workflow.
-   Calculate prices, eligibility, fees, approval decisions, or status
    transitions.
-   Contain complex `if/else` business branches.
-   Catch every exception and return a generic success or 400 response.

Illustrative pattern:

```python
from typing import Annotated

from fastapi import APIRouter, Depends, status

router = APIRouter(prefix="/users", tags=["users"])

CreateUser = Annotated[CreateUserUseCase, Depends(get_create_user_use_case)]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(request: CreateUserRequest, use_case: CreateUser) -> UserResponse:
    result = use_case.execute(
        CreateUserInput(email=request.email, display_name=request.display_name)
    )
    return UserResponse.from_result(result)
```

Notes on this pattern:

-   Use `Annotated[..., Depends(...)]` rather than `= Depends(...)`
    defaults. Define reusable aliases (such as `CreateUser` or
    `DbSession`) so routes stay short and dependencies stay consistent.
-   The return annotation is the response model. Do not also pass
    `response_model=` unless the two must differ.
-   There is no `try/except`. Domain errors propagate to the exception
    handlers registered at the API boundary (section 12).
-   `get_create_user_use_case` is defined in section 9.

The route delegates the work; it does not implement the business
policy.


## 5. Domain layer: business truth

The domain layer represents the business concepts and rules
independently of delivery and storage technology.

### Domain entities and value objects

-   Use entities when identity and lifecycle matter.
-   Use value objects for concepts defined by their values, such as
    `Money`, `EmailAddress`, or `DateRange`.
-   Keep invariants close to the domain objects or in explicit domain
    policies.
-   Make invalid states difficult to represent.
-   Use `Decimal` or a well-defined money type for financial
    calculations; do not use binary floating-point for currency.
-   Make time zones and currency precision explicit where relevant.

### Business policies

Name business decisions directly:

```python
from decimal import Decimal


class CreditPolicy:
    def can_approve(self, requested_amount: Decimal, available_limit: Decimal) -> bool:
        if requested_amount <= 0:
            return False
        return requested_amount <= available_limit
```

This example is illustrative only. Real rules should be explicit about
edge cases and should raise domain errors instead of returning `False`
where the distinction between rejection and invalid input matters.

Prefer named policies or domain methods over large conditional blocks
scattered across routes and services.

### Domain rules

-   Do not read environment variables in domain code.
-   Do not query a database from a domain entity.
-   Do not make HTTP calls from a domain policy.
-   Do not raise `HTTPException` from the domain.
-   Do not put SQLAlchemy declarative models in the domain.
-   Do not make domain decisions in Pydantic request validators alone.
    Boundary validation and business validation serve different
    purposes.


## 6. Application layer: use cases

A use case expresses one application action, such as `CreateInvoice`,
`ApprovePayment`, or `RegisterCustomer`.

A use case typically:

1.  Receives explicit input.
2.  Loads required state through ports/repositories.
3.  Invokes domain behavior and policies.
4.  Coordinates changes and external side effects.
5.  Persists changes.
6.  Returns an explicit result.

Guidelines:

-   Use one class or function per meaningful use case.
-   Give use cases business-oriented names.
-   Pass required dependencies explicitly through constructor injection
    or function arguments.
-   Keep HTTP concepts out of use cases.
-   Do not return ORM models directly.
-   Do not hide business workflows inside repository methods.
-   Avoid a single giant `UserService` or `ApplicationService` that owns
    unrelated actions.
-   Use a transaction boundary for operations that must commit or roll
    back together.
-   Make external side effects and retry behavior explicit.

A use case may coordinate repositories and clients, but the policy that
determines the correct business outcome should remain in the domain.

### Application DTOs

Use explicit input/output types at the use-case boundary when they
improve clarity or decouple the application from the API.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class CreateUserInput:
    email: str
    display_name: str

@dataclass(frozen=True)
class CreateUserResult:
    user_id: str
    email: str
    display_name: str
```

Do not reuse an HTTP request schema as the domain entity or application
model by default. Reuse a type only when the layers genuinely share the
same contract and doing so does not create unwanted coupling.

### Example use case

```python
# modules/users/application/use_cases/create_user.py
class CreateUserUseCase:
    def __init__(self, users: UserRepository, uow: UnitOfWork) -> None:
        self._users = users
        self._uow = uow

    def execute(self, data: CreateUserInput) -> CreateUserResult:
        email = EmailAddress(data.email)          # value object enforces format
        if self._users.get_by_email(email) is not None:
            raise EmailAlreadyRegistered(email)   # domain error, no HTTP status

        user = User.register(email=email, display_name=data.display_name)
        self._users.add(user)
        self._uow.commit()                        # explicit transaction boundary

        return CreateUserResult(
            user_id=str(user.id),
            email=str(user.email),
            display_name=user.display_name,
        )
```

The `get_by_email` check gives a clear error in the common case, but it
is not race-free. A unique constraint on `email` is the real guarantee;
the repository translates the resulting `IntegrityError` into
`EmailAlreadyRegistered` so both paths produce the same domain error.


## 7. Repository and infrastructure rules

Repositories isolate persistence mechanics from application and domain
logic.

-   Define repository ports in the domain layer and other ports in the
    application layer (see section 2), as `typing.Protocol` classes.
-   Implement those interfaces in infrastructure.
-   Use SQLAlchemy models only in infrastructure.
-   Convert between ORM records and domain objects explicitly when the
    domain model is separate.
-   Keep repositories focused on loading, storing, and querying
    data—not deciding business outcomes.
-   Use explicit methods such as `get_by_id`, `add`, and `save` instead
    of a universal generic repository that hides useful query semantics.
-   Keep transaction ownership clear. Do not commit independently in
    every repository method if a use case requires multiple changes to
    be atomic.
-   Avoid N+1 queries and load only the data required for the use case.
-   Use database constraints for data integrity in addition to
    application checks.
-   Use migrations (for example, Alembic) for schema changes; do not
    rely on production startup to silently mutate schemas.
-   Do not leak database sessions or ORM objects into API responses.
-   Translate driver and ORM exceptions that carry business meaning (for
    example, a unique-constraint violation) into domain errors.

Example ports:

```python
# modules/users/domain/repositories.py
from typing import Protocol


class UserRepository(Protocol):
    def get_by_id(self, user_id: UserId) -> User | None: ...
    def get_by_email(self, email: EmailAddress) -> User | None: ...
    def add(self, user: User) -> None: ...


# modules/users/application/ports.py
class UnitOfWork(Protocol):
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
```

`Protocol` keeps the inner layers free of infrastructure imports and
lets tests pass simple in-memory fakes without inheritance.

### External integrations

Wrap external APIs, email, object storage, and message queues behind
adapters/clients.

-   Set connection and read timeouts.
-   Define retry policies only for operations that are safe to retry.
-   Use idempotency keys where duplicate processing could cause harm.
-   Validate and normalize external responses.
-   Translate vendor-specific exceptions into application-level
    integration errors.
-   Never treat an external service response as trusted input.
-   Do not place provider-specific response objects in the domain model.
