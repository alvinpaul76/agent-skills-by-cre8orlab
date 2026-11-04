# review-fix-ship

Runs the usual closing routine for a piece of work in one go: review the changes,
fix problems, update the docs, commit, and push.

New to a word? See the [word list](../glossary.md). · skill folder:
[`review-fix-ship/`](../../skills/review-fix-ship/)

## When does the agent use it?

When you say things like "review again, fix, update docs, commit and push", "ship
it", or "wrap this up", even if you only name some of those steps. You can also
call it directly with `/review-fix-ship`.

## What does it do?

1. **Review** the current changes and anything that depends on them (renamed
   settings, scripts, docs, examples), then run the project's checks.
2. **Fix** what the review found, in scope. It stops and asks only if a fix changes
   intended behavior or needs a design choice.
3. **Update documentation** for what changed.
4. **Commit** with specific files staged by name (never `git add -A`).
5. **Push** the current branch. No force-push, no pull request unless you ask.

It ends with a short report: findings, fixes, docs changed, commit hashes, and
whether the push worked.

## Does it change anything?

Yes. It edits files, commits, and pushes. Invoking it counts as your request to push.
