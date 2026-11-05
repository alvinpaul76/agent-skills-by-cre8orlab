# Anti-patterns and definition of done (sections 23-24)

## Contents

-   [23. Anti-patterns to avoid](#23-anti-patterns-to-avoid)
-   [24. Definition of done](#24-definition-of-done)

## 23. Anti-patterns to avoid

Avoid these patterns unless there is a clearly documented reason:

-   Business rules inside FastAPI route functions.
-   SQL queries and transaction management inside routes.
-   Domain code importing FastAPI or SQLAlchemy.
-   ORM entities used as public request/response schemas.
-   One oversized service class containing unrelated use cases.
-   Repositories that make business decisions.
-   Global mutable sessions, clients, or application state.
-   Generic `utils.py` modules full of unrelated logic.
-   Catch-all exception handling that hides failures.
-   Unbounded list queries or background task creation.
-   Blocking I/O inside async functions.
-   Business rules duplicated between API, jobs, and consumers.
-   Configuration values used to conceal core business policy.
-   Tests that require production credentials or live third-party
    services.
-   Premature microservices, event buses, factories, or abstraction
    layers with no clear benefit.
-   Returning HTTP 200 with an error flag in the body.


## 24. Definition of done

A change is done when the non-negotiable rules in `SKILL.md` hold and this
checklist is complete.

> **Architecture test:** If replacing FastAPI, PostgreSQL, or an
> external vendor would require rewriting the core business rules, the
> boundaries are too tightly coupled.

### Checklist

#### Architecture

-   [ ] Routes are thin and contain no business decisions.
-   [ ] Business rules live in the domain layer or a clearly defined
    domain policy.
-   [ ] Use cases orchestrate the workflow.
-   [ ] Domain and application code do not import infrastructure
    implementations.
-   [ ] Repositories handle persistence, not business policy.
-   [ ] HTTP, database, and external-service concerns remain at their
    boundaries.

#### Validation and errors

-   [ ] Request and external inputs are validated.
-   [ ] Business invariants are enforced independently of request
    validation.
-   [ ] Known errors map to documented API responses.
-   [ ] Unexpected failures are logged safely and not exposed to
    clients.

#### Data and reliability

-   [ ] Transaction boundaries are explicit.
-   [ ] Sessions and clients have correct lifetimes.
-   [ ] Retries and duplicate processing are safe where applicable.
-   [ ] Migrations and database constraints are included where required.

#### Security and operations

-   [ ] Authentication and authorization are enforced where required.
-   [ ] Required keys fail closed at startup; safety switches default to secure.
-   [ ] Secrets and personal data are not leaked through logs or
    responses.
-   [ ] Timeouts and resource limits are configured.
-   [ ] Health and observability requirements are met.

#### Testing and quality

-   [ ] Domain policies and use cases have unit tests.
-   [ ] Repository behavior has integration tests where needed.
-   [ ] API behavior, validation, and authorization are tested.
-   [ ] Formatting, linting, type checks, and tests pass.
-   [ ] Docs and configuration examples are updated with the
    `fastapi-documentation` skill, and its `check_docs.py` passes.
