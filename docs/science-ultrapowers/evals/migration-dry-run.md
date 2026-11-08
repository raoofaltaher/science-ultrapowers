# Migration dry run on a real Claude Science database (2026-11-08)

`migrate_claude_science.py --dry-run` ran on scratchpad copies of a real Claude Science data directory: the database, `preferences.json`, the published skills, the project's artifact folder and the connector cache, copied while Claude Science was running. The target was a scratchpad copy of the project's own `research_lab/`, scaffolded with `init_lab.py --yes`. The live database was never opened; the copies were opened read-only and immutable.

The machine holds two Claude Science org folders: the account the project was built in, and the account it moved to on 2026-11-07. The plan's pinned counts (79 / 15 / 418 / 555 / 940 / 1,527) were read from the first. The dry run ran on both.

## Old org (where the counts were pinned)

| step | source count | imported | already present | skipped (reason) |
|---|---|---|---|---|
| memories | 79 | 76 | 0 | 3 (3 superseded (SUPERSEDED_MEMORIES.md)) |
| profiles | 15 | 15 | 0 | 0 |
| artifacts | 418 | 418 | 0 | 0 |
| versions | 555 | 555 | 0 | 0 |
| dependencies | 940 | 940 | 0 | 0 |
| verification checks | 1527 | 1527 | 0 | 0 |
| connectors | 46 | 1 | 0 | 45 (20 not portable; 25 unknown server) |
| secret names | 6 | 6 | 0 | 0 |
| permissions | 47 | 43 | 0 | 4 (4 no Claude Code equivalent) |
| skill settings | 0 | 0 | 0 | 0 |
| published lab skills | 66 | 20 | 0 | 46 (46 not lab or vendored) |
| transcripts | 42936 | 0 | 0 | 42936 (42936 off (no --transcripts)) |

## Current org (the account the project moved to)

| step | source count | imported | already present | skipped (reason) |
|---|---|---|---|---|
| memories | 79 | 76 | 0 | 3 (3 superseded (SUPERSEDED_MEMORIES.md)) |
| profiles | 15 | 15 | 0 | 0 |
| artifacts | 418 | 418 | 0 | 0 |
| versions | 555 | 555 | 0 | 0 |
| dependencies | 940 | 940 | 0 | 0 |
| verification checks | 1527 | 1527 | 0 | 0 |
| connectors | 32 | 12 | 0 | 20 (20 not portable) |
| secret names | 6 | 6 | 0 | 0 |
| permissions | 47 | 43 | 0 | 4 (4 no Claude Code equivalent) |
| skill settings | 13 | 13 | 0 | 0 |
| published lab skills | 70 | 20 | 0 | 50 (50 not lab or vendored) |
| transcripts | 42936 | 0 | 0 | 42936 (42936 off (no --transcripts)) |

## Reading the numbers

- The six pinned counts match exactly in both orgs: 79 memories, 15 profiles, 418 artifacts, 555 versions, 940 dependency edges, 1,527 verification checks. Zero error lines.
- Memories: 66 project rows and 10 rows scoped to one of the project's conversations are imported; 3 superseded rows are listed, not imported. No row is about a person, so `PROFILE_MEMORIES.md` stays empty.
- Versions: 326 copied, 217 host-linked, 12 missing (the linked file is gone); every one is a ledger row, so none is lost. 97 linked files changed since Claude Science saved them (status `changed`, both hashes in the report); 7 linked versions had no checksum recorded (status `ok`, sha256 taken from the file).
- Verification checks: 171 are on an artifact version, 1,356 on a conversation claim (no version; `source_ref` kept).
- The rows that differ between the orgs are account settings, explained by the move: the old org's connector attachments name 25 servers that are no longer in the re-fetched directory cache, the old org recorded no skill settings, and the new org publishes 70 skills against 66.
- The dry run wrote only `migration/MIGRATION_REPORT.md`; `lab.json` still records `claudeScience: null`, and no memory or store file was written.
