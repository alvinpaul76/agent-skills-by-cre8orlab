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
| context-audit | Read-only audit of Claude Code token cost: instruction files, MCP tools, model, hooks, subagents, scheduled jobs, and prompt-cache behavior | [context-audit](docs/skills/context-audit.md) |

Each skill's folder is under [`skills/`](skills/). Each page explains when the skill
triggers and what is inside it.
The repo also ships the [voice-notify](docs/plugins/voice-notify.md) plugin, two
Claude Code hooks ([quiet-command-output](docs/hooks/quiet-command-output.md) and
[docs-drift-reminder](docs/hooks/docs-drift-reminder.md)), and the reusable rules
files [`AGENTS.md`](AGENTS.md) and [`CLAUDE.md`](CLAUDE.md) — copy them per project
or globally; see [rules files](docs/installation.md#rules-files-agentsmd-and-claudemd).

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
