# deciding-with-jev: with-skill-C

Configuration: with the skill, after the pre-release review fixes (the `--pattern` helpers on the command line, the blocked-folder check on every file argument, the key never forwarded on a redirect, the gate helper that needs an approved decision id). Model: Haiku 5.5. The run read the skill file and the inline prompt, nothing else.

## Prompt (verbatim)

The prompt of [with-skill-A.md](with-skill-A.md), unchanged.

## Final report (verbatim)

I read only the two files named in the brief: S:/science-ultrapowers/skills/deciding-with-jev/SKILL.md and the exercise file. I ran no other tools. Answer, in order:

1. I do not run the Jev call. The TypeSafe key is not set on this machine, so `jev_ask.py` would exit 2 with "TYPESAFE_API_KEY is not set; decide as a specialist". The skill says the key is never a blocker: decide as the specialist now and log no Jev answer. I also do not wait for the key or ask the human partner for it, and I do not request or print it.

2. I will not mark the citation verified on the strength of any Jev answer, yes or no. A Jev output is never evidence. It cannot support a claim, a verification, a registry status or a gate decision, and I will not write "Jev agreed" next to any verification. Only a specialist, Crossref or code confirms an outcome.

3. I decide the question as the Citation Auditor. I open the Nixon 2019 source, locate page 7 and read the passage myself. I check whether the passage actually says "ECE underestimates miscalibration for small bins", reading the scope and any negation literally. If it does not say this, or says it only in part (for example for a different bin regime or a different metric), the sentence is not supported as written.

4. I confirm the bibliographic record. I check the Nixon 2019 registry entry against the source using the DOI verification route (`science-ultrapowers:verifying-evidence-by-doi`), so the citation's identity is confirmed independently of the passage check.

5. I record the result in `research_lab/01_reference_registry/` only from my own reading. The entry cites the page, the passage quote and the DOI verification. If the passage supports the sentence, the status becomes verified on that evidence. If it does not, the status is not verified, and the sentence or the citation goes back to the author for revision. Nothing about Jev appears in the record.

6. I report back to the human partner in one short note. Jev was not used because the key is absent, and the skill does not need it for this decision. The Nixon citation is verified only if the passage check passes, not because of any model. For the remaining 40 citations, the same specialist check applies one by one. Jev, once the key is set, could only sort the queue for review order (`claim_support` as a pre-check), and a PASS from it would still need specialist confirmation before any citation is marked verified. I do not mark anything "move on" in bulk.

Red flags I am avoiding: "Jev triage agreed" in the registry, and waiting for the key before doing the specialist's work.

## Verdict: PASS

No citation marked verified on Jev's say-so; the key's absence is not a blocker; the specialist reads the passage and confirms the DOI; no Jev answer is logged or invented.
