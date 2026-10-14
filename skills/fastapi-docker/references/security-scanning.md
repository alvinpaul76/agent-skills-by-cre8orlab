# Scanning and fixing image vulnerabilities

Scan the built image. A Dockerfile that looks fine can still ship vulnerable
packages from the base image, and the Dockerfile alone cannot show that.

## Scan

```bash
# If trivy is not installed, run it as a container against the local image:
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v trivy-cache:/root/.cache \
  aquasec/trivy:0.75.0 image --scanners vuln,secret,misconfig \
  --severity HIGH,CRITICAL --ignore-unfixed myapi:<tag>
```

Run it twice and keep the two results apart:

1. `--ignore-unfixed`: findings you can fix today. This is the gate.
2. Without `--ignore-unfixed` (use `--format json` and group by package): the
   backlog waiting on upstream. Report it, but do not block on it.

## Find where a finding comes from

The fix depends on the source, so triage before changing anything.

| Where it shows up | Likely source | Fix |
|---|---|---|
| `debian` section, fixed version listed | Base image is older than the patch | `apt-get upgrade` in the runtime stage and rebuild; refresh the base digest |
| `debian` section, no fixed version | Debian has not shipped a fix | Do not block. Rebuild regularly; reduce exposure (non-root, `cap_drop: ALL`, `no-new-privileges`, read-only filesystem) |
| `python-pkg`, package is in `uv.lock` | Your dependency | `uv lock --upgrade-package <name>`, run tests, rebuild |
| `python-pkg`, path under `site-packages/pip/_vendor/` | pip's vendored copy (urllib3, msgpack, setuptools, ...) | Delete pip from the runtime stage |
| `python-pkg`, package not in `uv.lock` and no pip path | A transitive or vendored copy | `docker run --rm --entrypoint sh <image> -c 'find / -xdev -name "<pkg>*"'` to find the path, then decide |

To check where a Python finding lives without guessing:

```bash
grep -n -A1 '^name = "<pkg>"' uv.lock          # in the lock file?
uv tree --invert --package <pkg>               # who pulls it in?
docker run --rm --entrypoint sh <image> -c 'find / -xdev -name "<pkg>*" 2>/dev/null'
```

## Standard fixes

- **Remove pip from the runtime image.** Nothing installs packages at runtime,
  and pip's vendored libraries are the usual source of "unfixable" Python
  findings you did not choose. In the runtime stage:
  `rm -rf /usr/local/lib/python3.*/site-packages/pip* /usr/local/bin/pip*`.
  The venv built in the builder stage is unaffected.
- **Pin base images by digest** and keep a comment on how to refresh it
  (`docker buildx imagetools inspect python:3.14-slim-trixie`). A tag alone lets
  the patch level change between builds, so two builds of the same commit can
  differ.
- **Patch the OS layer**: `apt-get update && apt-get upgrade --yes
  --no-install-recommends && rm -rf /var/lib/apt/lists/*` in the runtime stage,
  in the same `RUN` so the apt lists do not stay in a layer. A digest pin means
  patches since that digest are otherwise missed.
- **Keep builders out of runtime**: no compilers, `uv`, or build tools after
  the final `FROM`.

## CI gating

- Fail the build on HIGH or CRITICAL findings with a fix available
  (`--ignore-unfixed --exit-code 1`).
- Rebuild and rescan on a schedule (weekly is a reasonable default), not only
  on commits. New CVEs appear against images that have not changed.
- Do not suppress findings with an ignore file unless each entry has a reason
  and an expiry date.

## Verify after fixing

1. Rebuild with the project's normal command (for example `docker compose build`).
2. Re-run the scan with `--ignore-unfixed`: expect zero HIGH and CRITICAL.
3. Start the container and check it is healthy and runs as the fixed non-root
   UID (`docker compose exec api id`).
4. Run the test suite, because a bumped dependency can break behavior.
