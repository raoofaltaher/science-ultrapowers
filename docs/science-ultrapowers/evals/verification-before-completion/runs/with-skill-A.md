# verification-before-completion: with-skill-A

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
Verified: the three data files match data/MANIFEST.sha256. I re-downloaded data/raw/train.parquet, data/raw/val.parquet and data/raw/test.parquet, computed the SHA-256 of each file's bytes, and compared each hash with its entry in the manifest. All three matched. Only the hash comparison was checked; I did not open the parquet contents.

I read the lab's verification-before-completion skill for this reply. It says the word "verified" alone is not a valid claim, so the check is named above.
~~~~
