# Infisical agent skill: pin image via INFISICAL_CLI_IMAGE

Status: resolved
Type: task

## Answer
`infisical-docker-agent` reference compose now uses `image: ${INFISICAL_CLI_IMAGE}`. `SKILL.md` tells the agent to add `INFISICAL_CLI_IMAGE=infisical/cli:<pin-version>` to the compose `.env` and `.env.example`, and notes Compose fails if unset. Updated `docs/skills/infisical-docker-agent.md` to match.
