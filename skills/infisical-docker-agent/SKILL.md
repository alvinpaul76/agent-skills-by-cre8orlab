---
name: infisical-docker-agent
description: Add or debug an Infisical agent sidecar in a Docker Compose stack so containers start with their secrets after a server reboot, with no `infisical run` and no Infisical CLI on the host. Use when the user wants Compose services to pull secrets from Infisical on boot, asks about surviving reboots with Infisical, wants to remove `infisical run` from startup, or when an infisical-agent container, rendered env file, or post-reboot start is failing.
---

# Infisical agent sidecar for Docker Compose

Pattern: an `infisical-agent` container authenticates with Universal Auth, renders secrets into a shared volume, and the other services wait for it (`service_healthy`) and read the rendered file at start. Plain `docker compose up -d` plus Docker's restart policy then survives reboots. Reference implementation: the datamancer-by-cre8orlab repo. Copy-ready files are in `references/`.

## Steps

1. **Files** (adapt from `references/`):
   - `infisical-agent` service in `docker-compose.yml` (`references/compose-agent.yml`)
   - `infisical/agent-config.example.yaml` (placeholder `address`) and `infisical/templates/<app>.example.tpl` (placeholder project ID, env, path; set allowed keys; keep the `# render-complete` last line). Commit only these `*.example` files. Copy them to `agent-config.yaml` / `<app>.tpl` for the real values and **gitignore the real ones** (see Gotchas).
   - `.env.agent.example`; add `.env.agent` to `.gitignore`
   - If `infisical init` created `.infisical.yaml` (holds the project ID), gitignore it and commit a `.infisical.example.yaml` instead.
   - In the compose-level `.env` and `.env.example`, add the pinned agent image (user fills in the version):
     ```
     # Infisical agent sidecar image (pin a specific infisical/cli version)
     INFISICAL_CLI_IMAGE=infisical/cli:<pin-version>
     ```
2. **Shared volume** `shared_secrets` mounted rw in the agent, `:ro` in consumers. Declare it as a plain Docker-managed named volume (`shared_secrets:\n    name: shared_secrets`, no `driver_opts`/bind). No host dir, no setup script, no chown/chmod; it lives root-only under `/var/lib/docker/volumes` and persists across reboots. The last rendered file is the fallback when Infisical is down, so do NOT use tmpfs and do not use `down -v` casually. Only bind-mount if the user explicitly wants the data at a chosen host path.
3. **Consumers**: wrap the entrypoint (`references/compose-consumer.yml`): wait for the file, export only the keys needed, check they are non-empty, then `exec` the original entrypoint. Add `depends_on: infisical-agent: condition: service_healthy`.
4. **Restart policy**: `restart: unless-stopped` on every service including the agent.
5. **Host boot path**: `systemctl is-enabled docker` must be `enabled`. Any external network (`external: true`) must be created by something that also starts on boot.
6. **Docs**: if the repo has a README or `docs/`, update them in the same change; stale docs that say "put the secret in `.env`" are the usual leftover. Keep the setup steps on one page and link to it from the rest (install, configuration, troubleshooting, FAQ). Cover:
   - the Infisical prerequisites: project holding the secrets, Universal Auth machine identity (read-only, one project/env/path), pinned `INFISICAL_CLI_IMAGE`
   - the copy step: `.env.agent`, `agent-config.yaml`, `<app>.tpl` from their `*.example` files (and `chmod 600 .env.agent`), with a table of what to fill in each, and why the real files are gitignored
   - that the migrated secrets are no longer read from `.env`; remove them from the docs, or say they are unused if left in `.env.example`
   - restart after a secret change (`docker compose restart <svc>`), the offline fallback and the `down -v` warning
   - troubleshooting: `docker compose logs infisical-agent`, login errors (client ID/secret), missing key (secret name/project ID/env slug in the template), unset `INFISICAL_CLI_IMAGE`
   Finish with `grep -rn` for the migrated secret names in the docs to catch leftovers.
7. **Machine identity**: Universal Auth, read-only, scoped to one project/env/path. Its client ID/secret in `.env.agent` are the only secret left on disk: `chmod 600`, never commit.

## Verify (the real test is a reboot)

```bash
docker compose up -d && docker compose ps      # all healthy
docker compose logs --since=5m infisical-agent  # auth ok, template rendered
sudo reboot
# after boot, no manual commands:
docker compose ps                               # all Up/healthy
docker compose logs --since=10m infisical-agent
```

## Verify the offline fallback

The persisted file should let consumers start while Infisical is unreachable:

```bash
docker compose up -d && docker compose ps       # healthy, file rendered
docker compose stop
# make Infisical unreachable (bad `address` in agent-config.yaml, or block host)
docker compose up -d && docker compose ps       # consumers should still start from the stale file
```

If the agent truncates the file or token when it cannot reach Infisical, the healthcheck fails and consumers will not start; fix before relying on it.

## Gotchas

- **Don't commit deployment-specific values.** The Infisical host, project ID and env slug are specific to one deployment. Commit `*.example` files with placeholders and add the real files to `.gitignore`, with an exception so the examples stay tracked:
  ```
  infisical/agent-config.yaml
  infisical/templates/*.tpl
  !infisical/templates/*.example.tpl
  .infisical.yaml
  ```
  Also tell the user to document the copy step (README/docs). Check with `git check-ignore -v` that the examples are not ignored. If the real files were already committed, `git rm --cached` them; history rewrite is usually unnecessary since none are credentials.
- **umask scope.** Apply `umask 077` only in a subshell around the credential files (`( umask 077; printf ... )`). A global umask makes the agent's rendered file root-only 0600 and consumers (non-root) cannot read it.
- **Hardening.** Add `cap_drop: [ALL]`, `no-new-privileges:true`, and memory/cpu limits to the agent.

- **Healthcheck = real readiness.** Agent healthy only when `.agent-token` is non-empty AND the rendered file contains the `# render-complete` marker. A bare "file exists" passes on partial renders.
- **Universal Auth needs file paths, not values.** The agent config takes `client-id`/`client-secret` as paths. Write the env values to a tmpfs (`/run/infisical-auth`, mode 0700, umask 077) in the container command, then unset the vars before `exec`.
- **`$$` escaping.** In Compose `command`/`healthcheck`, shell variables must be `$$VAR`, else Compose interpolates them at parse time.
- **Pin the image.** The agent uses `image: ${INFISICAL_CLI_IMAGE}`, set in `.env` to `infisical/cli:<version>`, never `:latest`, so a reboot/pull doesn't change agent behavior. Compose fails if it is unset or still a placeholder, so tell the user to fill in the version.
- **Compose-time vars can't come from Infisical.** Things Compose resolves before containers start (host port mappings, volume paths) must also live in local `.env`; keep in sync.
- **`env_file:` is a weaker alternative.** It breaks on special characters and when the file doesn't exist yet; prefer the entrypoint wrapper.
- **Secret changes need a consumer restart.** The agent re-renders, but consumers read only at start: `docker compose restart <svc>`. Don't add agent `execute.command` hooks; they need Docker socket access.
- **Stateful images** only read init vars on first run (e.g. Postgres); changing a secret later won't change an existing DB password.
