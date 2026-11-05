---
name: fastapi-docker
description: Container and deployment standards for FastAPI and Python API services - multi-stage Dockerfiles, .dockerignore, uvicorn behind a proxy, healthchecks, migrations, secrets, hardening, image scanning, and Compose with Postgres. Use when writing, reviewing or debugging any of these, when containerizing or deploying a Python API, or when a container exits, fails health checks or shows CVEs, even if the user never says "Docker".
---

# FastAPI container standards

Goal: small, reproducible images that run as non-root, contain no secrets, and behave the same locally and in production. Scope is the container and runtime layer. Related skills: `fastapi-standards` (app code and the settings object), `docker-compose-standards` (Compose file names, image pinning, `.env.example`), `infisical-docker-agent` (when secrets come from Infisical, it replaces the secrets approach below).

## Base images

- **Python:** the newest release every dependency ships wheels for (3.14 today, else 3.13). Check FastAPI, Pydantic, SQLAlchemy, the Postgres driver and any C extensions. If the code must share an interpreter with Odoo 18 or other tooling, use the version that environment supports and confirm it in that project's docs.
- **Image:** `python:3.14-slim-trixie`. Avoid Alpine: most wheels target glibc, so musl builds compile from source and native dependencies break.
- **Postgres:** latest stable major (18) with a full minor tag, on the same Debian release as the app image so system libraries match.

## Rules

Blockers. If a request would break one, explain the risk and offer the compliant version.

1. Runs as a non-root user with a fixed numeric UID (10001), so platform policies can reference it.
2. No secrets in the image (`ENV`, `ARG`, copied files, layers). Build-time credentials use `RUN --mount=type=secret`; `ARG` values show in `docker history`.
3. Base images pinned (by digest in production); dependencies installed only from a lock file (`uv.lock`, or `requirements.txt` with hashes).
4. Migrations run as a separate step, never at container startup, because replicas would race.
5. Binds `0.0.0.0` on non-privileged port 8000.
6. No `--reload`, debug mode, or open `/docs`, `/redoc`, `/openapi.json` in production.
7. `.dockerignore` keeps `.env`, `.git`, caches and tests out of the build context.

Production hardening (should fix): `read_only: true` with `tmpfs` for writable paths; `cap_drop: [ALL]`; `no-new-privileges:true`; limits under `deploy.resources.limits`; no pip, uv or compilers after the final `FROM`; OS patches applied at build; image scanned in CI and rebuilt on a schedule.

## Runtime

- One uvicorn process per container; scale with replicas. If a container genuinely needs several workers, use gunicorn with `uvicorn.workers.UvicornWorker`.
- Behind a proxy: `--proxy-headers --forwarded-allow-ips=<proxy-ip-or-cidr>`. Never `*` on a publicly reachable port.
- `--timeout-graceful-shutdown 20` (at least the slowest request), so SIGTERM doesn't cut requests off.
- Exec-form `CMD`, or `sh -c "exec …"`, so uvicorn is PID 1 and receives signals.

## Healthchecks

Liveness (`/health/live`) touches no dependencies: a database outage must not restart every container. Readiness (`/health/ready`) checks the database with a short timeout and gates routing, not restarts. The Dockerfile `HEALTHCHECK` calls liveness with the Python standard library, so the slim image needs no `curl`. On Kubernetes or ECS the platform probes replace it.

## Migrations

Compose: a `migrate` service with `restart: "no"` running `alembic upgrade head`, which `api` depends on with `condition: service_completed_successfully`. Kubernetes: a Job. Keep each migration compatible with the running version so rolling deploys survive the overlap.

## Secrets

Configuration comes from environment variables through the settings object; never log it or a connection string. Under Compose, passwords come from Docker secret files (`DATABASE_PASSWORD_FILE`), not `.env`. In production use the platform's secret store, or Infisical via `infisical-docker-agent`.

## Reviewing

Check the rules, then the image (stages, pinning, lock file, `.dockerignore`, dependency layer before code), runtime, and Compose (dependency conditions, exposure, volumes, hardening, `docker-compose-standards`). Scan the built image rather than guessing CVEs from the Dockerfile text. Report findings as blocker, should fix, or suggestion, with corrected lines; say what is already right, and don't invent problems in a correct file.

## References

Read only the one the task needs.

- `references/dockerfile.md`: uv and pip Dockerfiles, `.dockerignore`, secret mount, build checks.
- `references/compose.md`: app, migrate and Postgres stack; dev override; common failures.
- `references/security-scanning.md`: scanning, tracing a finding to its source, fixes, CI gating.
