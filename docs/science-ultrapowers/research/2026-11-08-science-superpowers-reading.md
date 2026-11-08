# science-superpowers (K-Dense) read against superpowers v7.0.2 and science-ultrapowers

Research record, 2026-11-08. Sources: the science-superpowers clone at commit 0374bdf (2026-09-13, MIT, Copyright (c) 2026 K-Dense, Inc.), the superpowers v7.0.2 clone, our plugin at 0.1.1, and five K-Dense pages (introducing-science-superpowers 2026-05-28, introducing-scientific-agents 2026-06-02, k-dense-web-vs-claude-science 2026-07-16, ai-co-scientist-not-ai-scientist 2026-05-05, the homepage).

## Their lifecycle (docs/research-workflow.md, authoritative)

| Stage | Skill | Evidence needed to move on |
|---|---|---|
| Frame | framing-research-questions | a falsifiable question with measures and scope; partner approves the written document |
| Ground | surveying-prior-work | cited methods, known confounds, prior effect sizes or a precision target |
| Design | designing-the-analysis | exact datasets, transformations, estimators, validation steps, sample-size rationale, decision rules |
| Register | preregistering-analysis | frozen predictions and analysis choices before confirmatory outcomes; a passing audit |
| Prepare | setting-up-reproducible-analysis | pinned environment, recorded seeds, immutable raw inputs, verified baseline |
| Execute | subagent-driven-analysis or executing-analysis | each registered step yields a validated, reviewed artifact |
| Verify | verifying-results-before-claiming | fresh reproduction, assumption checks, evidence for every claim |
| Challenge | requesting-red-team-review, then receiving-critical-review | Critical and Important issues addressed; changes checked against the registration |
| Report | reporting-and-archiving-findings | honest labels, limitations, reproduction instructions, an archive; the partner decides the fate |

Side branches: anomalies interrupt Execute or Verify (investigating-anomalous-results); feasibility mode (establishing-feasibility-first) is opt-in off Frame, partner-only entry and exit, defers Ground, Design, Register; parallel work through dispatching-parallel-investigations. Artifacts: `docs/science-superpowers/{questions,plans,preregistrations,feasibility}/`, `data/raw` immutable, `data/derived`, `results/`, `reports/`. One session-start hook injects the bootstrap; AGENTS.md is a pointer to CLAUDE.md, a contributor guide like ours ("pre-registration is the central discipline, the way TDD is central to Superpowers").

Iron Law (blog and skill): "NO CONFIRMATORY CLAIM WITHOUT A PRE-REGISTERED PREDICTION FIRST." Failure modes named: p-hacking, HARKing, optional stopping, the garden of forking paths. The commit of the registration is "the timestamp"; their own docs say the audit proves git consistency, not what anyone saw.

## Skill map (name, words, superpowers parent, what is genuinely scientific)

- using-science-superpowers, 973, using-superpowers; peek-and-frame red flags only.
- framing-research-questions, 1463, brainstorming (older shape); HARD-GATE no outcome contact before an approved question, operationalization, unit of analysis, bundled-question decomposition, feasibility split.
- surveying-prior-work, 567, original; extraction frame (methods, confounds, prior effect sizes for power). Allows web search as a source, no verification: weak.
- designing-the-analysis, 1007, writing-plans; immutable-raw data flow, one handling per confound, power or MDE, mandatory simulated-data recovery, No-Placeholders list, decision rule independent of unseen results.
- preregistering-analysis, 1959 + statistical-fallacies.md + prereg.sh (316 lines POSIX sh), test-driven-development; the best transplant: RED=LOCK, watch-it-fail=state the disconfirming result, GREEN=EXECUTE as registered, REFACTOR=SEPARATE; "Looked? It's exploratory. Period."; "don't register over runs that have never happened"; cheapest falsifying run first; 10-row rationalization table.
- establishing-feasibility-first, 2732, original; Iron Laws "NOTHING IS FEASIBLE UNTIL IT HAS RUN", "NOTHING IS BOUNDED UNTIL THE BOUND HAS FIRED"; abandonment condition agreed before measurement; kill criteria proven to fire; three geometric probes; extrapolation over ~10x is a hope; "Not a stop criterion" list; solver-specific examples.
- setting-up-reproducible-analysis, 887, using-git-worktrees; pin, lock, one global seed, raw read-only with CHECKSUMS and provenance, baseline reproduces before new work.
- subagent-driven-analysis, 910, subagent-driven-development (pre-v7 shape); protocol-compliance review (COMPLIANT/ISSUES against five checks; over- and under-building both fail) before rigor review (seven questions, Critical/Important/Minor); analyst gets the exact protocol excerpt; statuses DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, BLOCKED.
- executing-analysis, 475, executing-plans (thin, no ledger or rulings).
- dispatching-parallel-investigations, 702, dispatching-parallel-agents; Pre-Registration Guard: parallelism multiplies researcher degrees of freedom; report every pre-specified result, never the survivor.
- investigating-anomalous-results, 1205, systematic-debugging; Iron Law "NO ADJUSTMENTS WITHOUT ROOT-CAUSE INVESTIGATION FIRST"; classify bug / data issue / real finding; a real finding is reported, not fixed; drop data only for a documented invalid measurement; never change the seed to change the result; three failed adjustments means stop.
- verifying-results-before-claiming, 936, verification-before-completion; claim table: a null needs an interval, model quality needs out-of-sample used once, confirmatory needs the audit, reproduces means re-run from raw with the seed.
- requesting-red-team-review, 575, requesting-code-review; eight lenses: alternative explanations, confounds/Simpson, unchecked assumptions, leakage/overfitting, researcher degrees of freedom, multiplicity, reproducibility from raw and seed, over-claiming; "what would change your mind".
- receiving-critical-review, 783, receiving-code-review; collider/mediator check on a suggested covariate; a reviewer's "better analysis" is a deviation that makes it exploratory.
- reporting-and-archiving-findings, 954, finishing-a-development-branch; Report Content (confirmatory vs exploratory, intervals, deviations, limitations, no causal wording from observational data) and an Archive list (code, lockfile, seed, frozen registration with audit output, raw checksums, re-run command).
- writing-science-skills, 1314, writing-skills (older); nothing for research.

Fidelity to superpowers: fourteen of fifteen v7 skills have a counterpart (diagnosing-superpowers has none); two skills are original (surveying, feasibility). The transplant follows a pre-v7 snapshot: no ledger, rulings, completion contract, review-package or final whole-branch review. Vocabulary: test to prediction, failing test to disconfirming result, implementer to analyst, spec to pre-registration, code quality to rigor, bug to anomaly, fix to adjustment, merge to archive and report.

## Overlap with ours (what they add that we lack)

- No rule in ours against looking at outcomes before G2 (only test-split use is restricted).
- No confirmatory/exploratory label: FINDINGS statuses are tentative, verified, superseded, refuted only.
- No proof that the protocol predates the runs and was not edited after approval (no freeze, no audit).
- No result-level anomaly procedure: we route anomalies (Escalation row to Experiments Lead, Data & Evaluation, Supervisor) but give no procedure; our debugging skills are code-centred.
- No feasibility branch before G2: the protocol template has a compute budget but never asks whether the configuration has run.
- No protocol-compliance check at G3 (we check registration and reproducibility, not adherence); no Status field in the hand-off.
- Devil's-advocate template has six types; missing four lenses: unchecked assumptions, researcher degrees of freedom, multiplicity, reproducibility from raw and seed; no "what would change your mind".
- No referee-response procedure (receiving-code-review is code-flavoured).
- No raw-data immutability and checksum rule (the experiment register records code, config and environment hashes, not the input's identity).
- No statistical acceptance rows in verification (null needs interval, model needs held-out metric, confirmatory needs audit).
- No parallel-dispatch guard against reporting the surviving specification.
- Pre-registration template lacks: simulated-data recovery, No-Placeholders, one handling per confound, power or MDE.

What ours has that they lack: the DOI evidence rule with tiers, verifier, cards and registry; the findings ledger and canonical numbers; the lab notebook; the versioned artifact store with lineage, reviewer checks and LFS; lab memory with gate and linter; fourteen roles; gates G0-G6 with named independent checks and approvers; task brief and hand-off block; access requests; kickoff and stand-up; migration; the Jev layer; memory hooks.

## Ranked ideas worth taking

1. Freeze and audit for the protocol (prereg.sh: freeze commits the registration alone with raw-input blob checksums, stamps the hash; audit checks FROZEN, STAMP, INTEGRITY, CHRONOLOGY, DATA). Fit: G2 criterion "frozen", G4 criterion "audit passes, saved as artifact"; rewrite in Python stdlib (their script rejects whitespace in paths, is not transactional); the orchestrator runs it; protocol under research_lab/03_experiments/protocols/.
2. Confirmatory-versus-exploratory Iron Law and label. Fit: `Basis: confirmatory | exploratory` on FINDINGS rows; "Deviations and their effect" in PREREGISTRATION.md; a standing rule in running-the-lab; rationalization rows in recording-findings; a G6 criterion that the manuscript labels exploratory results.
3. Result-level anomaly skill (investigating-anomalous-results). Fit: new lab skill used by experiments-lead and data-evaluation-researcher, referenced from the Escalation row and G3/G4; output a notebook entry and, for a real finding, a proposed finding labelled exploratory.
4. Feasibility mode with kill criteria that must fire. Fit: new skill owned by experiments-lead; G2 criterion "every configuration has run once or is within about 10x of a measured point"; a Feasibility row in the protocol template; a feasibility status in the experiment register; condense hard, drop solver examples.
5. Protocol-compliance review before rigor review. Fit: PROTOCOL_COMPLIANCE.md template; a G3 independent check; a Status line in the hand-off; the rigor questions as a G4 checklist.
6. Design-validation block (simulated recovery, No-Placeholders, one handling per confound, power or MDE). Fit: four lines in PREREGISTRATION.md and G2 criteria for the Data & Evaluation sign-off.
7. Eight-lens red-team list and the reviewer-suggestion guard. Fit: extend DEVILS_ADVOCATE_TEMPLATE.md's Type column and scientific-reviewer; a referee-response section.
8. Raw-data immutability, CHECKSUMS and a reproducing baseline. Fit: G3 criterion and an Input checksums register field; link via artifacts.py link.
9. Statistical claim rows for the verification table and report rules. Fit: rows in recording-findings and G4 checks (do not copy their fallacies file; vendored scientific-critical-thinking covers 22 pitfalls).
10. Parallel-dispatch Pre-Registration Guard. Fit: a short section in running-the-lab or a lab overlay on dispatching-parallel-agents.

Smaller: the "Not a stop criterion" list; "a clean number is not a correct number"; the analyst prompt that gives only the step text plus the registration excerpt.

## What to leave

Multi-harness plumbing; K-Dense product material; their literature method (web search as a source, no DOI check); worktree and branch finishing (our commit rule forbids git writes by roles); executing-analysis and subagent-driven-analysis control flow (continuous execution conflicts with our gates; anonymous agents that commit); tool names in skills; writing-science-skills; the `@statistical-fallacies.md` link; environment commands with swallowed failures; solver-specific examples; their storage model (Markdown under docs/ with git as the only record); treating a git freeze as proof of what anyone saw; the upstream skill-reference prefix and the upstream `docs/` paths; prereg.sh tooling risks.

## Licence and provenance

MIT, Copyright (c) 2026 K-Dense, Inc.; the file states the skill content is original and the packaging is modeled on obra/superpowers. Verbatim copying is permitted with the notice kept with any substantial portion (our LICENSE section 7 and a PROVENANCE.md, as for the other vendored skills); reworded rules carry no copy obligation. No trademark grant. Commit 0374bdf82c2372bdf1667e3c762146c3a29215f5, "Add docs", 2026-09-13, shallow clone.
