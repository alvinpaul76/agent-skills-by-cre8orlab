# Detect docs that drift from the code, and remind the agent with a hook

Status: resolved
Type: task

## Answer
The fastapi-documentation skill could only check the docs against themselves, so it
could not tell when the code had moved on. Added:

- `skills/fastapi-documentation/scripts/check_drift.py`: imports the app and fails
  when a route, settings field, or error code is missing from the docs, or when the
  docs describe one the code no longer has. It also flags variables in
  `docker-compose.yml` and `.env.example` that the app does not read. Routes come
  from `app.openapi()`, because current FastAPI nests routers and `app.routes` is
  empty of real routes.
- `skills/fastapi-documentation/SKILL.md`: step 7 now runs both checkers, and a new
  "Updating docs after a code change" section maps each kind of code change to the
  pages to edit.
- `hooks/docs-drift-reminder/`: a PostToolUse hook for `Edit|Write`. After an edit
  to a `.py` file under `app/`, it runs the drift check and sends the `DRIFT` lines
  back to the agent (exit 2). Silent when nothing drifted, when the file is
  elsewhere, or when the project has no `docs/` or the skill is missing. The app
  entry point defaults to `app.main:create_app` and can be set with `DOCS_DRIFT_APP`.
- `docs/hooks/docs-drift-reminder.md`, updates to `docs/skills/fastapi-documentation.md`
  and `README.md`, and `test/docs_drift_reminder_test.py`.

Tested against the craft-by-cre8orlab project: no output when docs match; removing a
settings row gave a `DRIFT` line and exit 2; a README edit was ignored. Install,
status, and uninstall were run in a throwaway HOME. `npm test` passes. Not yet tested
inside a live Claude Code session installed through the GitHub URL (needs a push).

## Comments
