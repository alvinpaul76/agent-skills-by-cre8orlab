---
name: fastapi-docker
description: Container and deployment standards for FastAPI services, covering Dockerfiles, multi-stage builds, non-root users, uvicorn or gunicorn runtime settings, healthchecks, database migrations as a separate step, secret handling, and Docker Compose for local development with Postgres. Use this skill whenever the user writes, reviews, or debugs a Dockerfile, .dockerignore, docker-compose.yml, or container runtime setup for a FastAPI or Python API service, asks how to containerize a FastAPI app, wants to run FastAPI with Postgres in Docker, or asks about container security hardening, image size, or getting uvicorn to behave behind a proxy in a container. Also use it when the user says "deploy this", "put this in a container", or "why does my container exit or fail health checks", even if they never say "Docker".
---

# FastAPI Container Standards

These standards produce images that are small, reproducible, run without
root, carry no secrets, and start the same way locally and in production.
They cover the container and runtime layer only. For code structure (routes,
use cases, repositories, errors), use the `fastapi-standards` skill.

## Choosing the base images

- **Python:** 3.14 is the default for new services. It is the current release
  line, with bugfix support until October 2027 and security fixes until
  October 2030. Before pinning it, confirm that every dependency publishes
  3.14 wheels (FastAPI, Pydantic, SQLAlchemy, the Postgres driver, and any
  C extensions). If one does not, use 3.13, which receives security fixes
  until October 2029. Avoid starting new services on 3.12 unless something
  requires it.
- **Shared environments:** if the service runs in the same environment as
  Odoo 18 or other Python tooling tied to older interpreters, pin the Python
  version that environment supports, and verify the requirement against that
  project's current documentation before deciding.
- **Debian:** trixie (Debian 13) is the current default. Alpine is avoided
  because most Python wheels target glibc, so musl builds often compile from
  source and native dependencies fail or slow down.
- **Postgres:** use the latest stable major (18.x) and a fixed minor tag.

## Non-negotiable rules

Treat these as blockers. If a request would break one, explain the risk and
offer the compliant version.

1. The container runs as a non-root user with a fixed numeric UID.
2. No secrets in the image: not in `ENV`, `ARG`, `COPY`ed files, or layers.
   Secrets come from the runtime environment or a secrets mechanism.
3. Base images are pinned to a specific version. Never `latest`, never an
   unpinned `python` tag in production.
4. Migrations do not run as part of container startup. They run as a
   separate, explicit step.
5. The app binds to `0.0.0.0` inside the container on a non-privileged port
   (8000 by default). Privileged ports are not used.
6. No `--reload`, debug mode, or interactive API docs exposed in production
   images.
7. The build context is limited by `.dockerignore`, so `.env`, `.git`, caches,
   and test artifacts never reach the image.

## Dockerfile shape

Use a multi-stage build: one stage compiles or installs dependencies, a
second stage holds only the runtime. Read `references/dockerfile.md` for the
complete example, including the `uv` variant and the BuildKit secret mount
for private package indexes.

The essentials:

- Start from a slim official Python image pinned to a minor version and a
  Debian release: `python:3.14-slim-trixie`. Use a digest-pinned reference
  in production. Keep the Debian release the same across the app and
  Postgres images so system libraries match.
- Set `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUNBUFFERED=1`.
- Install from a lock file (`uv.lock`, or a pinned `requirements.txt` with
  hashes), never from unpinned `pip install fastapi`.
- Create a system user with a fixed UID (for example 10001), set `USER` to it,
  and copy app files so they are owned by root and readable by the app user.
  The app does not need to write to its own code directory.
- Use exec-form `CMD` so the process receives signals directly.

## Runtime: uvicorn and proxies

- Prefer **one process per container** and scale with replicas. Set
  `--workers` only when you have a reason not to run multiple containers.
  If you do use multiple workers, use gunicorn with `uvicorn.workers.UvicornWorker`,
  which handles worker supervision better.
- Behind a reverse proxy or load balancer, enable proxy headers and trust
  only the proxy's address:
  `--proxy-headers --forwarded-allow-ips=<proxy-ip-or-cidr>`.
  Never use `*` on a publicly reachable port.
- Set a graceful shutdown timeout (`--timeout-graceful-shutdown 20`, adjusted
  to your slowest request) so orchestrators' SIGTERM does not cut requests off.
- Keep `--reload` out of every non-development image.

## Healthchecks

Split liveness from readiness:

- **Liveness** (`/health/live`): returns 200 if the process can serve requests.
  It does not touch the database or any external service. A database outage
  should not restart every container.
- **Readiness** (`/health/ready`): checks dependencies such as the database
  with a short timeout. Use it for load balancer routing and orchestrator
  readiness gates, not for restarts.

Dockerfile `HEALTHCHECK` should call the liveness endpoint with Python's
standard library, so the slim image does not need `curl`. See
`references/dockerfile.md`.

## Migrations

Run migrations as an explicit one-off step before the new version receives
traffic:

- Compose (local): a `migrate` service with `restart: "no"` that runs
  `alembic upgrade head`, which the app service depends on with
  `condition: service_completed_successfully`.
- Kubernetes or similar: a Job or init step, not the app container's `CMD`.
- Never run migrations from the app's startup code, because multiple replicas
  would race each other.

Migrations should be backward compatible with the currently running version,
so a rolling deploy does not break during the window where old and new
containers coexist.

## Secrets and configuration

- Configuration comes from environment variables. The app reads them through
  its settings object (see `fastapi-standards`).
- Local development uses an env file that is git-ignored. Commit an
  `.env.example` with placeholder values instead.
- Production secrets come from the platform's secret store, or from Docker
  secrets / mounted files for Compose. Prefer `DATABASE_PASSWORD_FILE`-style
  file references over raw passwords in environment variables when the
  platform supports it.
- If a build needs a credential (for example a private package index), use
  `RUN --mount=type=secret` with BuildKit. The secret is not stored in any
  layer. Never pass it as `ARG`, because `docker history` reveals it.
- Never log the settings object or connection strings.

## Compose for local development

Read `references/compose.md` for the full file. The key properties:

- Pin the Postgres image version and give it a `healthcheck` (`pg_isready`).
- The app waits on Postgres with `condition: service_healthy`, and on
  migrations with `condition: service_completed_successfully`.
- Postgres is on an internal network. Publish its port to the host only when
  you need local tools to connect, and bind it to `127.0.0.1`.
- Use a named volume for database data.
- The dev override (bind mounts, `--reload`) lives in a separate
  `compose.override.yml` or `compose.dev.yml`. Production-like runs use the
  base file alone.

## Hardening checklist

Apply these to every production service. Compose examples show how.

- Non-root user with fixed UID (Dockerfile).
- `read_only: true` root filesystem, with `tmpfs` for any path that must be
  writable such as `/tmp`.
- `cap_drop: [ALL]` and `security_opt: ["no-new-privileges:true"]`.
- Memory and CPU limits set (`mem_limit`, `cpus` or platform equivalent).
- Image scanned in CI (Trivy, Grype, or the registry's scanner) before
  deployment. Fail on critical or high findings that have fixes available.
- Base images rebuilt on a schedule to pick up OS security patches, because
  pinning the version does not pin the patch level unless you use a digest.
- Interactive docs (`/docs`, `/redoc`, `/openapi.json`) disabled or protected
  in production.
- No package managers, compilers, or build tools in the runtime stage.

## Reviewing a Dockerfile or compose file

1. Check the non-negotiable rules first.
2. Check the image: stage separation, pinned base, lock file, `.dockerignore`,
   layer ordering (dependency install before app code copy, so code changes
   do not reinstall dependencies).
3. Check runtime: exec-form CMD, user, port, signal handling, proxy settings,
   healthcheck.
4. Check compose: healthchecks and dependency conditions, network exposure,
   volumes, secrets, hardening options.
5. Report findings by severity (blocker, should fix, suggestion) with the
   corrected lines. Say what is already correct. Do not invent problems in a
   simple, correct file.

## Reference files

- `references/dockerfile.md`: full multi-stage Dockerfile (pip and uv
  variants), `.dockerignore`, BuildKit secret mount, HEALTHCHECK.
- `references/compose.md`: compose file with app, migrate, and Postgres
  services; dev override; hardening options.
- Read only the file the task needs.
