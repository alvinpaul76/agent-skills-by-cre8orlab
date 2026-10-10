# Installing skills

How to make a skill from this repository available to your coding agent.

New to a word? See the [word list](glossary.md).

## In plain words

An agent discovers skills by scanning specific folders on your machine or in your
project. Installing a skill means putting its folder in one of those places, either
as a copy or as a link back to this repository.

## How do I install a skill?

1. Clone the repository if you have not already:

   ```bash
   git clone https://github.com/alvinpaul76/agent-skills-by-cre8orlab.git
   cd agent-skills-by-cre8orlab
   ```

2. Pick a location from the table below. Use a **project** location to share the
   skill with your team through git, or a **global** location to use it in every
   project on your machine.

3. Copy or symlink the skill folder into that location:

   ```bash
   # Symlink: edits in the repo take effect immediately (recommended)
   ln -s "$(pwd)/fastapi-standards" ~/.agents/skills/fastapi-standards

   # Or copy: a frozen snapshot that will not change with the repo
   cp -r fastapi-standards ~/.agents/skills/fastapi-standards
   ```

4. Restart the agent or start a new session if it does not pick up the new skill on
   its own.

## Where does each agent look?

| Agent | Project-level (shared via git) | Global (all your projects) |
| --- | --- | --- |
| Devin CLI | `.devin/skills/`, `.agents/skills/`, or `.windsurf/skills/` | `~/.config/devin/skills/` or `~/.agents/skills/` |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Any agent following the `.agents` standard | `.agents/skills/` | `~/.agents/skills/` |

Each skill lives in a subfolder named after it, so a skill called `fastapi-docker`
goes at `<location>/fastapi-docker/SKILL.md`.

## Copy or symlink?

- **Symlink** when you want the skills to track this repository — `git pull`
  updates every agent at once, and your edits are visible immediately.
- **Copy** when you want a stable snapshot, or when the agent runs somewhere the
  symlink target would not exist (for example inside a container).

## How do I check it worked?

1. Start a session in a project where the skill is visible.
2. Ask the agent to list its skills, or look for the skill name in the session's
   skill list.
3. Say a phrase from the skill's description and confirm the agent invokes it.

If the skill does not appear, see [troubleshooting](troubleshooting.md).

## How do I update or remove a skill?

- **Update:** with a symlink, run `git pull` in this repository — nothing else to
  do. With a copy, repeat the `cp -r` command from step 3.
- **Remove:** delete the copied folder or the symlink inside the agent's skills
  directory. Removing a symlink never touches this repository.
