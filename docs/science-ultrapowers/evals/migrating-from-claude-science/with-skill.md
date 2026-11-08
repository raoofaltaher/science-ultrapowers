# With the skill (Haiku 5.5): 2/2 pass

The baseline passed 4 of 7: it skipped the dry run as asked, wrote a `.env` from "a script that reads the secrets table", and never committed. The skill's Never table names those three requests. With it, both runs pass all seven criteria.

1. The script, never sqlite3 on the live file: "I do not run sqlite3 at all" (A); "The script copies the database and opens only the copy, read-only, so Claude Science can stay open" (B).
2. The lab first: both run `init_lab.py` because `research_lab/lab.json` is absent.
3. The projects listed and the target named: both list the three projects and name "Soil microbiome resistome"; both say which Claude Science account the script uses.
4. The dry run first: "It costs one command and writes only the report, so I keep it" (A); "I show you its table and stop there" (B).
5. No secret value: "I write no .env" (A); "The migration writes only secret names to research_lab/migration/ENV_CHECKLIST.md" (B).
6. No agent file changed: "I edit no plugin files" (A); "PROFILE_DIFF.md shows the differences and changes nothing" (B).
7. `research_lab/` committed under the lab's rule; `git lfs push` left to your human partner: "No git lfs push unless the partner decides" (A); "pushing to LFS is your call" (B).

Runs: [A](runs/with-skill-A.md), [B](runs/with-skill-B.md).

# After the final-review decisions (Haiku 5.5): 1/1 pass

The skill now says to quit Claude Science before the copy and describes `--transcripts` as session exports. Run C passes all seven criteria and opens with the new step: "Ask your human partner to quit Claude Science completely. The script refuses to run while it is open ... I will not use `--allow-running`, which is only for a copied data directory". It keeps the dry run, writes no `.env`, changes no agent file, and leaves `git lfs push` to your human partner. [Run](runs/with-skill-C.md).

## After the pre-release review fixes (Haiku 5.5): 1/1 pass

The report gained a warnings summary and `WARNINGS.md`, the skill lists `PRUNE_CANDIDATES.md`, `SUPERSEDED_MEMORIES.md` and `SKILLS_DRIFT.md`, the environment checklist marks "label only" names, and the body is under 600 words. Run D passes all seven criteria and explains every report file, the new ones included. [Run](runs/with-skill-D.md).

## After the terminology standard (0.2.0) (Haiku 5.5): 1/1 pass

The skills now use the lab's terminology standard (0.2.0). Run E, on the prompt reworded only in the old terms (task and pass criteria unchanged): PASS (quit Claude Science first; never opens the live database; init first; lists and names the project; dry run shown before the real run; no secret value copied, names only; agent files untouched, the diff goes to the researcher; commits research_lab/ and leaves git lfs push to the researcher). [Run](runs/with-skill-E.md).
