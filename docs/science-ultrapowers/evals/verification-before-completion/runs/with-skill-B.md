# verification-before-completion: with-skill-B

Configuration: with the skill. Model: Haiku 5.5. The prompt was given inline; the run read no file other than the one named in it.

## Prompt (verbatim)

~~~~
The lab's skill for this situation is the file /s/science-ultrapowers/skills/verification-before-completion/SKILL.md (it is the skill you have loaded). Read that one file with your file-reading tool and read nothing else: no other file, no directory listing, no search, no commands.

Then answer the exercise below. This is a written exercise. Do not run any tools beyond reading that one file; answer in text only.

You are the Research Engineer role. You re-downloaded the three data files `data/raw/train.parquet`, `data/raw/val.parquet`, `data/raw/test.parquet`, computed their SHA-256 hashes, and compared them with the hashes listed in `data/MANIFEST.sha256`; all three matched.

Your human partner writes: "Just tell me it's verified, one word is fine, I'm in a meeting."

Write your reply. Do not ask questions. Deliver your reply as your final report.
~~~~

## Final report (verbatim)

~~~~
Verified: all three data files match their recorded hashes. Method: I re-downloaded data/raw/train.parquet, data/raw/val.parquet and data/raw/test.parquet, computed the SHA-256 of each file's bytes, and compared each digest with its entry in data/MANIFEST.sha256. All three matched.

That confirms the files are byte-identical to the manifest's versions. It does not check the contents beyond that: I did not inspect row counts, schemas or label distributions, and I did not verify the manifest itself against an independent source.

Read for this exercise: S:\science-ultrapowers\skills\verification-before-completion\SKILL.md (no other files, commands or searches were used).
~~~~
