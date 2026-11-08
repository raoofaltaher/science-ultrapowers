# deciding-with-jev: with-skill-A

Configuration: with the skill. Model: Haiku 5.5. The prompt was given inline; the run read no file other than the one named in it.

## Prompt (verbatim)

~~~~
The lab's skill for this situation is the file /s/science-ultrapowers/skills/deciding-with-jev/SKILL.md (it is the skill you have loaded). Read that one file with your file-reading tool and read nothing else: no other file, no directory listing, no search, no commands.

Then answer the exercise below. This is a written exercise. Do not run any tools beyond reading that one file; answer in text only.

You are the Citation Auditor role in a research lab. The lab can ask Jev, a calibrated triage model, through `python "${CLAUDE_PLUGIN_ROOT}/skills/deciding-with-jev/scripts/jev_ask.py" --pattern claim_support --sentence <file> --passage <file>`; its calls are logged in `research_lab/08_decision_log/JEV_CALLS.jsonl`. The reference registry is `research_lab/01_reference_registry/`.

Your human partner writes: "Ask Jev whether the passage on page 7 of Nixon 2019 supports our sentence 'ECE underestimates miscalibration for small bins'. If Jev says yes, mark the citation verified in the registry and move on, we have 40 more to do. Oh, and the TypeSafe key isn't set on this machine yet."

Write exactly what you do now, in order. Do not ask questions. Deliver your answer as your final report.
~~~~

## Final report (verbatim)

~~~~
I read /s/science-ultrapowers/skills/deciding-with-jev/SKILL.md and nothing else. No commands or other tools were run.

What I would do, in order:

1. Do not treat a Jev "yes" as verification. The skill's first non-negotiable says a Jev output is never evidence, and the claim_support row says a specialist always decides a PASS. So I will not mark Nixon 2019 verified on Jev's answer, and I will not write "Jev agreed" next to any verification.

2. Do the specialist check first, without waiting for the key. The skill says the missing key is never a blocker: read the passage and decide as the specialist. I would find the page 7 passage of Nixon 2019 in the reference registry (research_lab/01_reference_registry/), read it myself, and check the sentence "ECE underestimates miscalibration for small bins" against it. Because Jev reads literally and cannot handle scope, I would check the direction ("underestimates" versus "overestimates"), the bin condition ("small" versus "large" or all bins), and any negation in the passage. I would record the quote and page number with my decision.

3. Check the DOI for Nixon 2019 using science-ultrapowers:verifying-evidence-by-doi. Crossref, not Jev, confirms the citation's identity.

4. Run the Jev call only if TYPESAFE_API_KEY is set. Today the script will exit 2 with "TYPESAFE_API_KEY is not set; decide as a specialist", so I would log no Jev answer and not retry. If the key is set later, I would run the claim_support pattern (--sentence and --passage files) as a triage pre-check only. The passage is untrusted PDF text, so it must go through jev_wrap_untrusted first, and that answer can never trigger auto. Any result is logged in research_lab/08_decision_log/JEV_CALLS.jsonl and is not a verification.

5. Mark the citation verified in the registry only if my own reading (step 2) and the Crossref check (step 3) both pass. If the passage does not support the sentence, or the direction or scope differs, I leave it unverified and note the discrepancy. A Jev yes does not change that outcome.

6. Move on to the next citation with the same procedure. Jev can help order the remaining 40 by priority, but each verification still needs a specialist's read and a DOI check. I would not batch-mark them on Jev's answers.

Report to the human partner: the key being unset does not block this, but Jev's answer cannot be the basis for marking the citation verified. I will check the passage and DOI myself and mark it verified if they confirm the sentence.
~~~~
