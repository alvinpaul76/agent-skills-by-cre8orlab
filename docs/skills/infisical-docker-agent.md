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
| `SKILL.md` | The pattern, setup steps, the reboot test, and common gotchas |
| `references/compose-agent.yml` | The `infisical-agent` service, with its healthcheck |
| `references/compose-consumer.yml` | A service that waits for the secrets file, then starts |
| `references/agent-config.yaml` | Agent settings: Infisical address, login method, output file |
| `references/app.tpl` | Template that picks which secrets to write, ending in a `# render-complete` line |
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

## What it deliberately avoids

- Pointing at `:latest` for the agent image; the version is pinned.
- Agent `execute.command` hooks, which need Docker socket access.
- Putting variables Compose reads before containers start (port mappings, volume
  paths) only in Infisical; those must also be in the local `.env`.

Related: container standards are in [fastapi-docker](fastapi-docker.md).

Back to [how skills work](../how-skills-work.md).
