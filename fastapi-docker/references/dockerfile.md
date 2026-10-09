# Dockerfile reference

## Contents

- Multi-stage Dockerfile (uv, lock file)
- Variant with pip and a pinned requirements file
- .dockerignore
- Private package index via BuildKit secret mount
- Healthcheck and runtime command
- Build and verification commands

## Multi-stage Dockerfile (uv, lock file)

Preferred when the project has a `uv.lock`. Dependencies are installed into a
virtual environment in the builder stage; the runtime stage copies only that
environment and the application code.

```dockerfile
# syntax=docker/dockerfile:1.7

# ---- builder -------------------------------------------------------------
FROM python:3.14-slim-trixie AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

# Pin uv to a known version for reproducible builds.
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /usr/local/bin/uv

WORKDIR /build

# Install dependencies first so code changes do not invalidate this layer.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# Now copy the application and install the project itself.
COPY app ./app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# ---- runtime -------------------------------------------------------------
FROM python:3.14-slim-trixie AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_ENV=production

# Fixed numeric UID/GID so policies (Kubernetes runAsUser, etc.) can reference it.
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /srv

# Only the virtualenv and app code come from the builder. Files are owned by
# root and readable by everyone, so the app user cannot modify its own code.
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /build/app ./app
COPY --from=builder /build/pyproject.toml ./

USER 10001:10001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=2).status == 200 else 1)"]

# Exec form, so uvicorn receives SIGTERM directly. Proxy settings come from
# environment variables so the same image works in every environment.
CMD ["sh", "-c", "exec uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips=\"${FORWARDED_ALLOW_IPS:-127.0.0.1}\" --timeout-graceful-shutdown 20"]
```

Notes on the choices above:

- `--mount=type=cache` keeps the uv download cache out of the image while
  speeding up rebuilds.
- `--locked` fails the build if `uv.lock` is out of date with
  `pyproject.toml`, so the image always matches the reviewed lock file.
- The `sh -c` wrapper with `exec` is used only so the proxy address can come
  from an environment variable. `exec` replaces the shell, so uvicorn still
  becomes PID 1 and receives signals.
- `FORWARDED_ALLOW_IPS` defaults to loopback, which trusts no external proxy.
  Set it to the load balancer or ingress address in each environment.
- The app uses a factory (`create_app`) per `fastapi-standards`. If the app
  is a plain module-level `app`, use `app.main:app` and drop `--factory`.

## Variant with pip and a pinned requirements file

Use this when the project has no uv lock. The requirements file must be fully
pinned, ideally generated with hashes (for example `pip-compile --generate-hashes`).

```dockerfile
# syntax=docker/dockerfile:1.7

FROM python:3.14-slim-trixie AS builder

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --require-hashes -r requirements.txt

FROM python:3.14-slim-trixie AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /srv
COPY --from=builder /opt/venv /opt/venv
COPY app ./app

USER 10001:10001
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=2).status == 200 else 1)"]

CMD ["sh", "-c", "exec uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips=\"${FORWARDED_ALLOW_IPS:-127.0.0.1}\" --timeout-graceful-shutdown 20"]
```

`--require-hashes` makes the build fail if any package differs from the hash
recorded in the lock, which protects against a tampered or replaced package.

## .dockerignore

Place it next to the Dockerfile. Anything not needed at build or runtime stays
out of the build context.

```text
# Version control and editor files
.git
.gitignore
.vscode
.idea

# Secrets and local environment (never send these to the daemon)
.env
.env.*
!.env.example
*.pem
*.key

# Python caches and build output
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
.venv/
venv/
dist/
build/
*.egg-info/

# Tests, docs, and tooling not needed at runtime
tests/
docs/
*.md
compose*.yml
Dockerfile*
.dockerignore

# Local data
data/
*.sqlite3
```

The `.env.*` rule with an explicit `!.env.example` exception keeps the template
while excluding real environment files. Do not rely on `.dockerignore` alone to
protect secrets; keep them out of the repository too.

## Private package index via BuildKit secret mount

When a build needs a credential, mount it as a secret for a single `RUN`. It
never enters a layer and does not appear in `docker history`.

```dockerfile
RUN --mount=type=secret,id=pip_index_url \
    uv pip install --index-url "$(cat /run/secrets/pip_index_url)" ...
```

Build with:

```bash
DOCKER_BUILDKIT=1 docker build --secret id=pip_index_url,src=./pip_index_url.txt -t myapi:dev .
```

Do not write `ARG PIP_TOKEN` followed by `RUN pip install ... $PIP_TOKEN`.
`docker history` shows build arguments, so the token would be recoverable from
any image that was built this way.

## Healthcheck

The `HEALTHCHECK` above uses the standard library, so the slim image does not
need `curl`. It checks liveness only, as described in `SKILL.md`. Do not point
it at a readiness endpoint that queries the database: a database outage would
then mark every container unhealthy and trigger restarts that do not fix
anything.

If the platform (Kubernetes, ECS) uses its own probes, the Dockerfile
`HEALTHCHECK` is ignored or duplicated. Keep the platform probe as the source of
truth and remove the Dockerfile one.

## Build and verification commands

```bash
# Build with a fixed tag from the git commit, never "latest"
docker build -t myapi:$(git rev-parse --short HEAD) .

# Confirm the runtime user is not root
docker run --rm --entrypoint id myapi:$(git rev-parse --short HEAD)
# expect uid=10001(app)

# Scan for known vulnerabilities before pushing
trivy image --severity HIGH,CRITICAL --ignore-unfixed myapi:$(git rev-parse --short HEAD)

# Check that no secret-looking strings ended up in the image
docker history --no-trunc myapi:$(git rev-parse --short HEAD) | grep -i -E 'password|secret|token' || echo "clean"
```

Keep the `--entrypoint id` check in CI as an assertion so a future Dockerfile
change that re-introduces root fails the build.
