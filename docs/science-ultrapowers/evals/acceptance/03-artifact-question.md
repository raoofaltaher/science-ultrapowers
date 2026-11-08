# Acceptance 03: the artifact question

Date: 2026-11-08. Same project as acceptance 02, a headless session: `claude -p "What is RV-0048 based on, and what is still unaddressed on it?"`. RV-0048 is a Citation Auditor's gate review imported from Claude Science; its latest version in the store has five lineage inputs and three checks.

## First run, plugin 0.1.0: FAIL

16 turns. The session invoked `science-ultrapowers:running-the-lab`, said the record map points at the store's lineage, then grepped `artifacts.jsonl` for the artifact id, grepped `dependencies.jsonl` and `verification_checks.jsonl` for the same id, found nothing, and concluded "lineage and check-list rows are empty for this artifact, so the answer has to come from the report itself". It read the report's own input section and the task records and gave a correct-looking answer with the caveat that the store "carries no lineage or verification-check rows for it".

The store disagreed. `artifacts.py lineage <latest version id>` on the same artifact listed five inputs (the ELU paper's PDF, a second PDF, the proposed registry rows, the proposed BibTeX additions, the addendum's CSV) and one resolved check, and `check list --all` held two more checks on the review's claims. The ledgers are keyed by version id, so the grep by artifact id could never match.

## The fix, 0.1.1

`running-the-lab`'s record map now says: `science-ultrapowers:saving-artifacts` answers this question (`search <name>`, then `lineage <version id>` and `check list`; the ledgers are keyed by version id, so a grep of them proves nothing). `saving-artifacts` gained the same row and a rationalization row. Pressure scenario v2 (`../saving-artifacts/scenario-v2-based-on.md`): baseline fails on the same shortcut, two with-skill runs pass. The plugin was updated in the project through the marketplace (`claude plugin update`, 0.1.0 to 0.1.1).

## Second run, plugin 0.1.1: PASS

23 turns. Tool uses, in order: `science-ultrapowers:running-the-lab`, `science-ultrapowers:saving-artifacts`, then `artifacts.py search RV-0048`, `lineage` on both artifacts the search returned, `check list` on the report, `graph` on the report, and only then the review log, the report's headings, the task board, the registry, the evidence cards and the git log for what the store cannot hold.

The answer, in structure:

- **Based on**: the five inputs from the lineage output, named one by one (the addendum CSV, the proposed registry rows and BibTeX additions, and the two PDFs), with the review's own scope from the review log beside them.
- **Checks in the store**: five across the five versions, three pass and two warn, every one resolved; no open verdict.
- **Still unaddressed**, from the records: one registry row never promoted after its fix (checked in the card's quote field and the git history), nine stale registry notes, an unregenerated BibTeX file (entry count and timestamp checked), no auditor re-check of the last correction batch, five open full-text requests, one version-of-record comparison never done.

Verdict: PASS. The "based on" answer comes from `lineage`, the checks from `check list`, and the session says which part of "unaddressed" the store cannot hold and where it read it instead. The session's own closing observation is a fair one: a `check add` for each instruction a review leaves for other people would make the second half a one-command answer too.
