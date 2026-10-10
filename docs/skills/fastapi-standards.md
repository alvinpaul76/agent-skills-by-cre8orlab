# fastapi-standards

Engineering standards for building, reviewing, and refactoring FastAPI services
with a layered architecture (routes, use cases, domain, infrastructure).

New to a word? See the [word list](../glossary.md). · skill folder:
[`fastapi-standards/`](../../fastapi-standards/)

## When does the agent use it?

Whenever you ask it to write or change FastAPI code — a new endpoint, a CRUD
module, a service class, project structure — or to review a FastAPI pull request.
It triggers even when you never mention architecture, because that is when
standards matter most.

## What is inside?

| File | What it holds |
| --- | --- |
| `SKILL.md` | The core idea, non-negotiable rules, and pointers into the references |
| `references/architecture.md` | Layered architecture, folder layout, dependency rules |
| `references/boundaries-and-data.md` | Pydantic schemas, dependency injection, sessions and transactions, error handling |
| `references/operations.md` | Settings and secrets, auth, logging, testing, API design, background jobs, deployment |
| `references/review-checklist.md` | Anti-patterns, definition of done, implementation order |

The agent reads `SKILL.md` first, then opens only the reference file the task
needs, so a small question does not load the whole rulebook.

## How does it work inside?

1. The agent names the layers your code will touch and keeps business rules in the
   domain and use-case layers, out of HTTP handlers and database models.
2. For a new feature it works through the layers in order: contract, domain, use
   case, infrastructure, routes, tests.
3. For a review it applies the checklist, reports findings by severity, and says
   what is already done well instead of inventing problems.
4. For documentation it hands off to the
   [fastapi-documentation](fastapi-documentation.md) skill.

## What it deliberately avoids

- Demanding the full layered architecture for a small script or prototype.
- Framework detail leaking into the domain, or domain rules leaking into routes.
- Overriding your explicit instructions or existing project conventions without
  saying so — when the standards conflict with them, the agent follows you and
  notes the trade-off.

Pair it with [fastapi-docker](fastapi-docker.md) when the work also touches the
container or deployment setup. Back to [how skills work](../how-skills-work.md).
