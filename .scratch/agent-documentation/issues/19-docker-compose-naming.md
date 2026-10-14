# Standardize compose file names to docker-compose*.yml

Status: resolved
Type: task

## Answer
The `fastapi-docker` skill now names the base file `docker-compose.yml`, prefixes
every additional compose file with `docker-compose.` (for example
`docker-compose.override.yml`), and uses `.yml` — never `.yaml`. The compose and
Dockerfile references, the `.dockerignore` example, and the skill's docs page were
updated to match.

## Comments
