# Agent Skills by Cre8or Lab

Reusable skills, hooks, plugins, and rules files for coding agents. Each piece is
self-contained, so an agent loads only what a task calls for.

## What is it for?

- Give any coding agent consistent standards for FastAPI work
- Share the same guidance across different agents and projects

## Skills

| Skill | What it does | Docs |
| --- | --- | --- |
| fastapi-standards | Layered-architecture standards for building, reviewing, and refactoring FastAPI services | [fastapi-standards](docs/skills/fastapi-standards.md) |
| fastapi-docker | Container, deployment, and image-scanning standards for FastAPI services | [fastapi-docker](docs/skills/fastapi-docker.md) |
| fastapi-documentation | Writes plain-language docs that non-developers can follow | [fastapi-documentation](docs/skills/fastapi-documentation.md) |
| agent-documentation | Writes plain-language docs for agent skills and plugins | [agent-documentation](docs/skills/agent-documentation.md) |
| docker-compose-standards | Shared Compose rules: file names, pinned images set through variables, a complete `.env.example` | [docker-compose-standards](docs/skills/docker-compose-standards.md) |
| infisical-docker-agent | Infisical agent container for Docker Compose so services get their secrets after a reboot | [infisical-docker-agent](docs/skills/infisical-docker-agent.md) |
| context-audit | Read-only audit of Claude Code token cost: instruction files, MCP tools, model, hooks, subagents, scheduled jobs, and prompt-cache behavior | [context-audit](docs/skills/context-audit.md) |
| review-fix-ship | Closing routine: review changes, fix, update docs, commit, and push | [review-fix-ship](docs/skills/review-fix-ship.md) |

Each skill's folder is under [`skills/`](skills/). Each page explains when the skill
triggers and what is inside it.

## Hooks

| Hook | What it does | Docs |
| --- | --- | --- |
| quiet-command-output | Shrinks noisy install, build, and test output before the agent reads it | [quiet-command-output](docs/hooks/quiet-command-output.md) |
| docs-drift-reminder | Reminds the agent to update docs after code edits; in FastAPI projects it also checks for drift | [docs-drift-reminder](docs/hooks/docs-drift-reminder.md) |
| validate-docker-compose | Checks Compose changes against docker-compose-standards; sends the agent back to fix them | [validate-docker-compose](docs/hooks/validate-docker-compose.md) |

Also shipped: the [voice-notify](docs/plugins/voice-notify.md) plugin and the rules files
[`AGENTS.md`](AGENTS.md) and [`CLAUDE.md`](CLAUDE.md) ([how to use](docs/installation.md#rules-files-agentsmd-and-claudemd)).

## Get started

The quickest way is `npx` (needs Node.js, no clone):

```bash
npx skills add alvinpaul76/agent-skills-by-cre8orlab -g --skill fastapi-standards
npx skills update -g    # later: refresh installed skills, from any folder
```

Hooks install the same way, with the repo's own command:

```bash
npx github:alvinpaul76/agent-skills-by-cre8orlab install quiet-command-output
```

Installing by hand, or upgrading an older install (skills moved into `skills/`)?
See [installing skills](docs/installation.md).

## Docs

- [How skills work](docs/how-skills-work.md): what a skill is and how agents use one
- [Installing skills](docs/installation.md)
- [Creating a skill](docs/creating-a-skill.md)
- [Something not working?](docs/troubleshooting.md)
- [Word list](docs/glossary.md)

## License

Released under the [MIT License](./LICENSE).
