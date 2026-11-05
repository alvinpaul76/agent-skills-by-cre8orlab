# Generalize docs-drift-reminder beyond FastAPI

Status: resolved
Type: task

## Answer
`docs-drift-reminder` was FastAPI-only. FastAPI behavior is unchanged (`.py` under `app/`, `docs/`, skill installed: run `check_drift.py`, exit 2 on DRIFT). Any other project now gets a generic fallback: after an edit to a source file (`.py .js .jsx .ts .tsx .go .rs .java .kt .rb .php .cs .swift .sh`), if `docs/` or `README.md` exists, it reminds the agent once per session (marker file in the temp dir keyed by `session_id`) and exits 2. Edits under `docs/` and non-source files are ignored. The skill is no longer required to install the hook.

Tests: `is_source` and once-per-session cases added to `test/docs_drift_reminder_test.py`. Docs: `docs/hooks/docs-drift-reminder.md` and the README hooks table.
