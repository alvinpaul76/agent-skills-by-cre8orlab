---
name: infisical-docker-agent
description: Add or debug an Infisical agent sidecar in a Docker Compose stack so containers start with their secrets after a server reboot, with no `infisical run` and no Infisical CLI on the host. Use when the user wants Compose services to pull secrets from Infisical on boot, asks about surviving reboots with Infisical, wants to remove `infisical run` from startup, or when an infisical-agent container, rendered env file, or post-reboot start is failing.
---

# Infisical agent sidecar for Docker Compose

Pattern: an `infisical-agent` container authenticates with Universal Auth, renders secrets into a shared volume, and the other services wait for it (`service_healthy`) and read the rendered file at start. Plain `docker compose up -d` plus Docker's restart policy then survives reboots. Reference implementation: the datamancer-by-cre8orlab repo. Copy-ready files are in `references/`.

## Steps

1. **Files** (adapt from `references/`):
   - `infisical-agent` service in `docker-compose.yml` (`references/compose-agent.yml`)
   - `infisical/agent-config.yaml` (set `address`)
   - `infisical/templates/<app>.tpl` (set project ID, env, path, allowed keys; keep the `# render-complete` last line)
   - `.env.agent.example`; add `.env.agent` to `.gitignore`
2. **Shared volume** `shared_secrets` mounted rw in the agent, `:ro` in consumers. Host dir must be root-restricted; it holds live credentials.
3. **Consumers**: wrap the entrypoint (`references/compose-consumer.yml`): wait for the file, export only the keys needed, check they are non-empty, then `exec` the original entrypoint. Add `depends_on: infisical-agent: condition: service_healthy`.
4. **Restart policy**: `restart: unless-stopped` on every service including the agent.
5. **Host boot path**: `systemctl is-enabled docker` must be `enabled`. Any external network (`external: true`) must be created by something that also starts on boot.
6. **Machine identity**: Universal Auth, read-only, scoped to one project/env/path. Its client ID/secret in `.env.agent` are the only secret left on disk: `chmod 600`, never commit.

## Verify (the real test is a reboot)

```bash
docker compose up -d && docker compose ps      # all healthy
docker compose logs --since=5m infisical-agent  # auth ok, template rendered
sudo reboot
# after boot, no manual commands:
docker compose ps                               # all Up/healthy
docker compose logs --since=10m infisical-agent
```

## Gotchas

- **Healthcheck = real readiness.** Agent healthy only when `.agent-token` is non-empty AND the rendered file contains the `# render-complete` marker. A bare "file exists" passes on partial renders.
- **Universal Auth needs file paths, not values.** The agent config takes `client-id`/`client-secret` as paths. Write the env values to a tmpfs (`/run/infisical-auth`, mode 0700, umask 077) in the container command, then unset the vars before `exec`.
- **`$$` escaping.** In Compose `command`/`healthcheck`, shell variables must be `$$VAR`, else Compose interpolates them at parse time.
- **Pin the image.** Use `infisical/cli:<version>`, not `:latest`, so a reboot/pull doesn't change agent behavior.
- **Compose-time vars can't come from Infisical.** Things Compose resolves before containers start (host port mappings, volume paths) must also live in local `.env`; keep in sync.
- **`env_file:` is a weaker alternative.** It breaks on special characters and when the file doesn't exist yet; prefer the entrypoint wrapper.
- **Secret changes need a consumer restart.** The agent re-renders, but consumers read only at start: `docker compose restart <svc>`. Don't add agent `execute.command` hooks; they need Docker socket access.
- **Stateful images** only read init vars on first run (e.g. Postgres); changing a secret later won't change an existing DB password.
