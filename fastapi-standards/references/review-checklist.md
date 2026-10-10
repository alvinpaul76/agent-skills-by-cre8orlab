# Anti-patterns, definition of done, implementation order (sections 23-25)

## Contents

-   [23. Anti-patterns to avoid](#23-anti-patterns-to-avoid)
-   [24. Definition of done and non-negotiable rules](#24-definition-of-done-and-non-negotiable-rules)
-   [25. Practical implementation order](#25-practical-implementation-order)

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


## 24. Definition of done and non-negotiable rules

Use this section as the review gate for every new feature and meaningful
code change. A change is not done until the non-negotiable rules hold and
the checklist is complete.

### Non-negotiable rules

These are merge blockers. Each one is covered in detail in the section
noted.

1.  **No business decisions in API routes** (section 4).
2.  **No FastAPI, SQLAlchemy, or vendor SDK imports in the domain
    layer** (sections 1 and 5).
3.  **Use cases express application actions and orchestrate work**, and
    are reusable from HTTP, CLI, jobs, and message consumers (sections 6
    and 18).
4.  **Infrastructure implements technical details behind explicit
    boundaries** (section 7).
5.  **Business rules are testable without a web server or production
    database** (section 16).
6.  **Transactions, authorization, retries, and side effects are
    explicit** (sections 6, 10, and 14).
7.  **Prefer clear, boring, maintainable code over unnecessary
    abstraction** (section 23).

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
-   [ ] Documentation and configuration examples are updated, following the
    `fastapi-documentation` skill: the README's APIs table lists every API,
    each API has a page, new error codes are in troubleshooting, and its
    `check_docs.py` passes.


## 25. Practical implementation order

For a new feature, implement in this order:

1.  **Define the business rule.** Write down the invariants, decisions,
    and failure cases.
2.  **Create or update domain types and policies.** Keep them
    framework-independent.
3.  **Define the use case.** Specify inputs, outputs, dependencies, and
    workflow.
4.  **Define required ports.** Add repository or integration interfaces
    only where needed.
5.  **Implement infrastructure adapters.** Add database and
    external-service details.
6.  **Wire dependencies.** Connect implementations to use cases at the
    application boundary.
7.  **Expose the API.** Add request/response schemas, route, status
    codes, and error mapping.
8.  **Test at each layer.** Start with business rules, then integration,
    then HTTP behavior.
9.  **Review security and reliability.** Check authorization,
    transactions, retries, timeouts, and logging.
10. **Document the contract.** Update OpenAPI details, examples,
    configuration, and operational notes. Write the README and `docs/`
    pages with the `fastapi-documentation` skill.

The exact order can vary for exploratory work, but the final
architecture should preserve the boundaries.
