# context-audit lean rewrite; review-fix-ship and fastapi-documentation fixes

Status: resolved
Type: task

## Answer
- `context-audit/SKILL.md` (12.9 KB to 7.2 KB): repeated UNKNOWN, read-only and redaction rules collected into one Evidence rules section; severity definitions merged into the output contract (they contradicted each other on UNKNOWN). Same checks and output.
- `review-fix-ship`: follows the repo's own rules files (tickets, doc pages) during the docs step; `.env.example` check points to `docker-compose-standards`.
- `fastapi-documentation`: removed project-specific examples (`JEV_BACKEND`, ticket analyses, mock backend).
