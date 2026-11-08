# science-ultrapowers terminology standard

This standard controls the plugin's own terms and the writing rules of its texts. A research term outside it keeps its meaning in the researcher's field. It follows ASD-STE100 (Simplified Technical English) in shape: writing rules plus a controlled dictionary with one meaning per term. It follows the research literature in content: each term cites the standard or glossary it comes from, or says that this plugin coined it. Part 1 gives the writing rules. Part 2 gives the dictionary. The lists after Part 2 are read by `tests/claude-code/test-terminology.sh`, which refuses a term that is not approved. The Sources list at the end names every standard and glossary used.

## Part 1: writing rules

### Words

- **R1.** Use one term for one meaning.
- **R2.** Use one verb for one action.
- **R3.** Use each term as one part of speech.
- **R4.** Choose the short, common word.
- **R5.** Define a term at its first use in a document.
- **R6.** Use the plugin's terms as Part 2 gives them.
- **R7.** Add a new term to Part 2 before you use it.
- **R8.** Never use a term from the Not approved list.

### Grammar

- **R9.** Use the active voice and name the actor.
- **R10.** Use simple tenses: the present for a rule, the past for a finished action.
- **R11.** Never chain modal verbs.
- **R12.** Use an "-ing" word only as a noun.

### Sentences

- **R13.** Give one instruction in each sentence.
- **R14.** Write an instruction in 20 words or fewer.
- **R15.** Write an explanation in 25 words or fewer.
- **R16.** Keep the subject, the verb and the article.
- **R17.** Use a noun cluster of at most three words.
- **R18.** Put the condition before the instruction.

### Structure

- **R19.** Write one topic in each paragraph, in six sentences or fewer.
- **R20.** Use a numbered list for a sequence of three or more steps.
- **R21.** Use a bullet list for three or more parallel items.
- **R22.** Put the result first, then the reason.

### Names

- **R23.** Name a stage by its word, never by a code.
- **R24.** Name a folder by its word, never by its number.
- **R25.** Name a file by what it holds; give its path only where the reader must open it.
- **R26.** Name a status and a role by a word.
- **R27.** Keep the name of a product, a tool, an organization or a standard.

### Numbers and identifiers

- **R28.** Write a record identifier as `<PREFIX>-<NNNN>`.
- **R29.** Expand the prefix in every table header, as in "FND-id (finding)".
- **R30.** Keep an identifier that exists in a row exactly as written.
- **R31.** Write a number in prose only when it changes what the reader does.
- **R32.** State the unit of every number.

### Abbreviations

- **R33.** Expand an abbreviation at its first use in each document, as in `research question (RQ)`.
- **R34.** Introduce an abbreviation only when the Abbreviations list has it.
- **R35.** Write DOI without an expansion, because it is the name of the identifier.

### Spelling

- **R36.** Use American English and one dictionary.
- **R37.** Keep the spelling of a proper name.

### Status values

- **R38.** Write a status value as a lower-case word or phrase in prose.
- **R39.** Use a machine token only inside a script's output.

### Register

- **R40.** Claim an association from observational data; claim causation only when the design supports it.
- **R41.** State a result for the sample studied; extend it to a population only with a stated basis.
- **R42.** Match each hedging word to the strength of the evidence.
- **R43.** Label every analysis confirmatory or exploratory.
- **R44.** Quote a number only from the findings log or the key results table.
- **R45.** Cite only a matched source.
- **R46.** Name the mechanism whenever you write that a result is verified or checked.

## Part 2: controlled dictionary

One table per domain. Each term has one meaning, written in at most four sentences. "Operational form" names the file, column, command, block or value that embodies the term, or says none. "Replaces" lists the old terms; each one is on the Not approved list, and the full legacy forms are in the Legacy forms table. A row that names an old term ends with a legacy marker, so the test skips it. The Source column uses these short names, which the Sources list at the end cites in full:

- Framework for Open and Reproducible Research Training (FORRT): the open-scholarship glossary.
- Transparency and Openness Promotion (TOP): the guidelines of the Center for Open Science.
- Open Science Framework (OSF): its registration help pages.
- Registered Reports: the publishing model of the Center for Open Science.
- Contributor Roles Taxonomy (CRediT): the standard for naming contributions.
- Preferred Reporting Items for Systematic reviews and Meta-Analyses (PRISMA) 2020: the reporting guideline.
- Consolidated Standards of Reporting Trials (CONSORT): the guideline, with its pilot and feasibility extension.
- Standard Protocol Items: Recommendations for Interventional Trials (SPIRIT): the protocol guideline.
- Critical Appraisal Skills Programme (CASP): the appraisal checklists.
- Podsakoff 2016: the guidance on concept definitions.
- Spafford: the guidance on definitions in dissertations.
- Consortia Advancing Standards in Research Administration Information (CASRAI): the guide to operationalization.
- Simplified Technical English (STE): the controlled language ASD-STE100.
- Committee on Publication Ethics (COPE): its position on authorship and tools.
- this plugin: a term this plugin coined or fixed.

### Lifecycle and stages

| Term | Meaning in this plugin | Operational form | Not to be confused with | Replaces | Source |
|---|---|---|---|---|---|
| lifecycle | The route of a study from its question to its publication, in seven stages. A track enters it at the stage that fits what the researcher holds. | The stage table in `science-ultrapowers:running-the-lab`. | A project plan, which schedules work in time. | none | this plugin |
| track | A route into the lifecycle. The researcher chooses it by what they already hold: an idea, a study, literature, a manuscript, a draft or results. A track follows the same stages after its entry point. | One track skill for each route. | A task, which is one unit of work. | none | this plugin |
| stage | One of the seven named steps of the lifecycle. Each stage ends in a stage approval. | The stage table; the stage field of a task assignment. | A Stage 1 or Stage 2 of a Registered Report, which splits a study at the data. | gates; G0 to G6 (stage codes) | Registered Reports | <!-- legacy -->
| stage approval | The review that ends a stage, as in "the Preregistration approval". The role that owns the stage submits the work, independent checks run, and the approver decides. Nothing skips a stage approval, and an unresolved blocking objection stops it. | A row in the decision log and a row in the review log. | An approval of one task, which the project manager gives. | gate; stage gate | Registered Reports | <!-- legacy -->
| approval | A recorded decision by an approver that a stage, an exception or a manuscript may go on. It names the approver and the reason. | A decision log row with a `DEC-` identifier. | A review, which is a role's judgment and decides nothing. | sign-off | this plugin | <!-- legacy -->
| approver | The role that decides at a stage approval. The Academic Supervisor approves Question, Literature, Preregistration and Results. The Research Project Manager approves Execution and Reporting. The Academic Supervisor and then the researcher approve Publication. | The approver column of the stage table. | The submitter of the work, who does not decide. | none | this plugin |
| Question | The first stage. It ends when a hypothesis record links a falsifiable prediction to a research question (RQ), with prior-work evidence records and a stated contribution. The Methods & Innovation Researcher owns it. | The Question approval in the decision log. | A research question (RQ), which is the content, not the stage. | G0 (stage code) | Registered Reports | <!-- legacy -->
| Literature | The second stage. It ends when the search logs, the PRISMA 2020 counts, the evidence records and the source table rows exist. The Literature Researcher owns it, and the citation audit must be cleared. | The Literature approval; `literature/`. | A literature review, which is a deliverable that uses the stage's output. | G1 (stage code) | PRISMA 2020 | <!-- legacy -->
| Preregistration | The third stage. It ends when the protocol is registered with hypothesis, design, metrics, seeds, test, stopping rules, splits and compute budget. In Registered Reports, Stage 1 ends before data collection and Stage 2 follows it; this approval closes that first half. | The Preregistration approval; `experiments/preregistrations/`. | The preregistration, which is the document, not the stage. | G2 (stage code) | Registered Reports; OSF | <!-- legacy -->
| Execution | The fourth stage. It ends when every run is entered in the experiment register with commit, configuration hash, seeds, environment, artifacts and deviations. The Lab & Experiments Lead owns it. | The Execution approval; `experiments/EXPERIMENT_REGISTER.md`. | A run, which is one execution inside the stage. | G3 (stage code) | Registered Reports | <!-- legacy -->
| Results | The fifth stage. It ends when the analysis against the registered protocol is recorded in the findings log, with effect sizes, a confidence interval (CI) and tests. Write "the Results stage" in full where a manuscript's results section is near. | The Results approval; `findings/FINDINGS_LOG.md`. | The results section of a manuscript. | G4 (stage code) | Registered Reports | <!-- legacy -->
| Reporting | The sixth stage. It ends when documentation, model cards and datasheets are updated from the findings log and the source table. The Documentation Writer owns it. | The Reporting approval. | Publication, which releases a manuscript. | G5 (stage code) | this plugin | <!-- legacy -->
| Publication | The seventh stage. It ends when a manuscript or thesis chapter, for example in the Introduction, Methods, Results and Discussion (IMRaD) form, may leave the lab. The Academic Paper Author owns it. | The Publication approval; the full citation audit and the retraction check. | Reporting, which updates documents inside the lab. | G6 (stage code) | Registered Reports | <!-- legacy -->
| preregistration | A dated plan of one study, registered before the confirmatory outcomes are seen. It holds the hypothesis, design, metrics, seeds, test, stopping rules, splits and compute budget. A registration is a time-stamped, read-only version of that plan. | `experiments/preregistrations/`; the template `PREREGISTRATION.md`. | A protocol deviation, which records a change after registration. | pre-registration; pre-registered; pre-register | OSF; TOP; FORRT | <!-- legacy -->
| register | To commit the protocol as a dated, read-only version before any confirmatory run. The lead session runs the script; a role never does. | `preregister.py register`. | The experiment register and the source table, which are records. | freeze | OSF | <!-- legacy -->
| registered protocol | The protocol as registered. It is never edited. A change goes in a protocol deviation. | The file's `Registered at commit:` line; the commit trailers `Preregistration:` and `Preregistration-Timestamp:`. | A draft protocol, which is still editable. | frozen | OSF; Registered Reports | <!-- legacy -->
| time-stamped | A property of a registered protocol: its commit carries the registration's date, time and hash. The time stamp proves the order of commits, not what anyone saw. | The trailer `Preregistration-Timestamp:`. | The commit date of any other file. | none | OSF |
| registration check | A script check of five items that shows the registered protocol predates the runs and has not changed. It reports each item as clear, not clear or unprovable. | `preregister.py check`; its JSON names the five items. | The citation audit and the protocol-adherence review. | protocol audit | OSF; Registered Reports | <!-- legacy -->
| registered | The first item of the registration check. A commit that holds the protocol alone exists. | The `registered` key of the check's JSON. | The experiment status `registered`, which marks a run entered before it starts. | none | OSF |
| timestamp | The second item of the registration check. The registration commit carries the protocol's hash and the time of registration. | The `timestamp` key of the check's JSON. | The adjective time-stamped, which names the property. | none | OSF |
| unaltered | The third item of the registration check. The protocol file at the branch head equals the registered version, byte for byte. | The `unaltered` key of the check's JSON. | A protocol deviation, which is a recorded change. | none | OSF |
| chronology | The fourth item of the registration check. Every confirmatory run was committed after the registration, judged by commit ancestry. A run on a parallel branch is unprovable, never clear. | The `chronology` key of the check's JSON. | The date column of the experiment register. | none | OSF; Registered Reports |
| inputs | The fifth item of the registration check. The input files match the checksums recorded at registration. | The `inputs` key of the check's JSON; the input checksums field of the experiment register. | The inputs line of a task assignment, which lists files. | none | this plugin |
| protocol | The study protocol only: the registered plan of one study. | The registered protocol file. | A search plan, which the search log records; an evaluation plan, which is part of the protocol. | none | SPIRIT |
| protocol deviation | A departure from the registered protocol. The deviation record states what changed and its effect, and the affected analysis becomes exploratory. | The deviations section of `PREREGISTRATION.md`; the deviations column of the experiment register. | A departure from a task assignment, which the task report lists. | none | CONSORT; SPIRIT; OSF |
| confirmatory | An analysis planned in the registered protocol and run as registered. Only a confirmatory analysis tests the hypothesis. | The label on a finding and on a manuscript claim. | A replication, which repeats a study. | none | FORRT; TOP |
| exploratory | An analysis not in the registered protocol, or run after a protocol deviation. It generates hypotheses and tests none. | The label on a finding and on a manuscript claim. | A pilot run, which tests feasibility. | none | FORRT; TOP |
| pilot and feasibility study | A small study before the protocol that tests whether a configuration can run and within what bounds. It is opt-in, and the researcher decides its entry and exit. It cannot confirm a hypothesis. | `experiments/feasibility/`. | A confirmatory experiment. | feasibility mode | CONSORT | <!-- legacy -->
| pilot run | One run of a pilot and feasibility study, at a stated size. | A row of the experiment register that points to the feasibility record. | A run of the registered experiment. | scaling probes; smoke test | CONSORT | <!-- legacy -->
| series of pilot runs | Pilot runs at growing size, used to test whether a bound holds. The stopping rules end it. | The feasibility record. | A single pilot run. | campaign | CONSORT | <!-- legacy -->
| stopping rules | Conditions agreed before measurement that end an experiment or a series of pilot runs. Each rule must be shown able to fire. | The stopping rules section of the preregistration and of the feasibility record. | A stop because results look good, which is optional stopping. | kill criteria | SPIRIT; CONSORT | <!-- legacy -->
| protocol-adherence review | A review that checks the analysis against the registered protocol, before the rigor review. It lists each deviation and each step built over or under the protocol. | A report in `reviews/reports/` with an `ADH-` identifier. | The registration check, which tests the commits, not the analysis. | compliance review; protocol-compliance review | CONSORT; SPIRIT | <!-- legacy -->
| adversarial review | The strongest good-faith case against each primary claim, written by an independent reviewer who did not write the work. It runs at Results and at Publication, before the approval. Each objection is graded blocking, major or minor. | `reviews/reports/` with an `ADV-` identifier; the template `ADVERSARIAL_REVIEW.md`. | A referee report, which judges a whole manuscript. | devil's advocate; devil's-advocate; red team; red-team | FORRT; CASP | <!-- legacy -->
| critical-appraisal domain | One angle of appraisal that an adversarial review applies, such as confounds, leakage or multiplicity. | The domain list in `science-ultrapowers:running-the-lab`; the templates `ADVERSARIAL_REVIEW.md` and `REFEREE_REPORT.md`. | A stage criterion. | lenses | CASP | <!-- legacy -->
| blocking | The top grade of an objection. If it holds, the claim is wrong or unsupported as stated, and the stage approval stops. It clears by new evidence, a narrower claim or an approver's decision. | The grade column of an adversarial review. | major, which only weakens a claim. | CRITICAL | this plugin | <!-- legacy -->
| major and minor | Two lower grades of an objection. A major objection weakens the claim; the author answers it or narrows the claim. A minor objection is noted in the report. | The grade column of an adversarial review. | blocking. | none | this plugin |
| cleared and not cleared | The two verdicts of a citation audit. Cleared means every item is clear. Not cleared stops the stage approval until the items are fixed and re-audited. | The verdict line of the audit report. | The status clear in the registration check. | PASS; FAIL | this plugin | <!-- legacy -->
| hypothesis record | One hypothesis with its research question link, falsifiable prediction, refuting outcome, smallest effect size of interest and contribution relative to prior work. | `HYP-0001`; the template `HYPOTHESIS_RECORD.md`. | A finding, which is a recomputed result. | H-card | FORRT; OSF | <!-- legacy -->
| research question (RQ) | The question a study answers. A hypothesis is a falsifiable answer to it. | The project description; the RQ link of a hypothesis record. | A hypothesis. | none | FORRT |
| smallest effect size of interest (SESOI) | The smallest effect that would count for the research question. It is stated in the hypothesis record before data. | The prediction line of the hypothesis record. | A statistical significance threshold. | minimum effect of interest | FORRT; Registered Reports | <!-- legacy -->
| contribution relative to prior work | What a hypothesis adds against the closest matched sources: a replication, an extension, a new population or a novel claim. | A field of the hypothesis record. | The prior-work summary, which lists the sources. | novelty delta; innovation delta | this plugin | <!-- legacy -->
| primary claim | The claim that a stage approval tests, such as the main result of a manuscript. | The claim column of an adversarial review. | A secondary claim. | headline claim | this plugin | <!-- legacy -->
| negative result | A result that does not support the hypothesis. The lab records it as carefully as a positive one. | A lab notebook entry and a finding. | A deviation or an error. | dead ends | TOP | <!-- legacy -->
| held-out test set | Data kept apart until the registered final evaluation. A role touches it once. | The splits field of the protocol. | A validation set, which tunes the method. | none | this plugin |
| workflow | A sequence of processing steps in an analysis. | A workflow diagram or a script. | The lifecycle. | pipeline | this plugin | <!-- legacy -->

### Sources and evidence

| Term | Meaning in this plugin | Operational form | Not to be confused with | Replaces | Source |
|---|---|---|---|---|---|
| source | A work the lab may read or cite: an article, a chapter, a proceedings paper or a dataset description. Each source has one row in the source table. | `literature/SOURCES.csv`. | A citation, which is the in-text pointer to a source. | none | PRISMA 2020 |
| source table | One row for every source accepted or evaluated, with its status, DOI status, class and evidence record identifiers. The columns are source_id, status, doi_status, source_class and evidence_records. | `literature/SOURCES.csv`. | A reference list, which holds only cited sources. | reference registry; registry | PRISMA 2020 | <!-- legacy -->
| source class | The kind of a source, set by peer review and DOI. The next four rows name the values. A class is a word, never a letter. | The `source_class` column. | The source status. | see Legacy forms | this plugin |
| peer-reviewed, matched DOI | A work from a peer-reviewed journal or proceedings whose DOI resolved in Crossref and matched the full text in hand. It is not retracted. It is the default class for evidence. | The `source_class` value `peer-reviewed matched doi`. | A source whose DOI resolves but was never matched. | Tier A | this plugin | <!-- legacy -->
| peer-reviewed, no DOI | A peer-reviewed work without a Crossref DOI. It is citable only by exception: the official proceedings page confirms it, and the researcher approves it. | The `source_class` value `peer-reviewed no doi`; `literature/EXCEPTIONS.md`. | A work that is not peer-reviewed. | Tier B | this plugin | <!-- legacy -->
| not peer-reviewed | A preprint, thesis, blog, web page, vendor document, model recall, lab note or secondary citation. It is never evidence. A preprint may be cited only to credit a method's origin, marked as a preprint. | The `source_class` value `not peer-reviewed`. | A peer-reviewed work without a DOI. | Tier C | FORRT | <!-- legacy -->
| retracted or withdrawn | A work with a retraction, a withdrawal or an unresolved expression of concern. It is never evidence, unless the text discusses the retraction itself. | The `source_class` value `retracted`. | A work that a later paper corrects. | Tier X | this plugin | <!-- legacy -->
| source status | The value of the `status` column. The nine values are citable, citable by exception, metadata matched, awaiting full text, awaiting approval, candidate, excluded: preprint, excluded: retracted and rejected: mismatch. Only the first two permit a citation. | The `status` column. | The finding status. | ADMITTED; ADMITTED_EXCEPTION; DOI_VERIFIED; PENDING_FULLTEXT; PENDING_APPROVAL; CANDIDATE_DOI; EXCLUDED_PREPRINT; EXCLUDED_RETRACTED; REJECTED_MISMATCH | PRISMA 2020 | <!-- legacy -->
| matched | A DOI whose Crossref metadata matched the title, first author and year read from the full text in hand. | The `doi_status` value `matched` in the verifier's output. | verified, which names a recomputed finding. | none | this plugin |
| doi status | The verifier's result for one DOI, kept in its own column. The verifier prints its other values as machine tokens. | The `doi_status` column; `verify_doi.py`. | The source status. | none | this plugin |
| source check | One of the five checks that every source needs before a citation: resolve and match, integrity, peer review, read and record. A role never accepts another role's word that the checks were done. | `science-ultrapowers:verifying-evidence-by-doi`. | A review, which is a role's judgment. | none | this plugin |
| evidence record | One claim from one source: a verbatim quote of at most two sentences, its location, the DOI and its DOI status. It names the extractor and the verifier. | `literature/evidence_records/`; `EVR-0001`. | A finding, which is a recomputed result. | evidence card; evidence cards | PRISMA 2020 | <!-- legacy -->
| search log | The record of one search: queries, databases, dates, counts and screening decisions. | `literature/search_logs/`. | The lab notebook. | none | PRISMA 2020 |
| screening | Judging each identified record against the eligibility criteria. The counts go in the search log and feed the PRISMA 2020 flow. | The search log. | prioritization, which only orders the screening. | none | PRISMA 2020 |
| PRISMA 2020 flow | The counts from records identified to sources included, drawn from the search logs. | The counts table of a search log. | A reading list. | none | PRISMA 2020 |
| snowballing | Backward and forward citation chasing from a matched source. | A section of the search log. | A database search. | none | PRISMA 2020 |
| evidence rule | Facts enter a record only from peer-reviewed sources with a matched DOI, read in full text and held in an evidence record. A source without a DOI needs the researcher's approval. Preprints, web pages, lab notes and memory are never evidence. | `science-ultrapowers:verifying-evidence-by-doi`. | A rule of evidence in law. | none | this plugin |
| preprint | A version of a work that is not peer reviewed. It belongs to the not peer-reviewed class. | The status value `excluded: preprint`. | The published version of the same work. | none | FORRT |
| DOI | The persistent identifier of a published work. The lab writes it without an expansion. | The `doi` column; `verify_doi.py`. | The source identifier, which names a table row. | none | this plugin |
| full-text request | A request to the researcher for a paper that is missing or paywalled. Roles never get around a paywall. | The request type `full-text request`. | A DOI confirmation. | FULLTEXT | this plugin | <!-- legacy -->
| DOI confirmation | A request to the researcher to confirm a candidate DOI against the paper in hand. | The request type `DOI confirmation`. | A match by the verifier. | CONFIRM_DOI | this plugin | <!-- legacy -->
| exception approval | A request for the researcher's approval to cite a peer-reviewed source that has no DOI. The approval is logged. | The request type `exception approval`; `literature/EXCEPTIONS.md`. | An approval of a stage. | see Legacy forms | this plugin |
| request status | The state of a request: open, fulfilled, approved, declined or unavailable. | The status column of `requests/ACCESS_REQUESTS.md`. | The source status. | see Legacy forms | this plugin |
| request priority | The urgency of a request: blocks a stage, this cycle or background. | The priority column of `requests/ACCESS_REQUESTS.md`. | The priority of a task. | see Legacy forms | this plugin |
| citation audit | The check of every citation of a deliverable against the source table and the text of its sources. Only the Citation & Reference Auditor performs it, and its verdict is cleared or not cleared. | `literature/citation_audits/`; the template `CITATION_AUDIT.md`. | The registration check; a review. | none | this plugin |
| retraction check | The check that no source of a deliverable is retracted or withdrawn. It runs before the Publication approval. | A section of the citation audit. | A full citation audit. | retraction sweep | this plugin | <!-- legacy -->

### Findings and records

| Term | Meaning in this plugin | Operational form | Not to be confused with | Replaces | Source |
|---|---|---|---|---|---|
| finding | A result recomputed from its file and entered in the findings log. A literature fact becomes a finding only through an evidence record. | A row of `findings/FINDINGS_LOG.md`. | A claim in a manuscript, which a finding supports. | none | this plugin |
| findings log | The append-only table of findings, one row per finding. A verified row is never edited; a new row supersedes it. | `findings/FINDINGS_LOG.md`. | The lab notebook, which tells what was done. | ledger; findings ledger | this plugin | <!-- legacy -->
| key results table | The numbers a document quotes, each with its exact definition, its finding identifier and its allowed wording. | `findings/KEY_RESULTS.md`. | The findings log, which holds every finding. | canonical numbers | this plugin | <!-- legacy -->
| finding status | One of four values: tentative, verified, superseded by a later finding, or refuted by a later finding. There is no other value. | The status column of the findings log. | The source status. | none | this plugin |
| verified | A finding status. The Findings & Records Curator recomputed the finding from its file and named the check. | The value `verified` in the findings log. | matched, checked and reviewed. | none | this plugin |
| checked | A re-run of any procedure, with its mechanism named: which files, which method and against what. A bare claim of a check counts as unchecked. | The mechanism line of a task report. | verified, which names a finding only. | none | this plugin |
| reviewed | A named role's judgment of work that the role did not write. | A row of the review log. | checked, which is a re-run. | none | this plugin |
| recorded | Entered in a record after the check that supports it. A number seen only in a console log is not recorded. | A row with its date and role. | record, which is the noun. | none | this plugin |
| record | The noun for one row or one file of the lab's records. "The records" means all of them together. | none | recorded, which is the state of having been entered. | none | this plugin |
| lab notebook | Dated, append-only entries, one for each working session and role. It lists attempts, commands, results, failures, links and next steps. | `findings/LAB_NOTEBOOK.md`. | The findings log, which holds only recomputed findings. | none | this plugin |
| experiment | A registered unit of work with its own identifier and one row in the experiment register. | An `EXP-` row. | A run, which is one execution. | none | this plugin |
| run | One execution of an experiment or of a pilot run. | The run directory named in the register. | An experiment. | none | this plugin |
| experiment register | One row for each experiment: protocol, hypothesis, commit, configuration hash, seeds, environment, status, outputs, deviations and findings. | `experiments/EXPERIMENT_REGISTER.md`. | The source table; the preregistration. | none | this plugin |
| decision log | The dated log of stage approvals and scope decisions. | `decisions/DECISION_LOG.md`; `DEC-` rows. | The automation log. | none | this plugin |
| review log | One row for each review or stage-approval check. | `reviews/REVIEW_LOG.md`; `REV-` rows. | The decision log. | none | this plugin |
| automation log | The record of Jev calls and their thresholds. | `automation/JEV_CALLS.jsonl`; `automation/thresholds.json`. | The decision log. | none | this plugin |
| claim-evidence map | A table that links each claim of a manuscript to the findings and sources that support it. | A deliverable of the Academic Paper Author. | The key results table. | none | this plugin |
| internal review | The Academic Reviewer's review of a proposal, chapter or report before submission. | A `REV-` row; the template `INTERNAL_REVIEW.md`. | A referee report. | none | this plugin |
| referee report | The Scientific Peer Reviewer's report on a manuscript, with a recommendation. | The template `REFEREE_REPORT.md`. | An adversarial review, which attacks the claims. | none | this plugin |
| response to reviewers | The author's point-by-point answer to a referee report. | A deliverable of the Academic Paper Author. | A rebuttal in an adversarial review. | none | this plugin |
| checks performed | The line of a task report that lists each check with its mechanism. | A field of `TASK_REPORT.md`. | The review requested line. | verification record | this plugin | <!-- legacy -->
| record identifier | A prefix, a hyphen and a four-digit number, as in `FND-0001`. The prefix names the kind of record: finding, evidence record, review, adversarial review, request, decision, task, hypothesis, experiment, protocol-adherence review, method proposal or risk. A lab keeps one counter for each prefix. An identifier is never reused or renumbered. | `FND-0001` finding; `EVR-0001` evidence record; `REV-0001` review; `ADV-0001` adversarial review; `REQ-0001` request; `DEC-0001` decision; `TASK-0001` task; `HYP-0001` hypothesis; `EXP-0001` experiment; `ADH-0001` protocol-adherence review; `MTH-0001` method proposal; `RSK-0001` risk. | The name of a memory entry. | see Legacy forms | this plugin |

### The artifact archive

| Term | Meaning in this plugin | Operational form | Not to be confused with | Replaces | Source |
|---|---|---|---|---|---|
| artifact | A saved deliverable of the lab: a report, protocol, figure, table, script or dataset. | `artifacts/archive/`; the skill `saving-artifacts`. | A build artifact in software, or an object in archaeology. | none | this plugin |
| artifact archive | The versioned, git-committed copy of every saved artifact, with its tables. | `artifacts/archive/`; `artifacts.py`. | The lab's records, which hold the facts. | artifact store | this plugin | <!-- legacy -->
| archive table | One of the archive's four data files: artifacts, versions, dependencies and verification checks. Rows are keyed by version identifier, so a text search for a file name finds nothing. | `artifacts.jsonl`, `versions.jsonl`, `dependencies.jsonl` and `verification_checks.jsonl`. | A table of the findings log. | none | this plugin |
| version | One saved state of an artifact, with its own version identifier. | `artifacts.py save`; a row of `versions.jsonl`. | A version of the plugin. | none | this plugin |
| provenance | Where a version came from: its inputs and its reviewer findings. | `artifacts.py provenance <version id>`; `lineage` stays a hidden alias for one release. | A citation, which points to a source. | lineage | this plugin | <!-- legacy -->
| milestone copy | A version kept for good at a milestone. | `--destination milestone`. | A working copy. | snapshot | this plugin | <!-- legacy -->
| working copy | A version that a later save replaces. | `--destination working`. | A milestone copy. | working_data | this plugin | <!-- legacy -->
| save | Copy files into the archive as a new version, with a role, a task and the inputs. | `artifacts.py save`. | link. | none | this plugin |
| link | Record an existing file as an input without copying it. | `artifacts.py link`. | save. | none | this plugin |
| reviewer finding | A reviewer's verdict on one version: the claim, the verdict, the severity and the evidence. | `artifacts.py findings add`. | A finding, which is a recomputed result. | none | this plugin |
| reviewer-finding status | One of open, author-responded, re-opened or closed. The author sets author-responded. The reviewer closes or re-opens. | `respond`; `findings review`. | The finding status. | claimed; unaddressed | this plugin | <!-- legacy -->
| Git Large File Storage (LFS) | A Git extension that keeps large files outside the commit history. The archive checks that large files use it. | `artifacts.py lfs-check`; `.gitattributes`. | The artifact archive. | none | this plugin |

### Team and coordination

| Term | Meaning in this plugin | Operational form | Not to be confused with | Replaces | Source |
|---|---|---|---|---|---|
| role | One of the fourteen functions of the lab. Claude Code runs a role from its file, with the skills that file preloads. The researcher holds the fifteenth place. | `agents/<id>.md`; `science-ultrapowers:<id>`. | The researcher, who is not a role file. | subagent | CRediT | <!-- legacy -->
| the researcher | The human who runs the lab and holds final authority. The researcher supplies full texts, approves exceptions and approves Publication. | none | A role, which Claude Code runs. | your human partner; the owner; the user | this plugin | <!-- legacy -->
| Principal Researcher | The researcher's own title in the team. It owns full texts, exception approvals and the final release. | The first row of the team table, "Principal Researcher (you)". | The Literature Researcher, who searches. | References & Resources Specialist | this plugin | <!-- legacy -->
| lead session | The researcher's own Claude Code session. It acts as the project manager: it assigns roles, relays requests and commits the records. | The session that loads `science-ultrapowers:running-the-lab`. | A role run for one task. | main session | this plugin | <!-- legacy -->
| project manager | The Research Project Manager role, and the part the lead session plays. It assigns tasks, keeps the work plan and the risk register, and moves the stages along. | `research-project-manager`. | The researcher, who decides. | orchestrator | CRediT | <!-- legacy -->
| assign | Give a task to a role with a task assignment. The reviewer is never the author. | `science-ultrapowers:<id>` with a task assignment. | Delegate a decision, which no role may do. | dispatch | this plugin | <!-- legacy -->
| independent reviewer | A reviewer who gets only the work and its inputs and took no part in producing it. | A role run with the task assignment alone. | A non-author, who may know the author's reasoning. | fresh-context | this plugin | <!-- legacy -->
| non-author | A role that did not write the work it reviews. Nobody reviews or audits their own work. | The reviewer column of a task assignment. | An independent reviewer, who also lacks the author's reasoning. | none | this plugin |
| task | One unit of work with an identifier, an owner, a reviewer, a stage and a due date. | A row of `planning/WORK_PLAN.md`; `TASK-0001`. | A track. | none | this plugin |
| task assignment | The block that assigns every task: identifier, stage, owner, reviewer, due date, objective, inputs, deliverables, completion criteria and constraints. A free-form paragraph is not a task assignment. | The block in `science-ultrapowers:running-the-lab`. | The project description. | task brief | this plugin | <!-- legacy -->
| task report | The block every role ends a task with. A role that returns without it has not delivered. | `TASK_REPORT.md`; the block in `science-ultrapowers:running-the-lab`. | A lab notebook entry. | hand-off; handoff | this plugin | <!-- legacy -->
| completion criteria | The checkable bullets of a task assignment. The task is done when each one holds. | The criteria line of a task assignment. | The stopping rules of an experiment. | acceptance criteria | this plugin | <!-- legacy -->
| deliverable | A file that a task produces. | The deliverables line of a task assignment. | An artifact, which is a saved deliverable. | none | this plugin |
| work plan | The table of tasks with owners, reviewers, stages and statuses. | `planning/WORK_PLAN.md`. | The roadmap. | task board | this plugin | <!-- legacy -->
| risk register | The table of risks, each with an identifier, an owner and a mitigation. | `planning/RISK_REGISTER.md`. | The experiment register. | none | this plugin |
| roadmap | The status of the project's phases. | `planning/ROADMAP_STATUS.md`. | The work plan. | none | this plugin |
| session | One working session in Claude Code. A session opening starts it and a session close ends it. | Notes in `decisions/lab_meetings/`. | A conversation history, which can span several sessions. | none | this plugin |
| session opening | The note that starts a session. It gives a short lab status and the recommended next action. | `SESSION_OPENING.md`, filed in `decisions/lab_meetings/`. | A lab meeting. | kickoff | this plugin | <!-- legacy -->
| session close | The routine that ends a session: admit memory entries, check large files, write the note, clear the working notes and commit. | `SESSION_CLOSE.md`, filed in `decisions/lab_meetings/`. | A handover summary. | stand-up; standup | this plugin | <!-- legacy -->
| lab meeting | The note of a milestone meeting or a weekly meeting. | `decisions/lab_meetings/`. | A session opening. | none | this plugin |
| handover summary | The summary imported from another system or session that feeds the next session opening. | A file in `migration/`. | A task report. | where we left off | this plugin | <!-- legacy -->
| escalation | The route a role follows when a situation lies outside its decision rights. | The escalation table in `science-ultrapowers:running-the-lab`. | An approval. | none | this plugin |
| request | An ask from a role to the researcher: a full-text request, a DOI confirmation or an exception approval. A role files it and states it at the top of its task report. | `requests/ACCESS_REQUESTS.md`; `REQ-` rows. | A task. | none | this plugin |
| restricted folders | The folders that no role opens and that Jev never reads. | The `lab.json` key `scope.restrictedFolders`; the project description lists them. | A folder of private notes. | out of scope; blocked folder | this plugin | <!-- legacy -->
| lab | The project's research lab: its fourteen roles and its folder. | `research_lab/`. | The plugin. | none | this plugin |
| Research Project Manager | Plans and assigns the work, keeps the work plan and the risk register, and approves Execution and Reporting. CRediT roles: Project administration; Resources. | `research-project-manager`. | The researcher. | see Legacy forms | CRediT |
| Academic Supervisor | Directs the work and approves Question, Literature, Preregistration and Results, and Publication with the researcher. CRediT roles: Supervision; Conceptualization; Validation. | `academic-supervisor`. | The researcher's own academic supervisor, whom it never replaces. | none | CRediT |
| Literature Researcher | Searches, screens and records sources and evidence records. CRediT roles: Investigation; Data curation; Conceptualization. | `literature-researcher`. | The Citation & Reference Auditor, who audits the result. | none | CRediT |
| Methods & Innovation Researcher | Formulates hypotheses, methods and method proposals. CRediT roles: Methodology; Conceptualization; Formal analysis. | `methods-innovation-researcher`. | The Data & Evaluation Researcher, who tests the data. | see Legacy forms | CRediT |
| Data & Evaluation Researcher | Owns data validity, evaluation and statistics, and checks test-set hygiene at Preregistration. CRediT roles: Formal analysis; Methodology; Data curation; Validation. | `data-evaluation-researcher`. | The Findings & Records Curator, who recomputes. | none | CRediT |
| Lab & Experiments Lead | Registers and runs experiments, pins environments and tracks compute. CRediT roles: Investigation; Resources; Data curation; Validation. | `lab-experiments-lead`. | The Research Engineer, who writes code changes. | see Legacy forms | CRediT |
| Findings & Records Curator | Recomputes findings from their files and keeps the findings log and the key results table. CRediT roles: Data curation; Validation. | `findings-records-curator`. | The Documentation Writer. | see Legacy forms | CRediT |
| Documentation Writer | Writes documentation, model cards and datasheets from the records. CRediT roles: Writing - original draft; Visualization; Data curation. | `documentation-writer`. | The Academic Paper Author. | none | CRediT |
| Academic Paper Author | Writes manuscripts and claim-evidence maps and answers reviewers. CRediT roles: Writing - original draft; Writing - review and editing; Visualization. | `academic-paper-author`. | The Documentation Writer. | see Legacy forms | CRediT |
| Academic Reviewer | Reviews work before submission. CRediT roles: Writing - review and editing; Validation. | `academic-reviewer`. | The Scientific Peer Reviewer, who writes referee reports. | none | CRediT |
| Scientific Peer Reviewer | Writes referee reports and runs adversarial reviews, never on its own work. CRediT roles: Validation; Writing - review and editing. | `scientific-peer-reviewer`. | The Academic Reviewer. | see Legacy forms | CRediT |
| Citation & Reference Auditor | Runs citation audits and retraction checks. CRediT roles: Validation; Data curation. | `citation-reference-auditor`. | The Literature Researcher, who records sources. | see Legacy forms | CRediT |
| Research Engineer | Writes code changes with tests. CRediT roles: Software; Methodology. | `research-engineer`. | The Lab & Experiments Lead. | none | CRediT |
| Decision Systems Specialist | Runs the Jev layer: calibration studies, thresholds and log audits. CRediT roles: Methodology; Formal analysis; Software; Validation. | `decision-systems-specialist`. | The Academic Supervisor, who decides. | none | CRediT |
| CRediT role | One of the fourteen contribution roles of CRediT. Each lab role lists the CRediT roles that match its function. The mapping describes a function and never names a role as an author, which follows COPE. | The CRediT line in each agent file. | An authorship claim. | none | CRediT; COPE |
| Jev | TypeSafe's decision-support model. It gives typed answers with probabilities. A Jev output is never evidence and never approves a stage. | `science-ultrapowers:deciding-with-jev`. | An evidence source. | none | this plugin |
| prioritization | Putting screening, matching or routing work in order, often with a Jev answer. | A Jev call in the automation log. | screening, which judges eligibility. | triage | this plugin | <!-- legacy -->
| calibration study | A study of how well Jev's stated probabilities match outcomes. It reports the expected calibration error (ECE), the maximum calibration error (MCE) and the negative log-likelihood (NLL). | Run by the Decision Systems Specialist. | An accuracy test. | none | this plugin |

### Lab memory

| Term | Meaning in this plugin | Operational form | Not to be confused with | Replaces | Source |
|---|---|---|---|---|---|
| lab memory | The folder of lab knowledge: one fact in each file, indexed by `MEMORY.md` and committed to git. It holds what the records cannot tell. | `memory/`. | Claude Code user memory; a model's recall, which is never evidence. | none | this plugin |
| memory entry | One file with one fact of at most three sentences, a type, a basis and the name of the learning role. | A file in `memory/project/` or `memory/artifact/<id>/`. | A row of a record. | none | this plugin |
| entry type | The kind of a memory entry, one of five. A pitfall is a trap the records do not show; a decision is a reason no decision log row holds. A lesson is what the lab learned and the records do not state. A directive is a standing instruction from the researcher, and vocabulary is a term only this project knows. | The `type` frontmatter key: `pitfall`, `decision`, `lesson`, `directive` or `vocabulary`. | The type of a finding or a request. | none | this plugin |
| pitfall | An entry type: a trap that cost the lab time and that the records do not show. | `type: pitfall`. | A finding. | gotcha | this plugin | <!-- legacy -->
| basis | The field of a memory entry that says how the lab knows the fact. Stated means a person said it. Observed means the lab saw it in this project's data or runs. Inferred means a hypothesis, which every prune re-checks. | The `basis` frontmatter key: `stated`, `observed` or `inferred`; the consistency check reads `evidence` as a legacy key. | The evidence rule, which governs citations. | see Legacy forms | this plugin |
| admission criteria | The four tests of a memory entry: verified, durable, expensive to rediscover, and not derivable from code, documents, history or records. All four must hold, or nothing is saved. | The criteria in `science-ultrapowers:remembering-for-the-lab`. | The evidence rule. | memory gate | this plugin | <!-- legacy -->
| consistency check | The script that checks the memory folder against its format and its index. Exit code 0 means clean. | `memory-lint.mjs`. | A review of a fact. | lint | this plugin | <!-- legacy -->
| working notes | Temporary notes of one session, deleted at the session close. | `research_lab/.working/`. | The lab notebook, which stays. | scratch | this plugin | <!-- legacy -->
| reminder | A line that a hook prints to ask whether the session learned a fact worth admitting. | The hooks `memory-nudge` and `memory-postcompact`; the variable `SCIENCE_ULTRAPOWERS_NO_MEMORY_REMINDER`. | A task. | nudge | this plugin | <!-- legacy -->
| memory index | The list of entries, one line each, kept under the index budget. | `memory/MEMORY.md`; the `lab.json` key `memory.indexBudget`. | A memory entry. | none | this plugin |
| remember | Admit a fact to lab memory after the admission criteria hold. Only the lead session writes. | The remember steps of the skill. | recorded. | none | this plugin |
| recall | Search lab memory before assigning a role or recomputing a result. | The index first, then a search of the folder. | Human recall. | none | this plugin |
| prune | Re-check old entries and every inferred entry, and merge near-duplicates, at a milestone. | The prune steps of the skill. | Delete. | none | this plugin |
| Claude Code user memory | The memory of the researcher's own Claude Code setup. Facts about a person go there and never into lab memory. | Outside `research_lab/`. | Lab memory. | none | this plugin |

### Contributor vocabulary

| Term | Meaning in this plugin | Operational form | Not to be confused with | Replaces | Source |
|---|---|---|---|---|---|
| skill | A Markdown file of binding instructions that Claude Code loads for a kind of task. | `skills/<name>/SKILL.md`; `science-ultrapowers:<name>`. | A role, which Claude Code runs for one task. | none | this plugin |
| skill description | The first line of a skill's frontmatter. It says only when to use the skill, never its steps. | The `description` key. | The skill's overview. | none | this plugin |
| addendum | The binding block that the plugin adds to an adopted or kept skill. The upstream text stays verbatim. | The heading `LAB ADDENDUM (binding)`. | The upstream text. | overlay | this plugin | <!-- legacy -->
| adopted third-party skill | A skill copied into the plugin with its license text and its provenance record. Only its addendum changes. | A skill folder with `PROVENANCE.md`. | A skill the plugin wrote. | vendored | this plugin | <!-- legacy -->
| upstream text | The verbatim body of an adopted skill. The terminology test does not scan it. | Everything below the addendum. | The addendum. | none | this plugin |
| provenance record | The file that states a skill's source, license and vetting. | `PROVENANCE.md`. | The provenance of a version, which says where an artifact came from. | none | this plugin |
| tool vetting record | The note that a tool or an adopted skill was vetted before use. | `tool_vetting/`. | A provenance record. | none | this plugin |
| pressure test | A test that runs a model on a hard scenario to see whether a skill changes its behavior. It has a baseline run and with-skill runs. | `docs/science-ultrapowers/evals/<skill>/`. | A load test. | none | this plugin |
| binding rule | A rule of a skill that has no exception. It heads the skill in a code block. | The section titled `The binding rule`. | A warning sign. | Iron Law | this plugin | <!-- legacy -->
| warning signs | A list of thoughts or acts that mean stop and restore the rule. | The section titled `Warning signs`. | rationalizations and replies. | Red Flags | this plugin | <!-- legacy -->
| rationalizations and replies | A table that pairs a tempting excuse with the reply that answers it. | The section titled `Rationalizations and replies`. | warning signs. | Common Rationalizations | this plugin | <!-- legacy -->
| disclosure check | The test that refuses a project-specific string or a foreign-harness string in the plugin. | `tests/claude-code/test-no-foreign-harness.sh`. | The terminology test. | leak gate | this plugin | <!-- legacy -->
| terminology standard | This document. | `docs/science-ultrapowers/terminology.md`. | A skill description. | none | STE |
| terminology test | The test that refuses a not-approved term, a stage code, a British spelling or an unexpanded abbreviation. | `tests/claude-code/test-terminology.sh`. | The disclosure check. | none | this plugin |
| legacy form | An old term, identifier, token or key that the plugin keeps only to read an existing lab. A line that names one ends with a legacy marker. | The Legacy forms table; the marker `<!-- legacy -->`. | A not-approved term in new text. | none | this plugin |
| session primer | The skill text that the session-start hook puts in front of a session. | `using-science-ultrapowers`; `hooks/session-start`. | A session opening. | bootstrap | this plugin | <!-- legacy -->
| lab set-up | The creation of a lab's folders, templates and keys. | `science-ultrapowers:initializing-a-research-lab`. | A migration. | scaffold | this plugin | <!-- legacy -->
| migration | A change of an existing lab to the current layout. It is shown as a plan of rename, header and rewrite lines before the researcher confirms. | `init_lab.py`; `science-ultrapowers:migrating-from-claude-science`. | The lab set-up of a new lab. | none | this plugin |
| output style | A Claude Code file that sets how a session writes. The plugin ships one, Scholarly Explanatory. | `output-styles/scholarly-explanatory.md`. | The terminology standard, which the style applies. | none | this plugin |
| scholarly register | The writing style of the Register rules R40 to R46: claims matched to evidence, labeled analyses, numbers from records. | R40 to R46. | A citation style. | none | this plugin |
| agent | The file of a role under `agents/`. Lab text says role; contributor text may say agent. | `agents/<id>.md`. | A role, which is the function. | none | this plugin |
| hook | A script that Claude Code runs at a session event and whose output enters the session. | `hooks/`. | A Git hook. | none | this plugin |
| toolkit | A set of review skills that the stage table lists by stage. | The review toolkit table of `science-ultrapowers:running-the-lab`. | A role. | none | this plugin |
| dry run | A run that shows its plan and writes nothing. | The plan printed before `--yes`. | A pilot run. | none | this plugin |
| connector | A link from Claude Code to an outside service, such as a literature database. | The connector kinds in the lab set-up. | A source. | none | this plugin |

## Not approved

Each line below reads `old term => approved term`. The test matches the old term as a whole word, ignoring case. The stage codes are caught by the stage-code rule and are not listed here.

<!-- not-approved -->
```
gate => stage approval
gates => stage approvals
stage gate => stage approval
freeze => register
frozen => registered
ledger => findings log
findings ledger => findings log
canonical numbers => key results table
reference registry => source table
registry => source table
evidence card => evidence record
evidence cards => evidence records
hand-off => task report
handoff => task report
task brief => task assignment
kickoff => session opening
stand-up => session close
standup => session close
orchestrator => project manager
main session => lead session
dispatch => assign
subagent => role
fresh-context => independent
task board => work plan
acceptance criteria => completion criteria
devil's advocate => adversarial review
devil's-advocate => adversarial review
red team => adversarial review
red-team => adversarial review
Iron Law => binding rule
Red Flags => warning signs
Common Rationalizations => rationalizations and replies
lenses => critical-appraisal domains
kill criteria => stopping rules
campaign => series of pilot runs
scaling probes => pilot runs
feasibility mode => pilot and feasibility study
compliance review => protocol-adherence review
protocol-compliance review => protocol-adherence review
protocol audit => registration check
lineage => provenance
artifact store => artifact archive
gotcha => pitfall
nudge => reminder
scratch => working notes
memory gate => admission criteria
lint => consistency check
your human partner => the researcher
the owner => the researcher
the user => the researcher
out of scope => restricted folders
blocked folder => restricted folders
where we left off => handover summary
References & Resources Specialist => Principal Researcher
pipeline => workflow
smoke test => pilot run
bootstrap => session primer
scaffold => lab set-up
vendored => adopted
overlay => addendum
leak gate => disclosure check
H-card => hypothesis record
novelty delta => contribution relative to prior work
innovation delta => contribution relative to prior work
minimum effect of interest => smallest effect size of interest
pre-registration => preregistration
pre-registered => preregistered
pre-register => preregister
Tier A => peer-reviewed, matched DOI
Tier B => peer-reviewed, no DOI
Tier C => not peer-reviewed
Tier X => retracted
ADMITTED => citable
ADMITTED_EXCEPTION => citable by exception
DOI_VERIFIED => metadata matched
PENDING_FULLTEXT => awaiting full text
PENDING_APPROVAL => awaiting approval
CANDIDATE_DOI => candidate
EXCLUDED_PREPRINT => excluded: preprint
EXCLUDED_RETRACTED => excluded: retracted
REJECTED_MISMATCH => rejected: mismatch
FULLTEXT => full-text request
CONFIRM_DOI => DOI confirmation
retraction sweep => retraction check
verification record => checks performed
PASS => cleared
FAIL => not cleared
CRITICAL => blocking
sign-off => approval
headline claim => primary claim
dead ends => negative results
triage => prioritization
claimed => author-responded
unaddressed => re-opened
snapshot => milestone
working_data => working
digital object identifier => DOI
```

## Spelling

Each line below reads `British form => American form`. The test refuses the British form in the plugin's own text. A proper name keeps its spelling.

<!-- spelling -->
```
analyse => analyze
analysed => analyzed
analysing => analyzing
behaviour => behavior
licence => license
artefact => artifact
judgement => judgment
organise => organize
organisation => organization
summarise => summarize
prioritise => prioritize
centre => center
colour => color
favour => favor
labelled => labeled
labelling => labeling
modelling => modeling
programme => program
catalogue => catalog
defence => defense
recognise => recognize
minimise => minimize
optimise => optimize
standardise => standardize
characterise => characterize
```

## Abbreviations

Each line below reads `ABBR => expansion (ABBR)`. The first use of the abbreviation in a document must show the expansion. DOI is never expanded.

<!-- abbreviations -->
```
RQ => research question (RQ)
ECE => expected calibration error (ECE)
CI => confidence interval (CI)
PRISMA => Preferred Reporting Items for Systematic reviews and Meta-Analyses (PRISMA)
LFS => Git Large File Storage (LFS)
CRediT => Contributor Roles Taxonomy (CRediT)
IMRaD => Introduction, Methods, Results and Discussion (IMRaD)
MCE => maximum calibration error (MCE)
NLL => negative log-likelihood (NLL)
COPE => Committee on Publication Ethics (COPE)
SESOI => smallest effect size of interest (SESOI)
```

## Legacy forms

An existing lab can hold any of these old forms. Scripts read them and write the new form, and a migration rewrites them in a shown plan. Every line that names an old form ends with a legacy marker, so the test skips it.

| Old form | New form | Where it may still appear |
|---|---|---|
| Stage codes G0 to G6 | The seven stage names | Nowhere; the stage-code rule refuses them. | <!-- legacy -->
| The `Gate <G#>` field of a task assignment | The stage field | Rows of an existing work plan or review log. | <!-- legacy -->
| `F-` identifiers, as in F-0001 | `FND-` | Existing rows, and references such as "superseded by F-0041". | <!-- legacy -->
| `H-` identifiers | `HYP-` | Existing hypothesis records. | <!-- legacy -->
| `EC-` identifiers | `EVR-` | Existing evidence records. | <!-- legacy -->
| `RV-` identifiers | `REV-` | Existing rows of the review log. | <!-- legacy -->
| `DA-` identifiers | `ADV-` | Existing adversarial reviews. | <!-- legacy -->
| `D-` identifiers | `DEC-` | Existing rows of the decision log, and the approval named in `automation/thresholds.json`. | <!-- legacy -->
| `T-` identifiers | `TASK-` | Old tests and plans. | <!-- legacy -->
| `MP-` identifiers | `MTH-` | Existing method proposals. | <!-- legacy -->
| `R-` identifiers | `RSK-` | Existing rows of the risk register. | <!-- legacy -->
| `PC-` identifiers | `ADH-` | Plans only; no shipped record holds one. | <!-- legacy -->
| `00_project_knowledge/` | `project/` | A lab before migration. | <!-- legacy -->
| `01_reference_registry/` | `literature/` | A lab before migration. | <!-- legacy -->
| `02_findings_ledger/` | `findings/` | A lab before migration. | <!-- legacy -->
| `03_experiments/` | `experiments/` | A lab before migration. | <!-- legacy -->
| `04_reviews/` | `reviews/` | A lab before migration. | <!-- legacy -->
| `05_access_requests/` | `requests/` | A lab before migration. | <!-- legacy -->
| `06_decisions/` | `decisions/` | A lab before migration. | <!-- legacy -->
| `07_project_management/` | `planning/` | A lab before migration. | <!-- legacy -->
| `08_decision_log/` | `automation/` | A lab before migration. | <!-- legacy -->
| `09_skill_vetting/` | `tool_vetting/` | A lab before migration. | <!-- legacy -->
| `evidence_cards/` | `evidence_records/` | A lab before migration. | <!-- legacy -->
| `audits/` holding screening logs | `search_logs/` | A lab before migration. | <!-- legacy -->
| `protocols/` | `preregistrations/` | A lab before migration. | <!-- legacy -->
| `artifacts/store/` | `artifacts/archive/` | A lab before migration. | <!-- legacy -->
| `.scratch/` | `.working/` | A lab before migration. | <!-- legacy -->
| `REGISTRY.csv` | `SOURCES.csv` | A lab before migration. | <!-- legacy -->
| `FINDINGS.md` | `FINDINGS_LOG.md` | A lab before migration. | <!-- legacy -->
| `CANONICAL_NUMBERS.md` | `KEY_RESULTS.md` | A lab before migration. | <!-- legacy -->
| `DECISIONS.md` | `DECISION_LOG.md` | A lab before migration. | <!-- legacy -->
| `TASK_BOARD.md` | `WORK_PLAN.md` | A lab before migration. | <!-- legacy -->
| `H_CARD.md` | `HYPOTHESIS_RECORD.md` | A lab before migration. | <!-- legacy -->
| `HANDOFF.md` | `TASK_REPORT.md` | A lab before migration. | <!-- legacy -->
| `DEVILS_ADVOCATE_TEMPLATE.md` | `ADVERSARIAL_REVIEW.md` | A lab before migration. | <!-- legacy -->
| `REVIEW_ACADEMIC.md` | `INTERNAL_REVIEW.md` | A lab before migration. | <!-- legacy -->
| `SESSION_KICKOFF.md` | `SESSION_OPENING.md` | A lab before migration. | <!-- legacy -->
| `SESSION_STANDUP.md` | `SESSION_CLOSE.md` | A lab before migration. | <!-- legacy -->
| Source table columns `ref_id`, `lab_status`, `tier`, `verify_status`, `evidence_cards` | `source_id`, `status`, `source_class`, `doi_status`, `evidence_records` | A lab before migration. | <!-- legacy -->
| Source statuses ADMITTED, ADMITTED_EXCEPTION, DOI_VERIFIED, PENDING_FULLTEXT, PENDING_APPROVAL, CANDIDATE_DOI, EXCLUDED_PREPRINT, EXCLUDED_RETRACTED, REJECTED_MISMATCH | citable, citable by exception, metadata matched, awaiting full text, awaiting approval, candidate, excluded: preprint, excluded: retracted, rejected: mismatch | The `lab_status` column of an existing source table. | <!-- legacy -->
| Source classes Tier A, Tier B, Tier C, Tier X | The four source class words | Existing source tables and exception files. | <!-- legacy -->
| Request types FULLTEXT, CONFIRM_DOI, APPROVAL | full-text request, DOI confirmation, exception approval | The type column of an existing request file. | <!-- legacy -->
| Request statuses OPEN, FULFILLED, APPROVED, DECLINED, UNAVAILABLE | open, fulfilled, approved, declined, unavailable | The status column of an existing request file. | <!-- legacy -->
| Request priorities P1, P2, P3 | blocks a stage, this cycle, background | The priority column of an existing request file. | <!-- legacy -->
| Reviewer-finding statuses claimed, unaddressed, resolved | author-responded, re-opened, closed | Rows of an existing archive's verification checks. | <!-- legacy -->
| The DOI check value `VERIFIED` | `matched` | Existing evidence records; readers accept it for one release. | <!-- legacy -->
| Registration check items FROZEN, STAMP, INTEGRITY, CHRONOLOGY, DATA | registered, timestamp, unaltered, chronology, inputs | Plans only; no shipped script holds them. | <!-- legacy -->
| Commit trailers `Protocol-Freeze:` and `Protocol-Stamp:` | `Preregistration:` and `Preregistration-Timestamp:` | Plans only; no shipped script writes them. | <!-- legacy -->
| `snapshot` as a destination | `milestone` | Rows of an existing archive; the archive reads both. | <!-- legacy -->
| `working_data` as a destination | `working` | Rows of an existing archive; the archive reads both. | <!-- legacy -->
| The archive command `lineage` | `provenance` | A hidden alias for one release. | <!-- legacy -->
| The archive commands `check add`, `check list` and `check review` | `findings add`, `findings list` and `findings review` | Old scripts and notes; the archive reads both. | <!-- legacy -->
| The archive command `mark-addressed` | `respond` | A hidden alias for one release. | <!-- legacy -->
| The archive option `--command` | `--task` | Old scripts and notes. | <!-- legacy -->
| The `lab.json` key `jev.blockedPaths` | `scope.restrictedFolders` | An existing `lab.json`; the old key is read. | <!-- legacy -->
| The `lab.json` role keys `lab-project-manager`, `methods-researcher`, `experiments-lead`, `findings-curator`, `paper-author`, `scientific-reviewer`, `citation-auditor` | `research-project-manager`, `methods-innovation-researcher`, `lab-experiments-lead`, `findings-records-curator`, `academic-paper-author`, `scientific-peer-reviewer`, `citation-reference-auditor` | An existing `lab.json`, and hand copies under a project's `.claude/agents/`. | <!-- legacy -->
| The memory frontmatter key `evidence:` | `basis:` | Memory entries written before migration. | <!-- legacy -->
| The memory entry type `gotcha` | `pitfall` | Memory entries written before migration and imported entries. | <!-- legacy -->
| The variable `SCIENCE_ULTRAPOWERS_NO_MEMORY_NUDGE` | `SCIENCE_ULTRAPOWERS_NO_MEMORY_REMINDER` | A shell profile; the hooks honor both. | <!-- legacy -->

## Sources

- Parsons, S., et al. (2022). A community-sourced glossary of open scholarship terms. Nature Human Behaviour, 6, 312-318. This is the FORRT glossary.
- Center for Open Science. TOP Guidelines (Transparency and Openness Promotion).
- Nosek, B. A., et al. (2018). The preregistration revolution. Proceedings of the National Academy of Sciences, 115(11), 2600-2606.
- Center for Open Science. The Registered Reports model.
- Open Science Framework. Registration help pages.
- ANSI/NISO Z39.104-2022. CRediT, the Contributor Roles Taxonomy.
- Page, M. J., et al. (2021). The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. BMJ, 372, n71.
- Schulz, K. F., Altman, D. G., and Moher, D. (2010). CONSORT 2010 statement. BMJ, 340, c332.
- Eldridge, S. M., et al. (2016). CONSORT 2010 statement: extension for pilot and feasibility trials. BMJ, 355, i5239.
- Chan, A.-W., et al. (2013). SPIRIT 2013 statement: defining standard protocol items for clinical trials. Annals of Internal Medicine, 158(3), 200-207.
- Critical Appraisal Skills Programme. CASP checklists. The organization's name keeps its spelling.
- Podsakoff, P. M., MacKenzie, S. B., and Podsakoff, N. P. (2016). Recommendations for creating better concept definitions in the organizational, behavioral, and social sciences. Organizational Research Methods, 19, 159-203.
- Spafford, E. H. Definitions and terminology in dissertations. Purdue University, CERIAS.
- CASRAI. Operationalization in research.
- ASD-STE100, Issue 9 (2025). Simplified Technical English.
- ISO 24495-1:2023. Plain language, Part 1: governing principles and guidelines.
- ISO 704. Terminology work: principles and methods.
- Committee on Publication Ethics (COPE). Position statement on authorship and artificial intelligence tools.
