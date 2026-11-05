---
name: fastapi-standards
description: Engineering standards for building, reviewing and refactoring FastAPI services with a layered architecture (routes, use cases, domain, infrastructure). Use whenever the user writes or changes FastAPI code, designs a feature or project layout, reviews a FastAPI PR, or asks about routes, dependency injection, Pydantic schemas, SQLAlchemy sessions and transactions, errors, settings, auth, background jobs or API tests, even if they only ask for an endpoint, a CRUD module or a code review.
---

# FastAPI application standards

These standards keep FastAPI services maintainable and testable by keeping business decisions out of HTTP handlers, ORM models, repositories and jobs. Apply them when writing code and when reviewing or refactoring it.

Baseline: Python 3.11+, FastAPI with `Annotated` dependencies, Pydantic v2, SQLAlchemy 2.x. On older versions, adapt the syntax and keep the structure. Containers and deployment are covered by `fastapi-docker`; docs by `fastapi-documentation`.

## The core idea

Dependencies point inward: routes call use cases, use cases call domain rules, and infrastructure (database, external APIs) implements interfaces the inner layers define. The same rule ("is this refund allowed?") must behave identically whether HTTP, a scheduled job, a queue consumer or a CLI triggers it.

Quick test for where code belongs: *would this decision still be needed if the app were called from a CLI or a message consumer?* If yes, it is a domain rule or use case, not route code.

## Non-negotiable rules

Merge blockers. Flag any violation; if the user's request would break one, say so and propose the compliant alternative before writing code. Section numbers point to the detail.

1. No business decisions in API routes (§4).
2. No FastAPI, SQLAlchemy or vendor SDK imports in the domain layer (§1, §5).
3. Use cases express application actions and are reusable from HTTP, CLI, jobs and consumers (§6, §18).
4. Infrastructure implements technical details behind explicit boundaries (§7).
5. Business rules are testable without a web server or production database (§16).
6. Transactions, authorization, retries and side effects are explicit (§6, §10, §14).
7. Prefer clear, boring code over unnecessary abstraction (§23).

## Right-size the structure

- **Tiny endpoint or prototype:** thin route, real logic in a plain function or class; skip ports and mappers.
- **Growing service:** add use cases and a repository once more than one caller needs the logic or persistence details start leaking.
- **Complex domain:** the full domain / application / infrastructure / api split per feature module.

Keep the dependency direction at every size. Don't add factories, repositories or services just to follow a pattern.

## Building a feature

Work in this order so business rules stay framework-independent. Exploratory work can wander, but the result must keep the boundaries.

1. Define the business rule: invariants, decisions, failure cases.
2. Create or update domain types and policies.
3. Define the use case: inputs, outputs, dependencies, workflow.
4. Define ports (repository or integration interfaces) only where needed.
5. Implement the infrastructure adapters.
6. Wire dependencies with `Depends` at the API boundary.
7. Expose the route with request/response schemas and error mapping.
8. Test per layer: domain unit tests, then integration, then API.
9. Review authorization, transactions, retries, timeouts and logging.
10. Document the contract with `fastapi-documentation`; done when its `scripts/check_docs.py` passes.

Read the relevant reference before writing code: it holds the concrete patterns (thin route, use case, repository `Protocol`, session dependency, exception handlers, app factory and lifespan, test fixtures).

## Reviewing code

1. Check the rules above, then the anti-patterns and checklist in `references/review-checklist.md`.
2. Group findings as **blockers** (rule violations, security, data integrity), **should fix** (reliability, testability, maintainability) and **suggestions**.
3. For each, cite the section, show the problem, and give a minimal fix in the existing code's style.
4. Say what is already done well. Don't manufacture findings, and don't demand the full layered architecture from a small script.
5. If an endpoint, setting or error code changed without the docs following, that is **should fix**.

## Where to find details

Read only the file the task needs. Section numbers are stable, so "(section 12)" always resolves here.

| Task involves | Read | Sections |
|---|---|---|
| Layout, layer responsibilities, thin routes, domain model, use cases, repositories, external integrations | `references/architecture.md` | 1-7 |
| Pydantic schemas, dependency injection, sessions and transactions, sync vs async, errors | `references/boundaries-and-data.md` | 8-12 |
| Settings and secrets, auth, logging and health, testing, API design, background jobs, performance, code style, app lifecycle, tooling | `references/operations.md` | 13-22 |
| Anti-patterns and the definition-of-done checklist | `references/review-checklist.md` | 23-24 |

A new endpoint usually needs sections 4, 6, 8, 9 and 12; a PR review needs `review-checklist.md` plus whatever the diff touches.

## Output expectations

- Follow the reference patterns: `Annotated` dependency aliases, return annotations instead of a redundant `response_model=`, domain errors without HTTP status codes, explicit transaction boundaries, no `try/except` in routes for domain errors.
- When a standard conflicts with the user's instruction or an existing project convention, follow the user and name the trade-off in a sentence or two.
- Reference code is abbreviated: add imports and project names when generating real code.
