# Agent Skills by Cre8or Lab

Reusable skills that give coding agents focused engineering guidance, workflows, and
reference material. Each skill is a self-contained folder that an agent loads when a
task calls for it.

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
The repo also ships the [voice-notify](docs/plugins/voice-notify.md) plugin and two
hooks for Claude Code: [quiet-command-output](docs/hooks/quiet-command-output.md) and
[docs-drift-reminder](docs/hooks/docs-drift-reminder.md).

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

Prefer to install by hand (clone, then copy or symlink a folder from `skills/`)? See
[installing skills](docs/installation.md).

Installed an earlier version? Skills now live in `skills/`, so hand-made symlinks
break and `npx` installs may need a reinstall. See
[updating an existing install](docs/installation.md#updating-an-existing-install).

## Docs

- [How skills work](docs/how-skills-work.md): what a skill is and how agents use one
- [Installing skills](docs/installation.md)
- [Creating a skill](docs/creating-a-skill.md)
- [Something not working?](docs/troubleshooting.md)
- [Word list](docs/glossary.md)

## License

Released under the [MIT License](./LICENSE).
