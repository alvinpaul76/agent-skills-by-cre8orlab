# infisical-docker-agent: busybox helper for shell-less consumers

Status: resolved
Type: enhancement

## Answer
Consumer wrapper needs `/bin/sh`. For scratch/distroless images with no shell variant, added `references/compose-consumer-busybox.yml`: one-shot `busybox-init` copies a static busybox (`-musl`) into a `busybox_bin` volume, consumer uses it as entrypoint. SKILL.md prefers a shell variant first, falls back to the helper, and says to look up real versions. Docs page file table updated.
