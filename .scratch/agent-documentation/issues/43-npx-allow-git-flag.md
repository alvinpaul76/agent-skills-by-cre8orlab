# Hook install command fails on npm 12 (EALLOWGIT)

Status: resolved
Type: bug

## Answer
npm 12 defaults `allow-git=none`, so `npx github:alvinpaul76/agent-skills-by-cre8orlab install <hook>` failed with `EALLOWGIT`. The command now includes `--allow-git=all` in the README, the three hook pages under `docs/hooks/`, and the usage text in `bin/cli.js`. `docs/troubleshooting.md` has a new section explaining the error and the clone-based alternative (`node bin/cli.js install <hook>`).
