---
name: infisical-docker-agent
description: Add or debug an Infisical agent sidecar in a Docker Compose stack so containers start with their secrets after a server reboot, with no `infisical run` and no Infisical CLI on the host. Use when the user wants Compose services to pull secrets from Infisical on boot, asks about surviving reboots with Infisical, wants to remove `infisical run` from startup, or when an infisical-agent container, rendered env file, or post-reboot start is failing.
---

# Infisical agent sidecar for Docker Compose

Pattern: an `infisical-agent` container logs in with Universal Auth and renders secrets into a shared volume. Consumers wait for it (`service_healthy`) and read the rendered file at start. `docker compose up -d` plus `restart: unless-stopped` then survives reboots. Copy-ready files are in `references/`; the agent's hardening, tmpfs credential paths, `$$` escaping, subshell `umask 077` and `# render-complete` healthcheck are already in `references/compose-agent.yml`, so keep them when adapting.

## Steps

1. **Files**, in the compose directory that holds the consumer (only directories with secrets; paths below are relative to it). Name things after the app, not `app`, and keep names consistent across compose, agent config and template (`<app>.tpl`, `/shared-secrets/<app>.env`, `template-id: "<app>-env"`).
   - `infisical-agent` service in the consumer's `docker-compose.yml` (`references/compose-agent.yml`), `restart: unless-stopped` on every service.
   - `infisical/agent-config.example.yaml` (placeholder `address`) and `infisical/templates/<app>.example.tpl` (placeholders `<project-id>`, `<env-slug>`, path `/`; set allowed keys; keep the `# render-complete` last line).
   - `.env.agent.example` (placeholders `<client id>` / `<client secret>`; header: copy to `.env.agent`, then `chmod 600`).
   - Compose-level `.env` and `.env.example`: `INFISICAL_CLI_IMAGE=infisical/cli:<pin-version>` with a comment to pin a version (never `:latest`, so a reboot/pull can't change behavior; Compose fails while unset, so tell the user to fill it in).
   - If `infisical init` created `.infisical.yaml`, gitignore it (`git rm --cached` if tracked) and commit `.infisical.example.yaml` (`version: 1`, `general: {}`, `project-id: <project-id>`) at the repo root.
2. **One sidecar per compose project; no fixed names.** Each project with secrets gets its own agent, machine identity and `.env.agent`. Never set `container_name` on the agent: names are global on the host, so a second project fails with "container name already in use" (fix: delete the line; never remove the other project's container; check its `com.docker.compose.project` label with `docker inspect`). Address the agent by service name. A shared host agent is not the default: it needs an identity that reads every project, `depends_on` can't span projects (boot order breaks), and a shared volume exposes every app's secrets. Only build one if asked, with per-app host dirs mounted `:ro` and a boot-ordering plan.
3. **Shared volume** `shared_secrets`: rw in the agent, `:ro` in consumers, declared as `shared_secrets: {}` (plain Docker-managed; no `name:`, `driver_opts` or bind). A fixed global name collides across projects, leaks secrets between apps and makes `down -v` report "Volume belongs to project". It persists across reboots and its last rendered file is the offline fallback, so no tmpfs and no casual `down -v`. Bind-mount only if the user asks for a host path.
4. **Consumers** (`references/compose-consumer.yml`): wrap the entrypoint to wait for the file, export only the needed keys, `test -n` each, then `exec` the original entrypoint; add `depends_on: infisical-agent: condition: service_healthy`.
   - Needs `/bin/sh`: check `docker image inspect <image> --format '{{.Config.Entrypoint}}'`. For scratch/distroless images prefer a tag with a shell (e.g. `:alpine`) set in `.env`/`.env.example`; don't build wrapper images or mount busybox unless asked.
   - Secrets keep their Infisical names; if the app expects others, export mapped names after the check (`export API_KEY="$$MYAPP_API_KEY"`).
   - Remove migrated vars from `environment:`; keep non-secret vars. Compose-time vars (host ports, volume paths) can't come from Infisical and stay in `.env`.
   - Prefer the wrapper over `env_file:` (breaks on special characters and when the file doesn't exist yet). Don't add agent `execute.command` hooks (need Docker socket).
5. **Host boot**: `systemctl is-enabled docker` must say `enabled`; any `external: true` network must be created by something that also runs on boot.
6. **Gitignore** deployment-specific values (Infisical host, project ID, env slug); commit only `*.example` files:
   ```
   .env.agent
   # Deployment-specific Infisical config (copy from the *.example files)
   <dir>/infisical/agent-config.yaml
   <dir>/infisical/templates/*.tpl
   !<dir>/infisical/templates/*.example.tpl
   .infisical.yaml
   ```
   Scope paths to the compose dir in multi-compose repos. Check with `git check-ignore -v` that examples aren't ignored. If real files were committed, `git rm --cached` them (no history rewrite; none are credentials).
7. **Docs**, in the same change, if the repo has a README or `docs/`. Keep setup on one page; link from the rest. Cover:
   - prerequisites: Infisical project, Universal Auth machine identity (read-only, one project/env/path; its client ID/secret in `.env.agent` are the only secret left on disk), pinned `INFISICAL_CLI_IMAGE`
   - the copy step (`.env.agent` with `chmod 600`, `agent-config.yaml`, `<app>.tpl` from `*.example`), a table of what to fill in, and why the real files are gitignored
   - migrated secrets are no longer read from `.env`: keep the placeholder lines in `.env.example` with `# Moved to Infisical but kept for debugging purposes`, remove them from prose docs, then `grep -rn` the secret names to catch leftovers
   - `docker compose restart <svc>` after a secret change (consumers read only at start), offline fallback, `down -v` warning, each stack keeps its own agent
   - troubleshooting: `docker compose logs infisical-agent`; login error (client ID/secret); 404 or missing key (placeholders left in the template, wrong secret name/project ID/env slug); unset `INFISICAL_CLI_IMAGE`; "container name already in use"

## Verify

The real test is a reboot:

```bash
docker compose up -d && docker compose ps       # all healthy
docker compose logs --since=5m infisical-agent  # auth ok, template rendered
sudo reboot                                     # after boot, no manual commands:
docker compose ps && docker compose logs --since=10m infisical-agent
```

Offline fallback: with the stack healthy, `docker compose stop`, break `address` in `agent-config.yaml`, `docker compose up -d`. Consumers should start from the stale file. If the agent truncates the file or token when Infisical is unreachable, the healthcheck fails; fix before relying on it.

Stateful images (e.g. Postgres) read init vars only on first run; changing a secret later won't change an existing DB password.
