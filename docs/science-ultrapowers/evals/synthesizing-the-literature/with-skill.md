# With the skill (Haiku 5.5): 2/2 pass after one skill fix (iteration 2)

The baseline kept the log and refused the pooled number but wrote evidence records from abstracts. The skill's rules: a logged, bounded search with counts; evidence records only from papers that pass the five checks; a synthesis matrix that holds only evidence records; the flow diagram from the counts file through the script; a meta-analysis only as a study with a registered protocol; the survey text through the writing track.

## Iteration 1: B passes, A holds

- **B: pass.** "No candidate enters the matrix on its abstract." The preprint gets "no evidence record for a preprint". A bounded, logged search with criteria and snowballing both ways; the diagram "drawn with `flow_diagram.py --style prisma2020` from the counts JSON. If the sums fail, the log is fixed, never the count." The pooled number is a meta-analysis that "needs a registered protocol before any extraction", left to the researcher as a choice. The Literature Researcher and the auditor get the task block; the survey is a write-up that "follows approval, through `science-ultrapowers:writing-for-publication`"; each product is "saved as an artifact with `science-ultrapowers:saving-artifacts`".
- **A: hold.** It meets the same lines: "I do not start a card-and-write run.", no record for the preprint, "Build the counts file from the log, never from memory, and run `flow_diagram.py --style prisma2020`. If it exits 1, fix the log, not the count.", "A meta-analysis is a study, and it needs a registered protocol before any effect size is extracted.", the full task block, the auditor as reviewer. One line is missing: it promises that "the lab can ... write a narrative survey with a gap matrix" and never says that the survey's writing goes through `science-ultrapowers:writing-for-publication`.

## The fix

The transfer line for a review or survey paper in the skill now says that the survey text is never written inside this track, and that when the researcher asks for the survey the lead session says by name that its writing goes through `science-ultrapowers:writing-for-publication`.

## Iteration 2: A2 passes

A2 is run A's prompt on the fixed skill. The first query is logged and the criteria written before any further query ("no inclusion or exclusion criteria were set before this query"). Candidate 2 "gets no evidence record"; the full text of the others is read at the passage relied on. "If the script exits 1, the search log is corrected, never the count." "A meta-analysis is a study. It needs a registered protocol before any effect size is extracted", and it needs the whole lab ("init is re-run without `--track` after your yes"). The Literature Researcher gets the full task block and the Citation & Reference Auditor is the reviewer. The survey: "The survey is written in `science-ultrapowers:writing-for-publication`, after the Literature approval". The Literature approval is a `DEC-` row. It does not name `science-ultrapowers:saving-artifacts`; B does. [A](runs/with-skill-A.md), [B](runs/with-skill-B.md), [A2](runs/with-skill-A2.md).
