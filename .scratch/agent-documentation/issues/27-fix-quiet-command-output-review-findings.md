# Fix code-review findings on the quiet-command-output hook

Status: resolved
Type: task

## Answer
Fixed the problems found when reviewing ticket 25 against its spec:

- `uninstall` now removes the entry the installer wrote whatever its matcher is, so
  a changed matcher no longer leaves a settings entry pointing at a deleted script.
- The installer recognises its own entry by exact command, not by a substring of
  the script name, so `uninstall` no longer removes a user's unrelated hook that
  merely mentions `quiet-command-output.py`.
- The interactive check in the hook matches whole words (`--interactive`, `-i`,
  `--watch`, `watch`, `login`) instead of substrings, so `pytest tests/test_login.py`
  is wrapped again. `pip install -i <index>` is still skipped, on purpose.
- A command killed by a signal now returns `128 + signal` instead of a negative
  code, so the exit code is kept.
- The docs page no longer hard-codes `/usr/bin/python3` in the permission rule; it
  says to use the path from `which python3`, and lists the interactive words.
- Added the missing tests: `test/cli.test.js` (install twice, uninstall with a
  changed matcher and a foreign hook, in a throwaway HOME) and
  `test/eligible_test.py`. Run both with `npm test`.

Not changed: the extra `package.json` fields (`bin` is needed for `npx`; the rest
are harmless metadata), and `status` output, which already prints script and config
separately. Still not tested inside a live Claude Code session.

## Comments
