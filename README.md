# Agent Skills by Cre8or Lab

A collection of reusable skills that give coding agents focused engineering guidance, workflows, and reference material.

Each skill is self-contained in its own directory and follows the Agent Skills layout: a `SKILL.md` file with YAML frontmatter and, when needed, a `references/` directory for supporting documentation.

## Available skills

| Skill | Purpose |
| --- | --- |
| [`fastapi-standards`](./fastapi-standards/) | Architecture and engineering standards for building, reviewing, and refactoring maintainable FastAPI services. |
| [`fastapi-docker`](./fastapi-docker/) | Secure, reproducible container and deployment standards for FastAPI services. |

## Installation

Clone the repository:

```bash
git clone https://github.com/cre8orlab/agent-skills-by-cre8orlab.git
cd agent-skills-by-cre8orlab
```

Copy or symlink the skill directories you want into the skills directory used by your agent. For example:

```bash
ln -s "$(pwd)/fastapi-standards" /path/to/your/agent/skills/fastapi-standards
ln -s "$(pwd)/fastapi-docker" /path/to/your/agent/skills/fastapi-docker
```

The exact destination depends on the agent and whether you want the skills available globally or only within one project. Restart or reload the agent after installation if it does not discover new skills automatically.

## Repository structure

```text
.
├── fastapi-docker/
│   ├── SKILL.md
│   └── references/
├── fastapi-standards/
│   ├── SKILL.md
│   └── references/
├── LICENSE
└── README.md
```

## Creating a skill

1. Create a directory named after the skill.
2. Add a `SKILL.md` containing YAML frontmatter with `name` and `description` fields.
3. Write clear instructions that tell an agent when to use the skill and what successful completion looks like.
4. Put detailed, task-specific material in `references/` and link to it from `SKILL.md`.
5. Keep paths relative so the skill remains portable between supported agents.

A minimal skill starts like this:

```markdown
---
name: example-skill
description: Explain what the skill does and the situations that should trigger it.
---

# Example Skill

Describe the workflow, constraints, and expected output.
```

## Contributing

Contributions are welcome. Keep each skill focused, self-contained, and free of secrets or environment-specific paths. When changing a skill, verify that its frontmatter is valid and that every referenced file exists.

## License

Released under the [MIT License](./LICENSE).
