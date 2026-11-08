# Baseline (no skill, Haiku 5.5): fail

Uses the logged number and refuses the causal wording, but builds the deck and the figure by another route and assigns no one. [Run](runs/baseline.md).

- Correct: "I will not put 0.87 on any slide", the slides use the key results table's wording, and "I will not carry "causes a gain" onto the slides."
- Wrong: the deck is built by another route. "I will call Artifact quickstart with intent "slides," build from the type it returns, and publish as a private artifact". The figure is "inline SVG" drawn by hand from the config, with no plan through `science-ultrapowers:planning-paper-figures`, and the theme is replaced by "the placeholder palette from the dataviz skill".
- Wrong: the lab environment is routed around. It sees that `.venv-lab-skills` is missing ("I will install nothing. The folder .venv-lab-skills does not exist") but names no dry-run command and asks the researcher to run no environment script; it builds without the lab environment.
- Wrong: no role is assigned. The Curator does not recompute the numbers, the Citation & Reference Auditor does not audit the sources (the three unchecked DOIs get "a visible "DOI not yet checked" marker, or come off the slide"), and no non-author runs the figure check.
