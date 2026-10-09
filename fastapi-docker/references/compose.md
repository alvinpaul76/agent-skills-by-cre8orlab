# Docker Compose reference

## Contents

- Base compose file (app, migrate, Postgres)
- Development override
- Environment files and Postgres password handling
- Hardening options and why they matter
- Common failures and what to check

## Base compose file

`compose.yaml` describes the production-like topology. It runs without bind
mounts or `--reload`, so it is a realistic test of the built image.

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
    image: postgres:18.6-trixie   # latest stable release; match the Debian release of the app image; verify the tag on Docker Hub
    restart: unless-stopped
    environment:
      POSTGRES_DB: myapi
      POSTGRES_USER: myapi
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - db-data:/var/lib/postgresql   # PostgreSQL 18+ images expect this path, not /data
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
      FORWARDED_ALLOW_IPS: "172.16.0.0/12"   # the reverse proxy's network, not the internet
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
      - "127.0.0.1:8000:8000"   # reachable from the host only
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
    internal: true    # no outbound internet access for the database
  edge:
```

Points to notice:

- **Migrations run as their own service.** `migrate` exits when finished, and
  `api` starts only after it reports `service_completed_successfully`. If
  migrations fail, the app does not start. This is the local equivalent of the
  Kubernetes Job described in `SKILL.md`.
- **Postgres has a healthcheck, and the app waits for it.** `depends_on` with
  `condition: service_healthy` avoids the classic race where the app starts
  before the database accepts connections. Note that plain `depends_on` without
  a condition only waits for the container to start, not for the database to
  be ready.
- **Postgres 18 changed the data path.** Official images from 18 onward store
  data in a version-specific subdirectory of `/var/lib/postgresql`, so the
  volume mounts there. Mounting at `/var/lib/postgresql/data`, as in earlier
  guides, makes the container refuse to start or create a second data
  directory.
- **The database is on an internal network.** `internal: true` blocks outbound
  internet access from `backend`, so a compromised container cannot download
  tools or exfiltrate data directly.
- **Published ports are bound to `127.0.0.1`.** Without the prefix, Docker
  publishes to all interfaces and bypasses most host firewalls. This is one of
  the most common local-dev exposure mistakes.
- **Passwords come from a file, not the environment.** Environment variables
  show up in `docker inspect`, process listings, and crash dumps. The secret
  file is mounted at `/run/secrets/` inside the container.
- **`FORWARDED_ALLOW_IPS` is set to the proxy's network**, not `*`. Adjust the
  range to match the real proxy address in each environment.
- **The image tag is a fixed local name**, and both services share it so the
  build happens once. In CI, push a tag derived from the git commit instead.

### Application configuration for the file-based password

The app should read the password from `DATABASE_PASSWORD_FILE` when it is set,
and build the connection string itself. Keep the connection string out of
`.env` files. Example settings logic (adapt to your settings class):

```python
from pathlib import Path
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str = "db"
    db_port: int = 5432
    db_name: str = "myapi"
    db_user: str = "myapi"
    database_password_file: Path | None = Field(default=None, alias="DATABASE_PASSWORD_FILE")
    database_password: str | None = None

    @computed_field
    @property
    def database_url(self) -> str:
        password = (
            self.database_password_file.read_text().strip()
            if self.database_password_file
            else self.database_password or ""
        )
        return f"postgresql+psycopg://{self.db_user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}"
```

Do not log `database_url`. Hide the password from `repr` and logs, for example
by excluding `database_password` from the model's representation with
`Field(default=None, repr=False)`, and never print the computed URL.

## Development override

`compose.override.yaml` is loaded automatically by `docker compose up` on top
of `compose.yaml`. It adds hot reload and source mounts for local work. Do not
use it in staging or production.

```yaml
services:
  api:
    build:
      target: builder          # keeps dev tools available if the builder stage has them
    command: >
      uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000
      --reload --reload-dir /srv/app
    volumes:
      - ./app:/srv/app/app:ro  # read-only source mount; the container never writes to it
    environment:
      APP_ENV: development
```

The override keeps `read_only` enabled. The base file's `tmpfs` on `/tmp`
already provides writable scratch space. Do not remove `cap_drop`, the non-root user, or the healthcheck
because it is "dev": those settings should behave the same locally as in
production, so problems surface early. If a path needs to be writable, add a
`tmpfs` or named volume for that path.


## Environment files

- `.env` holds local, non-secret settings (log level, app name, feature flags)
  and is git-ignored.
- `.env.example` is committed with placeholder values and documents every
  variable the app reads.
- Passwords and tokens belong in `secrets/` files or the platform's secret
  store, not in `.env`, even for local work.

Create the local secret file once:

```bash
mkdir -p secrets && printf '%s' "$(openssl rand -base64 24)" > secrets/db_password.txt
chmod 600 secrets/db_password.txt
```

Add `secrets/` to `.gitignore` and `.dockerignore`.

## Hardening options explained

| Option | What it prevents |
|---|---|
| `read_only: true` | An attacker or bug writing malware or modifying code inside the container. Writable paths are made explicit with `tmpfs`. |
| `cap_drop: [ALL]` | Use of Linux capabilities such as raw sockets or mounting filesystems. The app needs none of them. |
| `no-new-privileges:true` | Setuid binaries or file capabilities escalating privileges inside the container. |
| `internal: true` network | Outbound connections from the database or internal services to the internet. |
| `127.0.0.1:` port binding | Exposure of database or admin ports to the LAN or internet. |
| `mem_limit` / `cpus` | A runaway process starving the host. |
| `restart: "no"` on migrate | Re-running migrations automatically after a failure, which can repeat a partial change. |

## Common failures and what to check

- **API exits immediately with "relation does not exist".** Migrations did not
  run. Check `docker compose logs migrate` and confirm `api` depends on
  `migrate` with `service_completed_successfully`.
- **"connection refused" on first start.** The app started before Postgres was
  ready. Confirm `db` has a healthcheck and `api` uses `condition: service_healthy`.
- **Container reports unhealthy but serves traffic.** The Dockerfile healthcheck
  points at the wrong port or path, or `--start-period` is shorter than startup
  takes. Check `docker inspect --format '{{json .State.Health}}' <container>`.
- **Upgrading an existing Postgres 16 volume.** A volume created with 16 will
  not start on 18 as-is. Either dump and restore (`pg_dumpall` from the old
  container, restore into the new one) or run `pg_upgrade` in a one-off
  container with both versions' binaries. Back up the volume before trying
  either. For a fresh local environment, `docker compose down -v` removes the
  old volume.
- **Permission denied writing a file.** The app is trying to write to the
  read-only root filesystem. Add a `tmpfs` or named volume for that path rather
  than disabling `read_only`.
- **Client IP is always the proxy's address in logs.** `FORWARDED_ALLOW_IPS` does
  not include the proxy's network, so forwarded headers are ignored.
- **Port 5432 reachable from another machine.** The port mapping lacks the
  `127.0.0.1:` prefix. Fix the mapping and recreate the container.
