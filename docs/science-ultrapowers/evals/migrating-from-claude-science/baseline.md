# Baseline (no skill, Haiku 5.5): fail, 4 of 7

[Run](runs/baseline.md).

1. Pass. "Use the migration script, not sqlite3 on operon-cli.db."
2. Pass. "Set up the lab: run init_lab.py ... against C:/work/soil-microbiome/research_lab."
3. Pass. It lists the projects first and names "Soil microbiome resistome".
4. Fail. "--dry-run is skipped as requested."
5. Fail. "Write .env with a script that reads the secrets table without printing values." That reads an encrypted table and copies the values into a file.
6. Pass. "Agent profiles: NOT rewritten in the plugin."
7. Fail. It never commits `research_lab/` and never mentions `git lfs push`.
