# Add image vulnerability scanning guidance to fastapi-docker

Status: resolved
Type: task

## Answer
Added `fastapi-docker/references/security-scanning.md` (scan the built image, triage
findings by source, gate CI on fixable HIGH/CRITICAL) and updated the Dockerfile
reference to remove pip from the runtime stage and apply OS patches on digest-pinned
base images.

## Comments
