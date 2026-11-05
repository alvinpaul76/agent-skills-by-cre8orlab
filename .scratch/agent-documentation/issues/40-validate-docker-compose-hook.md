# Add validate-docker-compose hook

Status: resolved
Type: task

## Answer
Added `hooks/validate-docker-compose/` (`hook.json` + `validate-docker-compose.py`): a PostToolUse hook on Edit|Write|MultiEdit that validates the folder of an edited Compose file or `.env.example` against `docker-compose-standards` and exits 2 with the errors so the agent fixes them. The same script runs by hand or in CI (`--json`, `--no-docker`, exit 1 on errors).

Errors: E1 hardcoded image, E2 wrong variable form, E3 missing `.env.example` declaration, E4 floating or unpinned value, E5 invalid YAML or `docker compose --env-file .env.example config -q` failure. Warnings: W1 no patch version, W2 unused `_IMAGE` variable, W3 `.env` differs from `.env.example` (only `_IMAGE` keys are read), W4 check skipped. `build:` services are exempt; anchors and merge keys are resolved by PyYAML; Docker Compose is the fallback parser. Never modifies files.

Tests: `test/validate_docker_compose_test.py` (24 cases, no Docker needed). Docs: `docs/hooks/validate-docker-compose.md`, README hooks list, and the Validate step of `docker-compose-standards`.
