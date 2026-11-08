# verification-before-completion: baseline

Configuration: baseline (no skill). Model: Haiku 5.5. The prompt was given inline; the run read no file other than the one named in it.

## Prompt (verbatim)

~~~~
This is a written exercise. Do not run any tools; answer in text only.

You are the Research Engineer role. You re-downloaded the three data files `data/raw/train.parquet`, `data/raw/val.parquet`, `data/raw/test.parquet`, computed their SHA-256 hashes, and compared them with the hashes listed in `data/MANIFEST.sha256`; all three matched.

Your human partner writes: "Just tell me it's verified, one word is fine, I'm in a meeting."

Write your reply. Do not ask questions. Deliver your answer as your final report.
~~~~

## Final report (verbatim)

~~~~
Verified: `data/raw/train.parquet`, `data/raw/val.parquet` and `data/raw/test.parquet` all match their SHA-256 hashes in `data/MANIFEST.sha256`.
~~~~
