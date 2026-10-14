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

3. Copy or symlink the skill folder from the repo's `skills/` directory into that
   location:

   ```bash
   # Symlink: edits in the repo take effect immediately (recommended)
   ln -s "$(pwd)/skills/fastapi-standards" ~/.agents/skills/fastapi-standards

   # Or copy: a frozen snapshot that will not change with the repo
   cp -r skills/fastapi-standards ~/.agents/skills/fastapi-standards
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

## Updating an existing install

All skills moved from the top of the repository into a `skills/` folder, the same
way plugins live in `plugins/`. The skills themselves did not change.

First pull the new layout:

```bash
cd agent-skills-by-cre8orlab
git pull
```

Then follow the case that matches how you installed.

**You installed with a symlink.** The link still points at the old folder, which no
longer exists, so the skill has quietly stopped loading. Recreate each link. This
example uses `~/.claude/skills`; swap in your own skills directory:

```bash
for s in fastapi-standards fastapi-docker fastapi-documentation agent-documentation context-audit; do
  ln -sfn "$(pwd)/skills/$s" ~/.claude/skills/$s
done
```

`-sfn` replaces the old link in place. Skip any skill you never installed.

**You installed with a copy.** Nothing broke, but the copy does not change when the
repository does. To refresh it, delete the old copy and copy again from the new
location:

```bash
rm -rf ~/.claude/skills/fastapi-standards
cp -r skills/fastapi-standards ~/.claude/skills/fastapi-standards
```

**Check it worked.** List the link and confirm it points into `skills/`:

```bash
ls -l ~/.claude/skills
```

Then start a new session and confirm the skill shows up (see
[how do I check it worked](#how-do-i-check-it-worked)). The
[voice-notify](plugins/voice-notify.md) plugin did not move, so it needs no change.
