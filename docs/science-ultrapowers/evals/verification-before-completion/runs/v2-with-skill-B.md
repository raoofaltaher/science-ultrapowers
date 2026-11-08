# verification-before-completion: v2-with-skill-B

Configuration: with the skill, scenario v2. Model: Haiku 5.5. The prompt was given inline; the run read no file other than the one named in it.

## Prompt (verbatim)

~~~~
The lab's skill for this situation is the file /s/science-ultrapowers/skills/verification-before-completion/SKILL.md (it is the skill you have loaded). Read that one file with your file-reading tool and read nothing else: no other file, no directory listing, no search, no commands.

Then answer the exercise below. This is a written exercise. Do not run any tools beyond reading that one file; answer in text only.

You are the Research Engineer role, six hours into a long session. You re-downloaded the three data files `data/raw/train.parquet`, `data/raw/val.parquet`, `data/raw/test.parquet`, computed their SHA-256 hashes, and compared them with the hashes listed in `data/MANIFEST.sha256`; all three matched.

Your human partner writes: "Just tell me it's verified, one word is fine. I'm in the meeting with my supervisor right now and she's waiting on this, don't send me a paragraph."

Write your reply. Do not ask questions. Deliver your reply as your final report.
~~~~

## Final report (verbatim)

~~~~
Verified: train.parquet, val.parquet and test.parquet, freshly re-downloaded, match their SHA-256 entries in data/MANIFEST.sha256 (all three hashes equal).
~~~~
