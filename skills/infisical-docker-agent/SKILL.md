---
name: infisical-docker-agent
description: Add or debug an Infisical agent sidecar in a Docker Compose stack so containers start with their secrets after a reboot, without `infisical run` or a host CLI. Use when Compose services should pull secrets from Infisical on boot, `infisical run` should leave startup, or an infisical-agent container, rendered env file or post-reboot start fails.
---

# Infisical agent sidecar for Docker Compose

An `infisical-agent` container logs in with Universal Auth and renders secrets into a shared volume. Consumers wait for it (`service_healthy`) and read the rendered file at start, so `docker compose up -d` plus `restart: unless-stopped` survives reboots. Adapt the files in `references/` and keep their hardening, tmpfs credential paths, `$$` escaping, `umask 077` subshell, `case` guard and `# render-complete` healthcheck.

## Steps

1. **Files**, in the consumer's compose directory (only directories with secrets). Name everything after the app and keep names consistent (`<app>.tpl`, `/shared-secrets/<app>.env`, `template-id: "<app>-env"`).
   - `infisical-agent` service from `references/compose-agent.yml`; `restart: unless-stopped` on every service.
   - `infisical/agent-config.yaml` (`references/agent-config.yaml`) and `infisical/templates/<app>.tpl` (`references/app.tpl`; set the allowed keys). Both are committed with the tokens `__INFISICAL_ADDRESS__`, `__INFISICAL_PROJECT_ID__`, `__INFISICAL_ENV__`, which the agent's startup script `sed`-substitutes from `.env.agent` into tmpfs copies. No deployment-specific value sits in a tracked file. The `case` guard exists because `sed` breaks on `|` and `&`.
   - `.env.agent.example`: placeholders for `INFISICAL_UNIVERSAL_AUTH_CLIENT_ID`, `INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET`, `INFISICAL_ADDRESS`, `INFISICAL_PROJECT_ID`, `INFISICAL_ENV`; header: copy to `.env.agent`, then `chmod 600`.
   - `.env.example`: `INFISICAL_CLI_IMAGE` and each consumer's image variable, per `docker-compose-standards` (a pinned agent means a reboot or pull can't change behavior). Tell the user to add them to `.env`; Compose won't start while they are unset.
   - `.infisical.yaml` from `infisical init`: commit as is (only the host CLI reads it; a project ID is an identifier).
2. **One sidecar per compose project**, each with its own machine identity, `.env.agent` and volume. The agent gets no `container_name`: names are global, so a second project fails with "container name already in use". Fix by deleting the line, not by stopping the other project's container (`docker inspect` its `com.docker.compose.project` label to see the owner). Build a shared host agent only if asked: it needs an identity that reads every project, `depends_on` can't span projects, and a shared volume exposes every app's secrets, so it needs per-app host dirs mounted `:ro` and a boot-ordering plan.
3. **Shared volume**: `shared_secrets: {}`, rw in the agent, `:ro` in consumers. Plain Docker-managed: a fixed `name:`, `driver_opts` or bind collides across projects, leaks secrets between apps and makes `down -v` report "Volume belongs to project". Bind-mount only if the user asks for a host path. The volume persists and its last rendered file is the offline fallback, so no tmpfs and no casual `down -v`.
4. **Consumers** (`references/compose-consumer.yml`): wrap the entrypoint to wait for the file, export only the needed keys, `test -n` each, then `exec` the original entrypoint; add `depends_on: infisical-agent: condition: service_healthy`.
   - The image needs `/bin/sh` (`docker image inspect <image> --format '{{.Config.Entrypoint}}'`). For scratch/distroless, pin a variant that has one (e.g. `<version>-alpine`) in the image variable.
   - The wrapper replaces the image's entrypoint and command, so `exec` the full original command (for a `fastapi-docker` image, the uvicorn line from its `CMD`). Any other service that reads a migrated secret, such as a `migrate` service, needs the same wrapper.
   - Secrets keep their Infisical names; if the app expects others, export mapped names after the check (`export API_KEY="$$MYAPP_API_KEY"`).
   - Remove migrated vars from `environment:`; non-secret vars stay. Compose-time vars (host ports, volume paths) can't come from Infisical and stay in `.env`.
   - The wrapper replaces `env_file:`, which breaks on special characters and when the file doesn't exist yet. Agent `execute.command` hooks need the Docker socket, so leave them out.
5. **Host boot**: `systemctl is-enabled docker` says `enabled`; any `external: true` network is created by something that also runs on boot.
6. **Gitignore** `.env.agent` only, scoped to the compose dir in multi-compose repos. `git check-ignore -v` must not match `.env.agent.example`, the agent config, the template or `.infisical.yaml` (`.env*` patterns need `!.env.agent.example`). If `.env.agent` was ever committed: `git rm --cached` it and rotate the secret.
7. **Docs**, in the same change, if the repo has a README or `docs/`: one setup page, linked from the rest, covering
   - prerequisites: an Infisical project and a read-only Universal Auth identity scoped to one project/env/path (its credentials in `.env.agent` are the only secret left on disk)
   - setup: copy `.env.agent.example` to `.env.agent` (`chmod 600`), with a table of what to fill in
   - migrated secrets: placeholder lines stay in `.env.example`, marked `# Moved to Infisical but kept for debugging purposes`; remove them from prose docs and `grep -rn` the names for leftovers
   - operations: `docker compose restart <svc>` after a secret change (consumers read only at start), offline fallback, `down -v` warning
   - troubleshooting: `docker compose logs infisical-agent`; login error = client ID/secret; 404 or missing key = placeholder values in `.env.agent` or a wrong secret name, project ID or env slug; plus the errors named in steps 1–2

## Verify

The real test is a reboot:

```bash
docker compose up -d && docker compose ps       # all healthy
docker compose logs --since=5m infisical-agent  # auth ok, template rendered
sudo reboot                                     # after boot, no manual commands:
docker compose ps && docker compose logs --since=10m infisical-agent
```

Offline fallback: with the stack healthy, `docker compose stop`, break `INFISICAL_ADDRESS` in `.env.agent`, `docker compose up -d`. Consumers start from the stale file. If the agent truncates the file or token when Infisical is unreachable, the healthcheck fails; fix before relying on it.

Stateful images (e.g. Postgres) read init vars only on first run; changing a secret later won't change an existing DB password.
