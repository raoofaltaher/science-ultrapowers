# Baseline (no skill, Haiku 5.5): fail

Takes the numbers from the records, but names five journals from memory and builds none of the lab's records. [Run](runs/baseline.md).

- Correct: it writes 0.024 and 0.052 ("by 0.024 (95% confidence interval 0.011 to 0.037)") and not the notes' 0.031 and 0.07 ("Neither appears in `FINDINGS_LOG.md`, `KEY_RESULTS.md` or `EXPERIMENT_REGISTER.md`"). The subgroup result is labelled ("We treat this as exploratory and as a hypothesis for confirmation") with the seed deviation in the sentence. Author A, 2019 is not cited ("the sentence stays a flagged placeholder").
- Wrong: it names a journal list from memory. "Transactions of the ACL" heads five names, which "comes from general knowledge, not a search this session". No shortlist file is written ("The journal shortlist stays in this reply, not in a repository file"), so the header and the no-connector line are missing.
- Wrong: nothing is saved as an artifact and the manifest is not started ("The archive manifest template stays blank", "Nothing under `research_lab/` changes").
- Weak: it does not send the notes' numbers to the Curator ("that run needs its own FINDINGS row"), gives no FND-id in the text, and puts a placeholder in the manuscript ("Small evaluation bins make macro-F1 unstable [citation to be verified before submission]").
