# Infisical agent skill: per-project agent, tighter SKILL.md, placeholder fixes

Status: resolved
Type: task

## Answer
`SKILL.md` rewritten as one ordered setup list: files, one sidecar per compose project (no `container_name`), plain `shared_secrets: {}` volume (no fixed `name:`), consumer wrapper notes (needs `/bin/sh`, name mapping), host boot, gitignore, docs, verify. References now use `<app>` placeholders consistently, the agent has `mem_limit`/`cpus`, the consumer example checks every key, and `.env.agent.example` has a header and `<client id>` placeholders. `docs/skills/infisical-docker-agent.md` updated for per-project agents/volumes, `*.example` + gitignore, the docs step, and the new avoid-list entries.
