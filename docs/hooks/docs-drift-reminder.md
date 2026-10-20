# docs-drift-reminder (hook)

A Claude Code hook that reminds the agent to update a FastAPI project's docs when
it edits the code and the docs no longer match.

New to a word? See the [word list](../glossary.md). · hook folder:
[`hooks/docs-drift-reminder/`](../../hooks/docs-drift-reminder/)

This is a hook, not a skill. It runs on its own after edits. It works with the
[fastapi-documentation](../skills/fastapi-documentation.md) skill, which supplies the
check it runs.

## Install

Needs Node.js, Python 3, and the fastapi-documentation skill installed in
`~/.claude/skills/`:

```bash
npx github:alvinpaul76/agent-skills-by-cre8orlab install docs-drift-reminder
npx github:alvinpaul76/agent-skills-by-cre8orlab status docs-drift-reminder
npx github:alvinpaul76/agent-skills-by-cre8orlab uninstall docs-drift-reminder
```

Then restart Claude Code and check `/hooks`. The installer works the same way as for
[quiet-command-output](quiet-command-output.md#install): it merges one entry into
`~/.claude/settings.json`, backs the file up first, and leaves your other hooks alone.

## What does it do?

After the agent edits or writes a `.py` file under the project's `app/` folder, the
hook runs the skill's `check_drift.py`. That check compares the code with the docs:
routes, settings, and error codes must all be documented, and nothing documented may
be gone.

- **Docs match:** the hook says nothing.
- **Docs have drifted:** the hook sends the `DRIFT` lines back to the agent, such as
  `setting DOCUMENT_MAX_BYTES is missing from docs/architecture.md`, so it can fix
  the page right away.

## Things to know

- **A new route, setting, or error code triggers a reminder at once.** The code is
  edited before the docs, so the reminder is expected. Update the docs in the same
  change.
- **It only acts when it fits.** It does nothing if the project has no `docs/` folder,
  if the skill is not installed, or if the file is outside `app/`.
- **Other app entry points.** The check loads `app.main:create_app`. For a different
  one, set `DOCS_DRIFT_APP`, for example `DOCS_DRIFT_APP=service.main:build_app`.
- **Speed.** Each check imports the app, which takes about a second. It uses `uv run`
  when `uv` is installed, so the project's own packages are available.
- **Not Windows.** The settings entry calls `python3`.

## Back to

[Installing skills](../installation.md) · [how skills work](../how-skills-work.md)
