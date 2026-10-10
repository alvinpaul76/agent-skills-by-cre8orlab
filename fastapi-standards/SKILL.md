---
name: fastapi-standards
description: Engineering standards for building, reviewing, and refactoring FastAPI services with a layered architecture (routes, use cases, domain, infrastructure). Use this skill whenever the user is writing or changing FastAPI code, designing a new FastAPI service or feature, structuring a Python API project, reviewing a FastAPI pull request, or asking about routes, dependency injection, Pydantic schemas, SQLAlchemy sessions and transactions, error handling, background jobs, API testing, or project layout in a FastAPI codebase. Trigger even if the user does not mention "best practices" or "architecture" and just asks for an endpoint, a CRUD module, a service class, or a code review of a FastAPI file.
---

# FastAPI Application Engineering Standards

These standards keep FastAPI services maintainable and testable by keeping
business decisions out of HTTP handlers, ORM models, repositories, and jobs.
Apply them when writing new code and when reviewing or refactoring existing
code.

Baseline assumed: Python 3.11+, FastAPI with `Annotated` dependencies,
Pydantic v2, SQLAlchemy 2.x. If the project is on older versions, adapt
syntax but keep the structure.

## The core idea

Business decisions belong in the domain and application layers. Dependencies
point inward: API routes call application use cases, use cases call domain
rules, and infrastructure (database, external APIs) implements interfaces the
inner layers define. This matters because the same rule (for example, "is
this refund allowed") must behave identically whether it is triggered by
HTTP, a scheduled job, a queue consumer, or a CLI command.

Quick test for where code belongs: *would this decision still be required if
the app were called from a CLI or a message consumer?* If yes, it is a domain
rule or use case, not route code.

## Non-negotiable rules

Treat these as merge blockers. Flag any violation, and if the user's request
would break one, say so and propose the compliant alternative before writing
the code.

1. No business decisions in API routes.
2. No FastAPI, SQLAlchemy, or vendor SDK imports in the domain layer.
3. Use cases express application actions, orchestrate work, and are reusable
   from HTTP, CLI, jobs, and consumers.
4. Infrastructure implements technical details behind explicit boundaries.
5. Business rules are testable without a web server or production database.
6. Transactions, authorization, retries, and side effects are explicit.
7. Prefer clear, boring, maintainable code over unnecessary abstraction.

## Right-size the structure

The standards describe a full layered layout, but a small service does not
need every directory on day one. Match the structure to the complexity:

- **Tiny endpoint or prototype:** keep routes thin, put real logic in a plain
  function or class, and skip ports and mappers.
- **Growing service:** add use cases and a repository when more than one
  caller needs the logic or when persistence details start leaking.
- **Complex domain:** use the full domain / application / infrastructure /
  api split per feature module.

Preserve the dependency direction at every size. Do not add factories,
repositories, or services merely to follow a pattern.

## Workflow: building a feature

Follow this order so business rules stay framework-independent:

1. Define the business rule: invariants, decisions, failure cases.
2. Create or update domain types and policies.
3. Define the use case: inputs, outputs, dependencies, workflow.
4. Define ports (repository or integration interfaces) only where needed.
5. Implement infrastructure adapters.
6. Wire dependencies with `Depends` at the API boundary.
7. Expose the route with request/response schemas and error mapping.
8. Test per layer: domain unit tests first, then integration, then API.
9. Review security and reliability: authorization, transactions, retries,
   timeouts, logging.
10. Document the contract (use the `fastapi-documentation` skill).

For concrete code patterns (thin route, use case, repository `Protocol`,
session dependency, exception handlers, app factory and lifespan, test
fixtures), read the reference files listed below before writing code.

## Workflow: reviewing code

1. Read the code against the non-negotiable rules first, then the anti-pattern
   list and checklist in `references/review-checklist.md`.
2. Report findings grouped by severity: **blockers** (rule violations,
   security, data integrity), **should fix** (reliability, testability,
   maintainability), **suggestions**.
3. For each finding, cite the section number, show the problem line or
   pattern, and give the corrected version. Keep fixes minimal and in the
   style of the existing code.
4. Say what is already done well. Do not manufacture findings.
5. If the code is a small script or prototype, do not demand the full
   layered architecture; call out only what would cause real problems.

## Where to find details

The full standards are split by topic. Section numbers are preserved so
cross-references like "(section 12)" resolve using this map. Read only the
file(s) relevant to the task.

| Task involves | Read | Sections |
|---|---|---|
| Project layout, layer responsibilities, thin routes, domain model, use cases, repositories and external integrations | `references/architecture.md` | 1-7 |
| Pydantic schemas, dependency injection and wiring, DB sessions and transactions, sync vs async, error taxonomy and exception handlers | `references/boundaries-and-data.md` | 8-12 |
| Settings and secrets, auth and security, logging and health, testing strategy, API design and versioning, background jobs, performance, code style, app lifecycle and deployment, tooling | `references/operations.md` | 13-22 |
| Anti-patterns, definition of done, non-negotiable rules detail, implementation order | `references/review-checklist.md` | 23-25 |

Common pairings: a new endpoint usually needs `architecture.md` (sections 4,
6) and `boundaries-and-data.md` (sections 8, 9, 12); a PR review needs
`review-checklist.md` plus whichever area the diff touches.

## Output expectations

- Generate code that follows the patterns in the references: `Annotated`
  dependency aliases, return-type annotations instead of redundant
  `response_model=`, domain errors without HTTP status codes, explicit
  transaction boundaries, no `try/except` in routes for domain errors.
- When a standard conflicts with the user's explicit instruction or an
  existing project convention, follow the user, but mention the trade-off in
  one or two sentences so it is a conscious choice.
- Code samples in the references are abbreviated. Add imports and
  project-specific names when generating real code.
