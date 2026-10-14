# Move skills into a skills folder

Status: resolved
Type: task

Skills sat at the top of the repo while plugins lived under `plugins/`. Group the
skills the same way, and tell people who already installed them how to update.

## Answer
Moved the five skill folders (`fastapi-standards`, `fastapi-docker`,
`fastapi-documentation`, `agent-documentation`, `context-audit`) into `skills/`
with `git mv`, so history follows. The skills' contents did not change. The docs
checker finds skills with a recursive search, so it needed no change and reports
0 errors and 0 warnings.

Updated the links and paths that pointed at the old locations: the "skill folder"
link on each `docs/skills/*.md` page, the page template in
`skills/agent-documentation/references/templates.md`, the repo tree in
`docs/how-skills-work.md`, the new-skill steps in `docs/creating-a-skill.md`, and
the install command in `skills/context-audit/README.md`.

Documented the change for people who already installed: `docs/installation.md` has
a new "Updating an existing install" section covering symlink installs (the links
now point at a folder that no longer exists, so recreate them with `ln -sfn`) and
copy installs (delete and copy again). The install steps there now use the
`skills/` path. `README.md` links to that section, and `docs/troubleshooting.md`
mentions it under "The agent does not see my skill". The `voice-notify` plugin did
not move.

Documented the `npx skills` route: `docs/installation.md` has a new "Install with
npx" section (list, install globally or per project, update, remove, and installing
from a branch) and the README "Get started" leads with it. Tested with the `skills`
CLI (1.7.2) in a throwaway home folder: the tool finds all five skills in
`skills/` on the `develop` branch; `npx skills update -g` works from an unrelated
folder; removing and re-adding a skill records the new `skills/<name>/SKILL.md`
path. Not tested: updating an install made before the move, because that needs the
move on `main`, the branch the tool reads. The docs give a reinstall fallback.

## Comments
