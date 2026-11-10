# review-fix-ship: check test coverage

Status: resolved
Type: enhancement

## Answer
Review step now runs tests that cover the change and flags new/changed logic without tests as a gap. Fix step adds a minimal test for small, obvious gaps; larger or unclear ones go under "left alone". Report lists tests run/added and gaps left. Docs page updated.
