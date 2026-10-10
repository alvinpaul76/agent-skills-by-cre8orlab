# fastapi-docker

Container and deployment standards for FastAPI services: Dockerfiles, compose
files, image security, and vulnerability scanning.

New to a word? See the [word list](../glossary.md). · skill folder:
[`fastapi-docker/`](../../fastapi-docker/)

## When does the agent use it?

Whenever you write, review, or debug a Dockerfile, `.dockerignore`, or
docker-compose file for a FastAPI or Python API — or ask to containerize an app,
run it with Postgres in Docker, harden an image, or find out why a container
exits or fails health checks. It also triggers when you ask to "deploy this" or
"put this in a container", even without the word Docker.

## What is inside?

| File | What it holds |
| --- | --- |
| `SKILL.md` | Base-image choices, non-negotiable rules, hardening checklist |
| `references/dockerfile.md` | A production multi-stage Dockerfile, `.dockerignore`, BuildKit secrets, healthcheck |
| `references/compose.md` | Compose file with app, migrate, and Postgres services; dev override; `.env` pitfalls |
| `references/security-scanning.md` | Scanning the built image, triaging findings by source, CI gating |

## How does it work inside?

1. The agent starts from the production Dockerfile pattern: multi-stage build,
   locked dependencies, a fixed non-root user, and no pip in the runtime stage.
2. It applies the hardening checklist to every production service and checks
   compose for healthchecks, network exposure, and secret handling.
3. For a review it scans the built image rather than guessing at
   vulnerabilities from the Dockerfile text, then reports findings by severity
   and says what is already correct.
4. Vulnerability findings are triaged by source — base OS package, your lock
   file, or pip's vendored libraries — because each has a different fix.

## What it deliberately avoids

- Covering code structure, routes, or business logic — that is
  [fastapi-standards](fastapi-standards.md)' job.
- Blocking builds on findings nobody can fix; unfixed vulnerabilities are
  reported separately from the gate.
- Tags like `latest` in anything meant for production; base images are pinned.

Back to [how skills work](../how-skills-work.md).
