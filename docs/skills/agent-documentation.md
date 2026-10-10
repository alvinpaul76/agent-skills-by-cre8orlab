# agent-documentation

Writes documentation for agent skills and plugins that people who are not developers
can understand, install, and use.

New to a word? See the [word list](../glossary.md). · skill folder:
[`agent-documentation/`](../../agent-documentation/)

## When does the agent use it?

Whenever you ask it to document a skill or plugin, write a README for a skills
repository, explain a skill or plugin to non-technical readers, add docs for a new
skill or plugin, or refresh the docs after one changed.

## What it produces

- `README.md`: a short project summary with a Skills table and a Plugins table
- `docs/skills/<name>.md`: one page per skill
- `docs/plugins/<name>.md`: one page per plugin
- `docs/how-it-works.md`, `docs/installation.md`: the shared background
- `docs/troubleshooting.md`: symptoms, causes, and fixes
- `docs/glossary.md`: only the terms the docs actually use

## What is inside?

| File | What it holds |
| --- | --- |
| `SKILL.md` | The workflow and the rules the docs must follow |
| `references/plain-language.md` | Word rules, before/after examples, glossary starter |
| `references/templates.md` | Page layouts for the README and every docs page |
| `scripts/check_docs.py` | A checker for missing pages, unlinked skills and plugins, broken links, listed files that do not exist, leaked secrets, and machine-specific paths |
| `agents/openai.yaml` | Display name and short description for agents that read it |

## How does it work inside?

1. The agent finds every skill folder and plugin, reads their files, and runs or
   traces anything it plans to describe, so no behavior is guessed from a name.
2. It writes one page per skill and plugin from the templates, quoting the real
   trigger description and listing only files that exist.
3. It writes the shared pages and turns the README into a project summary with a
   row for every skill and plugin.
4. It finishes by running `check_docs.py` and a newcomer reading test.

## What it deliberately avoids

- Describing behavior from a name instead of from the files.
- Hiding costs: plugin pages say whether it uses the network, tokens, or permissions.
- Rewriting existing docs from scratch when a page only needs an update.
- Real secrets and machine-specific paths in any example.

It is the sibling of [fastapi-documentation](fastapi-documentation.md), which does the
same job for a FastAPI service.

Back to [how skills work](../how-skills-work.md).
