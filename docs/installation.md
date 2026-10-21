# Installing skills

How to make a skill from this repository available to your coding agent.

New to a word? See the [word list](glossary.md).

## In plain words

An agent discovers skills by scanning specific folders on your machine or in your
project. Installing a skill means putting its folder in one of those places, either
as a copy or as a link back to this repository.

## Install with npx (no clone needed)

The `skills` command-line tool installs a skill straight from GitHub and records
where it came from, so you can update it later with one command. It needs
[Node.js](https://nodejs.org) but nothing else.

```bash
# See what is available
npx skills add alvinpaul76/agent-skills-by-cre8orlab --list

# Install one skill for every project on your machine (-g = global)
npx skills add alvinpaul76/agent-skills-by-cre8orlab -g --skill fastapi-standards

# Install it into the current project only (leave out -g)
npx skills add alvinpaul76/agent-skills-by-cre8orlab --skill fastapi-standards
```

Use `-a claude-code` to pick one agent, or leave it out to let the tool detect the
agents you have. See what is installed with `npx skills list -g` (or without `-g` for
the current project).

**Update:** `npx skills update -g` checks every global skill against GitHub and
refreshes the ones that changed. A global update works the same from any folder, so
you do not need to `cd` anywhere first. Always pass `-g` for global skills: without
it the tool asks which scope you mean (or, with `-y`, picks project skills when
you are inside a project folder), and project skills are looked up relative to the
folder you are in.

**Remove:** `npx skills remove -g fastapi-standards`.

The tool reads the repository's default branch. To try a branch before it is merged,
add `#branch-name` to the source, for example
`alvinpaul76/agent-skills-by-cre8orlab#develop`.

## How do I install a skill by hand?

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

## Rules files (AGENTS.md and CLAUDE.md)

Skills load on demand. Rules files are the opposite: always-on instructions the
agent reads at the start of every session. The `AGENTS.md` and `CLAUDE.md` at the
root of this repository are written to be reused — copy them into a project, or
into your agent's global config to apply them everywhere.

**Per project** — copy the files to the project root:

```bash
cp AGENTS.md /path/to/project/AGENTS.md
cp CLAUDE.md /path/to/project/CLAUDE.md
```

Claude Code reads `CLAUDE.md`. Its first line (`@AGENTS.md`) makes it load
`AGENTS.md`, so copy both files and you only ever edit `AGENTS.md`.

**Global (every project)** — one file per agent:

| Agent | Global rules file |
| --- | --- |
| Devin CLI | `~/.config/devin/AGENTS.md` (`%APPDATA%\devin\AGENTS.md` on Windows) |
| Claude Code | `~/.claude/CLAUDE.md` (Devin CLI reads this too) |

One caveat before copying: this repo's `AGENTS.md` has two halves. Section 1
(behavioral guidelines) is generic and safe to reuse anywhere. Section 2 (issue
tracker, triage labels, domain docs) is specific to this repository — leave it
out, or replace it with rules for the project you are copying into.

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

**You installed with `npx skills`.** The tool remembers each skill's old path inside
the repository. Once the move reaches the default branch, run:

```bash
npx skills update -g
```

If it says everything is up to date but you want to be sure, or a skill stops
loading, reinstall it. This always works, because the tool searches the `skills/`
folder:

```bash
npx skills remove -g fastapi-standards
npx skills add alvinpaul76/agent-skills-by-cre8orlab -g --skill fastapi-standards
```

**You installed by hand.** First pull the new layout:

```bash
cd agent-skills-by-cre8orlab
git pull
```

Then follow the case that matches how you copied it.

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
