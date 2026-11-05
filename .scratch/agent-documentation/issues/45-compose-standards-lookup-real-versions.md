# docker-compose-standards: look up real versions instead of inventing them

Status: resolved
Type: bug

## Answer
The skill could suggest made-up versions like `0.x.y`. Added rule 6: when suggesting, adding or pinning a version (including examples), look up the current stable release first, use that exact `major.minor.patch`, and say which was found. "Latest" only selects the version to pin, never a floating tag. Docs page updated.
