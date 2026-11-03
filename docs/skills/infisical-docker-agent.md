# infisical-docker-agent

Adds an Infisical agent container to a Docker Compose stack so services start with
their secrets after a server reboot, without `infisical run` or the Infisical CLI
on the host.

New to a word? See the [word list](../glossary.md). · skill folder:
[`infisical-docker-agent/`](../../skills/infisical-docker-agent/)

## When does the agent use it?

When you want Compose services to pull secrets from Infisical on boot, ask how to
survive reboots with Infisical, want to remove `infisical run` from startup, or when
an `infisical-agent` container, its rendered env file, or a post-reboot start is
failing.

## What is inside?

| File | What it holds |
| --- | --- |
| `SKILL.md` | The pattern, setup steps, the reboot and offline-fallback tests, and common gotchas |
| `references/compose-agent.yml` | The `infisical-agent` service, with its healthcheck |
| `references/compose-consumer.yml` | A service that waits for the secrets file, then starts |
| `references/agent-config.example.yaml` | Agent settings: Infisical address, login method, output file |
| `references/app.example.tpl` | Template that picks which secrets to write, ending in a `# render-complete` line |
| `references/.env.agent.example` | Example of the agent's own login credentials file |

## How does it work inside?

1. The agent container logs in to Infisical with a machine identity (Universal Auth)
   and writes the chosen secrets to a shared volume.
2. Other services wait until the agent reports healthy, read the file at start, and
   keep only the keys they need.
3. Docker's restart policy plus `docker compose up -d` then brings everything back
   after a reboot with no manual commands.
4. The skill's real test is a reboot: check that all services are up and healthy
   afterwards.
5. The shared volume is a plain Docker-managed volume (no host folder, setup script
   or fixed `name:`), so each Compose project gets its own. It keeps the last
   rendered file, so services can still start if Infisical is down. A second test
   checks this offline fallback.
6. Each Compose project with secrets gets its own agent, machine identity and
   `.env.agent`. The agent has no `container_name`, so two projects never clash.
7. Only the `*.example` config files are committed. The real `agent-config.yaml`,
   `<app>.tpl`, `.env.agent` and `.infisical.yaml` hold deployment-specific values
   and are gitignored.
8. The skill also updates the repo's README or docs: prerequisites, the copy step,
   restart after a secret change, and troubleshooting.

## What it deliberately avoids

- Pointing at `:latest` for the agent image; the version is pinned in the compose `.env`
  as `INFISICAL_CLI_IMAGE=infisical/cli:<version>`. Fill in the version; Compose fails
  if it is unset.
- Agent `execute.command` hooks, which need Docker socket access.
- A tmpfs or host bind mount for the shared secrets; either loses the offline fallback
  or needs extra host setup.
- A fixed `container_name` or volume `name:`; both are global on the host and break a
  second project.
- A shared host-wide agent, unless you ask for one.
- Putting variables Compose reads before containers start (port mappings, volume
  paths) only in Infisical; those must also be in the local `.env`.

Related: container standards are in [fastapi-docker](fastapi-docker.md).

Back to [how skills work](../how-skills-work.md).
