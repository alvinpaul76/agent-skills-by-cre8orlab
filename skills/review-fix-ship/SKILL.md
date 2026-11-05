---
name: review-fix-ship
description: Review the current changes, fix problems found, update documentation, then commit and push. Use whenever the user says things like "review again, fix, update docs, commit and push", "ship it", "wrap this up", "review/fix/document/push", or asks to finish up and push recent work, even if they only name some of those steps.
---

# Review, fix, document, commit, push

The user repeats this closing routine at the end of a piece of work. Run it end to end without asking at each step. They have asked for the push by invoking this skill.

## 1. Review

Review what changed, not the whole repo: `git status`, `git diff HEAD` (plus the last commit if the work is already committed but unpushed, `git log @{u}..`).

Look past the edited lines to what depends on them. A change to a config format, variable, path or function usually breaks something that reads it: helper scripts, docs, CI, systemd units, examples. Grep for every renamed or reshaped thing; a shell script that can't parse a new `${VAR:-default}` in a compose file is the typical miss.

Also check: duplicated keys, leftover debug code, secrets or real credentials in tracked files, and `.env.example` declaring every variable `.env` and the compose files use (for Compose changes, the `docker-compose-standards` rules).

Verify rather than assume: run the project's validation (e.g. `docker compose config -q`, `bash -n`, tests, linters) and exercise changed logic in isolation when it can't be run for real (e.g. sourcing a single function).

## 2. Fix
Fix what the review found, minimally and within scope. Stop and ask only if a fix would change intended behavior, needs a design choice between options, deletes or rewrites significant code, or falls outside the scope of the work. Otherwise fix it and note it in the report. Mention anything you left alone.

## 3. Update documentation

Follow the repo's own rules first (`AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`): required changelog or ticket entries, doc pages and checks are part of this step. Then update README and any other docs describing what changed: new or renamed variables, defaults, required vs optional settings, setup steps, troubleshooting entries. Make examples match `.env.example` and the code. Don't add docs for things that didn't change.

## 4. Commit

- Stage specific files by name; never `git add -A` (avoids committing `.env` or scratch files).
- Several logical changes can be several commits, but one is fine for a small change.
- Imperative subject line, short body explaining why.
- Add the co-author trailer given in the session's attribution reminder.
- If on the default branch, branch first.

## 5. Push

`git push origin <current-branch>`, then confirm with `git status -sb` that the branch is in sync. Don't force-push. Don't open a PR or merge unless asked (the `pr` skill covers PR bodies).

## Report

End with a short summary: what the review found, what was fixed, which docs changed, commit hashes, and that the push succeeded. State plainly anything that failed or was skipped.
