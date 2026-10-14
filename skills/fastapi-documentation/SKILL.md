---
name: fastapi-documentation
description: "Write or update documentation for a FastAPI service so that people who are not developers (product owners, support, testers, new teammates) can understand and use it. Produces a short README, a plain-language overview of how it works, one page per API feature, a troubleshooting page, a glossary, and an optional deployment page. Use whenever the user asks to document a FastAPI app or its endpoints, write API docs or a user guide, explain the API to non-technical people, onboard someone, split a long README, or refresh the docs after adding or changing an endpoint, even if they never say 'documentation skill'."
---

# FastAPI documentation

Write docs that someone who has never seen the code can follow. A developer-only
page forces every newcomer to interrupt a developer; a plain page does not, and
developers skim it faster too.

Before writing anything, read `references/plain-language.md` (word rules, a glossary
starter, before/after examples). Take page layouts from `references/templates.md`.

## What gets produced

```
README.md                  project summary: purpose, APIs table linking to docs, get running, links
docs/
├── architecture.md        how it works, in plain words first, details after
├── apis/<feature>.md      one page per feature (named for what it does, not its URL)
├── troubleshooting.md     symptoms, causes, fixes; status codes in plain words
├── glossary.md            only the terms the docs use
└── deployment.md          only if running it needs more than one command
```

Match the size to the service. One router with one or two endpoints needs the
README, one API page, and a short troubleshooting page. Add the rest only when
there is something to say.

## Steps

### 1. Learn the app from the code, then run it

Find with search, not guesswork: the app factory (`create_app` or `FastAPI(...)`),
every `APIRouter` and `include_router` prefix, middleware, exception handlers,
startup hooks, auth dependencies, and the settings and environment variables. Read
the tests: they hold realistic example requests. Read any existing README and docs
so you extend them instead of replacing them. Also learn what the project is *for*
(README, `pyproject.toml` description, folder names). If it is not clear, ask the owner one
question; the README summary is only as good as this answer.

Then get real examples: call the endpoints with the test client or the running app,
using the `mock` backend or a placeholder key, and keep the actual answers.

Done when: you have a table of `{router, path, who may call it, what it is for}`
covering every route (cross-check `grep -rn "include_router\|APIRouter"` for
strays), and one real request and answer per route.

### 2. Write `docs/architecture.md`

Follow the template. Open with the plain-words summary and one diagram of a
request's journey. Details (folders, settings table, rules for new APIs) come after.
The error codes are listed once, in troubleshooting; link to them.

Done when: no sentence is true of only one endpoint (those move to step 3), and
every technical term is explained where it first appears or links to the glossary.

### 3. Write one `docs/apis/<feature>.md` per router group

Follow the template: purpose, how to use it, what to send, what comes back, how it
works inside, what can go wrong. Take limits from the code and name the file each
comes from.

Done when: every route on that router is documented, every limit quoted exists in
the code, and every example came from a real run.

### 4. Write `docs/troubleshooting.md` and `docs/glossary.md`

Troubleshooting starts from what the reader sees ("I get 401") and gives the cause,
a check, and the fix. Keep only the status codes this API returns. The glossary holds
the terms the docs use, one plain sentence each.

Done when: every error code the API returns appears in troubleshooting with its exact
`code` string and a "what to do" line, and there is one real error body.

### 5. Write `docs/deployment.md` only if needed

Secrets and keys, choosing a backend or mode, Docker and compose notes, and settings
that switch protections on or off. Each setting says what it does, the safe value for
production, and the risk of the other value. If running is just `uv run <cmd>`, skip
this file.

### 6. Rewrite README.md as the project summary

The README describes the project, not one API: its purpose, an **APIs** section, how to get
it running, and links. The APIs section is a table with one row per `docs/apis/<feature>.md`
(name, one plain sentence, link). It is the front door to the API pages, so a project with
several APIs shows all of them and a new API is easy to find. First requests, endpoint
paths and example answers live on the API pages, not here.

Follow the template.

Done when: every `docs/apis/*.md` is linked from the README's APIs table, a newcomer can get
a running and ready service from the README alone, and the README has no endpoint paths or
request and response examples.

### 7. Check

Run the checker, then do the reading test.

```bash
python <skill-dir>/scripts/check_docs.py <repo-root>
```

It fails on broken links or heading anchors, an API page the README does not link to,
unbalanced code fences, pages without a title and purpose
line, and text that looks like a real secret. It warns about developer jargon: for
each warning, explain the term in place or add it to the glossary.

Reading test, answered by rereading as a newcomer would:
- Can I tell in the first three lines of each page what it is for?
- Is there a word I would have to ask a developer about?
- Could I do the first task by following the steps exactly?
- Does each example match what the code really returns?
- Does the README tell me what the project is for and list every API, without teaching one API?

## Rules

- **Facts live once.** A limit, default or error code is written on the one page that
  owns it and linked from the others (other pages say "the size limit" and link, they
  do not repeat the number). The owning page quotes the source file. After writing,
  search the docs for each number to confirm it appears once.
- **Examples are real.** Run them. Never invent output.
- **Secrets stay out.** Use `<your-api-key>` placeholders. Never print values from a
  `.env` file or paste a real key, even partly.
- **Update, do not rewrite.** When docs exist, extend the affected page and refresh
  shared pages only where the code changed them. Keep the reader's links working.
- **Explain why.** A rule or limit with its reason is easier to trust and remember.
- Put `docs/` in `.dockerignore` when the project has one.
