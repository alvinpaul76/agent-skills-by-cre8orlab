# Infisical agent skill: commit config with tokens, gitignore only .env.agent

Status: resolved
Type: task

## Answer
Agent config and template are now committed with `__INFISICAL_ADDRESS__`, `__INFISICAL_PROJECT_ID__`, `__INFISICAL_ENV__` tokens (replacing the `*.example` copies). The agent's startup script validates the values with a `case` guard and `sed`-substitutes them from `.env.agent` into tmpfs copies. `.env.agent.example` gained the three values (it was missing them, so the agent would have failed to start). `compose-agent.yml` requires `INFISICAL_CLI_IMAGE` with a clear error. `SKILL.md` and `docs/skills/infisical-docker-agent.md` updated; only `.env.agent` is gitignored and `.infisical.yaml` is committed.
