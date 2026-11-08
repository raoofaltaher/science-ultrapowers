# PLAN-08: Release 0.1.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use ultrapowers:subagent-driven-development (recommended) or ultrapowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the plugin installable from a public GitHub marketplace and prove the Definition of done: validation passes, the README documents install, init, migrate, the team, the stores and the connectors, and the three acceptance scenarios have transcripts.

**Architecture:** Documentation and assets, `claude plugin validate`, repository hygiene (`.gitignore`), the public remote, a marketplace install into a fresh folder, then the three acceptance runs recorded under `docs/science-ultrapowers/evals/acceptance/`.

**Tech Stack:** `claude` CLI, `gh` CLI, git, Markdown, hand-written SVG, Python stdlib for a PNG.

**Spec:** `specs/2026-11-07-science-ultrapowers-design.md` — Definition of done 1-6, Testing "Acceptance", Constraints (install scope, public repository).

**Sources:** Claude Code plugin install reference (https://code.claude.com/docs/en/plugins/install.md: `/plugin marketplace add owner/repo`, `/plugin install name@marketplace`, `claude plugin install name@marketplace --scope project`, private repos through existing git credentials), host-marketplace reference (https://code.claude.com/docs/en/plugins/host-marketplace.md: `gh auth setup-git` for background updates, keep plugin files out of LFS, `version` drives updates), manifest reference (`claude plugin validate <path>`, `--strict`), all read 2026-11-07. Not checked: none.

## Global Constraints

- PLAN-01 Global Constraints apply.
- Repository `raoofaltaher/science-ultrapowers`, public, source-available under the ultrapowers-style licence (`LICENSE`), default branch `main`; no LFS in this repository.
- Install path documented as project scope first: `claude plugin install science-ultrapowers@science-ultrapowers --scope project`.
- No third-party logo in the assets.

## Review Focus

1. A fresh machine without `jq` cannot run `bump-version.sh --check`: the README lists `jq` under development requirements only, and the runtime requirements as Git for Windows, Python 3.11+, node 22+.
2. A private fork of the marketplace whose credential helper is missing never auto-updates: README's install section includes `gh auth setup-git`.
3. `claude plugin validate --strict` may warn on fields the docs call recent; Task 2 records the exact output and fixes every error, keeping warnings only when the doc says they are informational.
4. The acceptance test in the source-project repo touches a live research project: Task 5 runs `migrate` only after `--dry-run` matches PLAN-07's pinned counts, commits only `research_lab/`, and nothing else.
5. The session that runs the acceptance tests has this plugin installed from a local path as well as from the marketplace; Task 4 uninstalls the local one first so the marketplace copy is what runs.

---

### Task 1: README, release notes, assets, `.gitignore`

**Files:**
- Modify: `README.md`, `RELEASE-NOTES.md`, `LICENSE`, `.gitignore`
- Create: `assets/science-ultrapowers-small.svg`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`, `.github/pull_request_template.md`
- Already in place since PLAN-01: `.claude-plugin/icon.png` (512×512 listing icon), `.gitignore`, a README stub with the install commands

- [ ] **Step 1: Write `README.md`**

Sections: title and one-paragraph description (a research-lab methodology for Claude Code; fourteen roles; gates G0-G6; the evidence rule; versioned artifacts; lab memory; migration from Claude Science); "Built from obra/superpowers v7.0.2 (MIT) as the template; see LICENSE" (the attribution line the gate exempts); **Install** (register the marketplace, install at project scope, `gh auth setup-git` for private auto-update, requirements: Git for Windows or bash, Python 3.11+, node 22+, git-lfs for project stores; `jq` for development); **Start a lab** (`initializing-a-research-lab`: what it asks, what it writes, the connectors, `/mcp`); **Continue from Claude Science** (`migrating-from-claude-science`: what is imported, what is not, the report); **The team** (table: role, agent, owns); **How a session runs** (kickoff, briefs, hand-offs, orchestrator saves and commits `research_lab/`, stand-up); **The stores** (artifact store layout and the `artifacts.py` verbs; memory store layout, gate, lint, hooks; LFS rule); **Skills** (lab skills, kept engineering skills, vendored third-party skills with licences); **Connectors** (the catalogue: science set, other set, account connectors, not-portable bundled servers); **Testing** (`bash tests/claude-code/run-tests.sh`); **Licence**.

- [ ] **Step 2: Release notes and assets**

`RELEASE-NOTES.md`: `## 0.1.0` with the date and ten bullets, one per shipped unit. `assets/science-ultrapowers-small.svg`: a 420×80 hand-written SVG with the word mark `science-ultrapowers` and the same flask glyph as `.claude-plugin/icon.png` (indigo `#2d0789`, violet `#8e09fa`, white), no external fonts. Do not recreate the PNG icon: `claude plugin validate --strict` already finds it.

- [ ] **Step 3: `.gitignore`**

Already written in PLAN-01; confirm it still lists `.claude/`, `__pycache__/`, `*.pyc`, `node_modules/`, `.DS_Store`, and add nothing unless a later plan created a new generated folder.

- [ ] **Step 4: Repository documents**

Add the files a public, source-available repository carries: `LICENSE` (the ultrapowers-style licence, adapted: section 6 says no earlier release exists; section 7 lists superpowers v7.0.2 under MIT and the fourteen vendored skills with their own licences), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, the `.github/` issue and pull-request templates, and the README banner and links the owner asked for.

- [ ] **Step 5: Gate and commit**

Run: `bash tests/claude-code/run-tests.sh && git add README.md RELEASE-NOTES.md LICENSE CONTRIBUTING.md CODE_OF_CONDUCT.md .github assets .gitignore && git commit -m "docs: README, release notes 0.1.0, licence, community files, assets and ignore rules"`

### Task 2: Validate the plugin

- [ ] **Step 1: Run the validator**

Run: `claude plugin validate . && claude plugin validate . --strict`
Expected: `valid`; record the full output in `docs/science-ultrapowers/evals/validate-0.1.0.txt`. Fix every error; for each warning note whether the docs call it informational.

- [ ] **Step 2: Commit**

Run: `git add docs/science-ultrapowers/evals/validate-0.1.0.txt && git commit -m "test: record claude plugin validate output for 0.1.0"`

### Task 3: Public remote

- [ ] **Step 0: Squash the sanitised history into one commit**

Confirm `.gitignore` lists `/.ultrapowers/` and that `bash tests/claude-code/run-tests.sh` passes on the tree, `specs/` and `plans/` included (the gate scans them for private strings). Merge `dev` into `main` first: `git switch main && git merge dev`. Keep the build history on a local branch that is never pushed: `git branch dev-history main`. Then collapse `main` to one initial commit: `git checkout --orphan release && git commit -m "science-ultrapowers 0.1.0" && git branch -D main && git branch -m main`. The squash happens before `gh repo create --push`, so the remote only ever holds the one commit.

- [ ] **Step 1: Create the repository and push**

Run: `gh repo create raoofaltaher/science-ultrapowers --public --source . --remote origin --push`
Expected: `https://github.com/raoofaltaher/science-ultrapowers` exists, public; `git ls-remote origin` lists `main` only (not `dev` or `dev-history`) and returns the current commit.

- [ ] **Step 1b: Repository metadata**

Run: `gh repo edit raoofaltaher/science-ultrapowers --description "A research-lab methodology for Claude Code: fourteen research roles, stage gates G0-G6, a DOI-verified evidence rule, a versioned artifact store and lab memory, with migration from Claude Science" --homepage https://raoofaltaher.com --enable-discussions --enable-wiki=false --add-topic ai --add-topic ai-agents --add-topic ai-skills --add-topic claude-code --add-topic claude-code-plugin --add-topic research --add-topic science --add-topic research-lab --add-topic reproducibility --add-topic evidence --add-topic literature-review --add-topic plugin --add-topic marketplace --add-topic subagents`
Expected: the README's eleven Discussions links resolve (the default categories q-a, ideas and show-and-tell exist once Discussions is on); `gh repo view --json description,homepageUrl,repositoryTopics,hasDiscussionsEnabled` shows the values.

- [ ] **Step 2: Tag and release**

Run: `git tag v0.1.0 && git push origin v0.1.0 && gh release create v0.1.0 --title "science-ultrapowers 0.1.0" --notes-file <(awk '/^## 0.1.0/{f=1; next} /^## /{f=0} f' RELEASE-NOTES.md)`
Expected: `gh release view v0.1.0` shows the release, so the README's release badge reads `0.1.0`, not `none`.

### Task 4: Marketplace install into a fresh folder

- [ ] **Step 1: Remove any local-path install of this plugin**

Run inside a Claude Code session: `/plugin` → uninstall `science-ultrapowers` if present from a local marketplace; `/reload-plugins`.

- [ ] **Step 2: Install from the marketplace**

Run: `/plugin marketplace add raoofaltaher/science-ultrapowers`, then in a fresh empty folder `<smoke-folder>`: `claude plugin install science-ultrapowers@science-ultrapowers --scope project`.
Expected: `.claude/settings.json` in `<smoke-folder>` lists the plugin; a new session there shows the bootstrap (ask: "what skills do you have?" and expect `running-the-lab` among them). Save the session transcript excerpt as `docs/science-ultrapowers/evals/acceptance/00-install.md`.

### Task 5: The three acceptance runs

**Files:**
- Create: `docs/science-ultrapowers/evals/acceptance/01-fresh-lab.md`, `02-source-project-kickoff.md`, `03-artifact-question.md`

- [ ] **Step 1: Fresh lab**

In `<smoke-folder>`, a new session, message: `Let's start the lab for my paper on X`. Pass: `initializing-a-research-lab` runs before any file is written, asks its questions, shows the plan, writes after yes. Save the transcript.

- [ ] **Step 2: Source-project migrate and kickoff**

In `<host-project>` with the plugin installed at project scope: run `init` (expect duplicate warnings for `.claude/agents` and `.claude/skills`, nothing else changed under `.claude/`), run `migrate --dry-run`, compare with PLAN-07's pinned counts, then `migrate`; commit `research_lab/` as the skill says. New session, message: `Lab, where do we stand?` Pass: a kickoff that cites the last stand-up note, the open tasks, open access requests and at least one imported memory. Save the transcript.

- [ ] **Step 3: Artifact question**

Same repo, message: `What is RV-0048 based on, and what is still unaddressed on it?` Pass: the answer comes from `artifacts.py lineage` / `check list` (inputs include the ELU PDF and the registry proposal files; outstanding checks listed), not from reading the Markdown alone. Save the transcript.

- [ ] **Step 4: Commit the transcripts and finish**

Run: `git add docs/science-ultrapowers/evals/acceptance && git commit -m "test: acceptance transcripts for 0.1.0" && git push`
Expected: Definition of done 1-6 all hold; report each with its evidence to your human partner.
