# fastapi-documentation

Writes documentation for a FastAPI service that people who are not developers —
product owners, support, testers, new teammates — can understand and use.

New to a word? See the [word list](../glossary.md). · skill folder:
[`fastapi-documentation/`](../../fastapi-documentation/)

## When does the agent use it?

Whenever you ask it to document a FastAPI app or its endpoints, write API docs or
a user guide, explain the API to non-technical readers, onboard someone, split a
long README, or refresh docs after adding or changing an endpoint.

## What it produces

- `README.md`: a short project summary with a table linking every API page
- `docs/architecture.md`: how the service works, plain words first
- `docs/apis/<feature>.md`: one page per API feature
- `docs/troubleshooting.md`: symptoms, causes, and fixes
- `docs/glossary.md`: only the terms the docs actually use
- `docs/deployment.md`: only when running the service needs more than one command

## What is inside?

| File | What it holds |
| --- | --- |
| `SKILL.md` | The workflow and the rules the docs must follow |
| `references/plain-language.md` | Word rules, before/after examples, glossary starter |
| `references/templates.md` | Page layouts for the README and every docs page |
| `scripts/check_docs.py` | A checker that fails on broken links, unlinked API pages, unbalanced code fences, missing titles, and leaked secrets |

## How does it work inside?

1. The agent learns the app from the code — routers, auth, settings, tests — and
   runs real requests so every example is genuine, never invented.
2. It writes the pages in template order and keeps each fact on the one page that
   owns it; other pages link instead of repeating.
3. The README becomes a project summary: what the project is for, a table of the
   APIs, how to get running, and links — endpoint detail stays on the API pages.
4. It finishes by running `check_docs.py` and a newcomer reading test on every
   page.

## What it deliberately avoids

- Developer jargon without explanation; a term is explained in place or added to
  the glossary.
- Rewriting existing docs from scratch when a page only needs an update.
- Real secrets in any example; keys appear as `<your-api-key>`.

Pair it with [fastapi-standards](fastapi-standards.md): that skill's
documentation step and review checklist already point here.

Back to [how skills work](../how-skills-work.md).
