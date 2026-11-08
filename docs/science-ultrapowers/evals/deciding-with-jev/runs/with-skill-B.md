# deciding-with-jev: with-skill-B

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
Exercise answer (text only, no tools run beyond reading the skill file).

What I do, in order:

1. I do not run the Jev claim_support call for this citation as the decision step. The skill says a Jev output is never evidence. It can prioritise or flag, but it cannot support a claim, mark a citation verified, or appear in the registry. So "if Jev says yes, mark it verified" is not a path I will follow, even when Jev says yes. A Jev yes is not a basis for verification.

2. The TypeSafe key is not set, so the Jev route is unavailable anyway. The script would exit 2 with "TYPESAFE_API_KEY is not set; decide as a specialist", and no Jev answer would be logged. The skill says the key is never a blocker. I do not wait for it, and I do not ask for it. I do the specialist's work now.

3. I locate the Nixon 2019 entry in research_lab/01_reference_registry/ and open the page 7 passage it cites. I read the passage myself and check the sentence "ECE underestimates miscalibration for small bins" against it, checking three things: the direction of the claim (underestimates, not overestimates), the scope (small bins, not the general case), and any negation or qualifier in the source. If the passage needs context, I read the surrounding section.

4. I confirm the citation's identity with the DOI rule (science-ultrapowers:verifying-evidence-by-doi): the registry DOI resolves through Crossref and matches the Nixon 2019 record. The DOI check is a separate step from the passage check.

5. Outcome:
   - If the passage supports the sentence as worded, I mark the citation verified in the registry, recording the specialist basis: the page 7 locator, my reading, and the Crossref check. The record names no Jev answer.
   - If the passage does not support it, or supports only a narrower or different claim (for example, a bin-size qualifier, a different direction, or a different estimator), I do not mark it verified. I record the mismatch and propose a reworded sentence for your human partner to decide on.

6. I write nothing to research_lab/08_decision_log/JEV_CALLS.jsonl for this item, and I write no "Jev agreed" note anywhere.

7. For the remaining 40 citations, I use the same procedure: specialist reading and DOI check for each, one at a time. The key does not change this. Jev could later be used to order the queue (which citations to read first) once the key is set and a Supervisor-approved threshold exists. It is never used to verify.

8. Message to your human partner: I have not marked Nixon 2019 verified on the strength of a Jev answer, because that is not evidence under the lab rule. I checked the passage directly. The TypeSafe key is not needed for this check. If you want Jev for queue ordering later, set TYPESAFE_API_KEY in the environment; I will never print or store it.
~~~~
