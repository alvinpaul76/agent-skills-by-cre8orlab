# Compose reference

Image pinning, file names and `.env.example` rules come from `docker-compose-standards`.

## Base file: `docker-compose.yml`

Production-like topology: no bind mounts or `--reload`, so it is a realistic test of the built image.

```yaml
name: myapi

x-app-hardening: &app-hardening
  read_only: true
  tmpfs:
    - /tmp
  cap_drop:
    - ALL
  security_opt:
    - no-new-privileges:true

services:
  db:
    image: ${POSTGRES_IMAGE:?POSTGRES_IMAGE is required}   # e.g. postgres:18.6-trixie in .env.example
    restart: unless-stopped
    environment:
      POSTGRES_DB: myapi
      POSTGRES_USER: myapi
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - db-data:/var/lib/postgresql   # Postgres 18+ path; not /var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U myapi -d myapi"]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 5s
    networks:
      - backend
    ports:
      - "127.0.0.1:5432:5432"   # local tools only; remove if not needed
    deploy:
      resources:
        limits:
          memory: 512M

  migrate:
    build:
      context: .
      target: runtime
    image: myapi:local
    <<: *app-hardening
    command: ["alembic", "upgrade", "head"]
    restart: "no"
    env_file:
      - .env
    environment:
      DATABASE_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    depends_on:
      db:
        condition: service_healthy
    networks:
      - backend
    deploy:
      resources:
        limits:
          memory: 256M

  api:
    build:
      context: .
      target: runtime
    image: myapi:local
    <<: *app-hardening
    restart: unless-stopped
    env_file:
      - .env
    environment:
      DATABASE_PASSWORD_FILE: /run/secrets/db_password
      FORWARDED_ALLOW_IPS: "172.16.0.0/12"   # the proxy's network, not the internet
    secrets:
      - db_password
    depends_on:
      db:
        condition: service_healthy
      migrate:
        condition: service_completed_successfully
    networks:
      - backend
      - edge
    ports:
      - "127.0.0.1:8000:8000"   # host only
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "1.0"

secrets:
  db_password:
    file: ./secrets/db_password.txt   # git-ignored; contains only the password

volumes:
  db-data:

networks:
  backend:
    internal: true    # no outbound internet for the database
  edge:
```

Why it is shaped this way:

- Plain `depends_on` only waits for a container to start. `service_healthy` waits for Postgres to accept connections, and `service_completed_successfully` keeps the API down if migrations fail.
- `migrate` and `api` share one local image tag, so it builds once. In CI, tag with the git commit.
- The app reads the password from `DATABASE_PASSWORD_FILE` and builds the connection string itself (in the settings object, per `fastapi-standards`). Environment variables leak through `docker inspect` and crash dumps; files under `/run/secrets/` don't.
- Create the secret once, and add `secrets/` to `.gitignore` and `.dockerignore`:
  `mkdir -p secrets && printf '%s' "$(openssl rand -base64 24)" > secrets/db_password.txt && chmod 600 secrets/db_password.txt`
- `.env` holds only non-secret settings; passwords and tokens stay in `secrets/` even locally.

## Dev override: `docker-compose.override.yml`

Loaded automatically by `docker compose up`; never used in staging or production. It reuses the runtime stage, so dev keeps the non-root user, `read_only`, `cap_drop` and the healthcheck, and problems surface locally.

```yaml
services:
  api:
    command: >
      uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000
      --reload --reload-dir /srv/app
    volumes:
      - ./app:/srv/app:ro   # replaces the image's code; the container never writes to it
    environment:
      APP_ENV: development
```

If a path must be writable, add a `tmpfs` or named volume for it rather than disabling `read_only`.

## Hardening options

| Option | Prevents |
|---|---|
| `read_only: true` | Writing malware or modifying code inside the container |
| `cap_drop: [ALL]` | Raw sockets, mounts and other capabilities the app never needs |
| `no-new-privileges:true` | Privilege escalation through setuid binaries |
| `internal: true` network | Outbound connections from internal services |
| `127.0.0.1:` port prefix | Publishing to all interfaces, which bypasses most host firewalls |
| `deploy.resources.limits` | A runaway process starving the host |
| `restart: "no"` on migrate | Re-running a partially applied migration after a failure |

## Common failures

- **"relation does not exist" on start:** migrations didn't run. Check `docker compose logs migrate` and that `api` waits on it with `service_completed_successfully`.
- **"connection refused" on first start:** `db` lacks a healthcheck or `api` doesn't use `service_healthy`.
- **Unhealthy but serving traffic:** wrong healthcheck port or path, or `start-period` shorter than startup. `docker inspect --format '{{json .State.Health}}' <container>`.
- **Permission denied writing a file:** the root filesystem is read-only; add a `tmpfs` or volume for that path.
- **Client IP is always the proxy:** `FORWARDED_ALLOW_IPS` doesn't include the proxy's network.
- **Port 5432 reachable from another machine:** the mapping lacks `127.0.0.1:`. Fix it and recreate the container.
- **Postgres 18 won't start on an old volume:** a volume from 16 (or one mounted at `/var/lib/postgresql/data`) needs migrating. Back it up, then `pg_dumpall` from the old container and restore into the new one, or run `pg_upgrade` in a one-off container with both versions' binaries. For a throwaway local database, `docker compose down -v`.
