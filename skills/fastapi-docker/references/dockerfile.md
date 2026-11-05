# Dockerfile reference

## uv with a lock file (preferred)

The builder installs dependencies into a venv; the runtime stage copies only the venv and the app code.

```dockerfile
# syntax=docker/dockerfile:1.7

# ---- builder -------------------------------------------------------------
FROM python:3.14-slim-trixie AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /usr/local/bin/uv

WORKDIR /build

# Dependencies first, so code changes don't invalidate this layer.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# --no-editable: an editable install would point at /build, which the runtime stage doesn't have.
COPY app ./app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

# ---- runtime -------------------------------------------------------------
FROM python:3.14-slim-trixie AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_ENV=production

# OS patches released after the pinned base; pip removed (nothing installs at runtime,
# and its vendored libraries show up as CVEs); fixed-UID user.
RUN apt-get update \
 && apt-get upgrade --yes --no-install-recommends \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /usr/local/lib/python3.*/site-packages/pip* /usr/local/bin/pip* \
 && groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /srv

# Owned by root and readable by the app user, which cannot modify its own code.
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /build/app ./app
COPY --from=builder /build/pyproject.toml ./

USER 10001:10001
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=2).status == 200 else 1)"]

# sh -c only so the proxy address can come from the environment; exec keeps uvicorn as PID 1.
CMD ["sh", "-c", "exec uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips=\"${FORWARDED_ALLOW_IPS:-127.0.0.1}\" --timeout-graceful-shutdown 20"]
```

- `--locked` fails the build when `uv.lock` is out of date, so the image matches the reviewed lock.
- `FORWARDED_ALLOW_IPS` defaults to loopback (trusts no proxy); set it per environment.
- For a module-level `app` instead of a `create_app` factory, use `app.main:app` without `--factory`.
- In production, pin each `FROM` and the uv image by digest (see `security-scanning.md`); the tags here are for readability.

## pip with hashed requirements

Use when there is no `uv.lock`. Only the builder changes; the runtime stage is the same as above, except it copies `app` from the build context.

```dockerfile
FROM python:3.14-slim-trixie AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/opt/venv/bin:$PATH"
WORKDIR /build
RUN python -m venv /opt/venv
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --require-hashes -r requirements.txt
```

Generate the file with hashes (`pip-compile --generate-hashes`); `--require-hashes` fails the build if any package was tampered with or replaced.

## .dockerignore

```text
.git
.gitignore
.vscode
.idea

# Secrets and local environment
.env
.env.*
!.env.example
secrets/
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

# Not needed at runtime
tests/
docs/
*.md
!README.md
docker-compose*.yml
Dockerfile*
.dockerignore
data/
*.sqlite3
```

`!README.md` is kept because build backends fail when `pyproject.toml` declares `readme = "README.md"` and the file is missing. `.dockerignore` is a second line of defence; keep secrets out of the repository too.

## Build-time credentials

```dockerfile
RUN --mount=type=secret,id=pip_index_url \
    uv pip install --index-url "$(cat /run/secrets/pip_index_url)" ...
```

```bash
docker build --secret id=pip_index_url,src=./pip_index_url.txt -t myapi:dev .
```

## Build and verify

```bash
TAG=$(git rev-parse --short HEAD)               # never "latest"
docker build -t myapi:$TAG .
docker run --rm --entrypoint id myapi:$TAG      # expect uid=10001(app); keep as a CI assertion
docker run --rm --entrypoint sh myapi:$TAG -c 'which pip && exit 1 || echo no-pip'
trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 myapi:$TAG
docker history --no-trunc myapi:$TAG | grep -i -E 'password|secret|token' || echo clean
```
