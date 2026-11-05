# Add docker-compose-standards skill and slim the Docker skills

Status: resolved
Type: task

## Answer
Added `skills/docker-compose-standards/SKILL.md`: Compose file naming, external images set by one pinned `<SERVICE>_IMAGE` variable (`${VAR:?}`, no defaults), `.env.example` coverage, `:?` vs `:-`, recreate after `.env` changes, and `docker compose --env-file .env.example config -q` as the minimum check. New page `docs/skills/docker-compose-standards.md`; added to the README table, the tree in `docs/how-skills-work.md` and the symlink loop in `docs/installation.md`.

`fastapi-docker`: shorter description; rules, hardening and review steps no longer repeat each other; Compose rules moved to the shared skill. Fixed: dev override ran the builder stage as root with wrong paths (now runtime stage, `./app:/srv/app`); `uv sync` installed the project editable (now `--no-editable`); `.dockerignore` dropped `README.md` that build backends need; pip removal hardcoded `python3.14`; Postgres image hardcoded (now `${POSTGRES_IMAGE:?}`); mixed `mem_limit`/`deploy.resources`. Settings code for `DATABASE_PASSWORD_FILE` moved to fastapi-standards section 13 as a rule.

`infisical-docker-agent`: consumer image is a pinned variable; `:alpine` advice now pins a version; note that the wrapper overrides the image `CMD` (FastAPI consumers and `migrate`); limits under `deploy.resources`; docs step shortened.
