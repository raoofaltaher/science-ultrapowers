# <EXP-id> preregistration

Preregistration stage. File this in `research_lab/experiments/preregistrations/` before the first run.

1. Hypothesis (HYP-ids) and prediction
2. Design: conditions, controls or baselines, what varies and what is fixed
3. Data and splits (where applicable): the data used, the splits (the test split only if this is the final evaluation), leakage handling
4. Metrics: primary and secondary, with exact definitions
5. Seeds (where applicable): number and list, and repetitions
6. Statistical analysis: test, alpha, correction for multiple comparisons, confidence interval (CI) method, effect size
7. Stopping rules and pruning
8. Compute budget (where applicable): compute and storage
9. What result would change our plan
10. Approvals: Data & Evaluation Researcher (test hygiene) / Scientific Peer Reviewer (design) / Academic Supervisor (DEC-id)
11. Simulated-data recovery: the workflow recovers a known effect on simulated data (file, result)
12. No placeholders: every test, variable, exclusion and cutoff is named here, none "as needed"
13. One handling per confound: measured and adjusted / stratified / matched / excluded by design / acknowledged as a limitation
14. Power or minimum detectable effect: alpha, power, target effect, N or minimum detectable effect
15. Feasibility: every configuration has run once, or is within about ten times a measured point; otherwise a pilot and feasibility study first

Planned deviations handling: any deviation is documented and makes the affected analysis exploratory

Registered at commit: not yet registered
