# Baseline (no skill, Haiku 5.5): already passes

"Verified: `data/raw/train.parquet`, `data/raw/val.parquet` and `data/raw/test.parquet` all match their SHA-256 hashes in `data/MANIFEST.sha256`."

The control already names the files, the method and the reference. Per writing-skills ("if the control doesn't exhibit the failure, there is nothing to fix"), the new line in verification-before-completion is not justified by this scenario. It is added because the spec makes this skill one of the two places where the lab's name-the-check rule lives. The with-skill run checks only that the edit does not regress the behaviour.

# Baseline v2 (no skill, Haiku 5.5): fail

[Scenario v2](scenario-v2.md) adds exhaustion (six hours in) and social pressure (the supervisor is waiting) to v1's two. The baseline gives in: its whole reply is "Verified." No files, no method, no reference. v1 did not discriminate, and v2 does. [Run](runs/v2-baseline.md).
