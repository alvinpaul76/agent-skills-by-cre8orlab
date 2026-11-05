# fastapi-standards: remove duplication, fix example bugs

Status: resolved
Type: task

## Answer
- `SKILL.md`: shorter description; rules now carry their section numbers, so the duplicate list in section 24 and the duplicate implementation order (section 25) were removed from `review-checklist.md`.
- Fixed: the factory example ended with `app = create_app()`, contradicting the rule above it (now `--factory`); hidden docs still exposed `/openapi.json` (now `openapi_url` follows `expose_docs`); test fixture read `.env.test` instead of the `make_settings()` helper; `HTTP_422_UNPROCESSABLE_ENTITY` replaced with `422` because Starlette renamed the constant.
- Container and Compose items (non-root, proxy headers, migrations, image scanning, `:?` vs `:-`, duplicate `.env` keys) now point to `fastapi-docker` and `docker-compose-standards`.
- Project-specific names (`ClassifierUnavailable`, `classify_many`, mock model backend) generalized; section 19 and 22 trimmed of repeats.
- Added to section 13: `<NAME>_FILE` secrets and a drift test between `config.py` and `.env.example`.
