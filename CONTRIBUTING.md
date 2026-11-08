# Contributing

Thank you for helping improve science-ultrapowers.

This repository is source-available, not open source. The code is public so you can see what you install, but every right in it belongs to the repository owner. Read [LICENSE](LICENSE): you may install the plugin in Claude Code and use it, and nothing else.

## How you can help

- **Report a bug.** Open an issue with the [bug report template](https://github.com/raoofaltaher/science-ultrapowers/issues/new/choose).
- **Request a feature or a change.** Open an issue with the feature request template. Describe the problem you hit in your lab, not a patch.
- **Ask a question or start a discussion.** Use [Discussions](https://github.com/raoofaltaher/science-ultrapowers/discussions): [Q&A](https://github.com/raoofaltaher/science-ultrapowers/discussions/new?category=q-a) for help, [Ideas](https://github.com/raoofaltaher/science-ultrapowers/discussions/new?category=ideas) for suggestions, [Show and tell](https://github.com/raoofaltaher/science-ultrapowers/discussions/new?category=show-and-tell) for what your lab built with it.

Ideas and reports submitted in issues and discussions may be used by the repository owner freely, as section 3 of the license sets out.

## What is not accepted

- Pull requests, patches or code from anyone other than the repository owner. They are closed without review (license, section 3).
- Forks, copies, mirrors or modified versions of the plugin published elsewhere.

## Writing a good report

A report is easiest to act on when it names:

- the plugin version (`.claude-plugin/plugin.json`) and the Claude Code version (`claude --version`);
- your operating system and shell;
- the skill or agent involved, and the message you sent;
- what you expected, and which rule in the skill or in `AGENTS.md` was not followed;
- a short transcript excerpt.

Search open and closed issues first. Never paste secrets, lab records, unpublished data or personal data into an issue or a discussion. Remove them from every excerpt before you post it.

## What a skill is

A skill is a markdown file that shapes how an agent behaves, so a wording change is a behavior change. Binding rules, rationalization tables and warning signs in the skills are deliberate devices. A skill's `description` says only when to use it ("Use when..."), never its workflow. Skills name actions, not tool names, and refer to each other as `science-ultrapowers:<skill>`. "The researcher" is deliberate terminology for the person who runs the lab.

Five track skills (idea, literature, review, writing and dissemination), with the study track in `running-the-lab`, enter one lifecycle of seven stages at the stage that fits.

For this reason no skill is added or changed without a pressure test: a baseline run without the change, a run with it, and a grading of both. `science-ultrapowers:writing-skills` describes the method, and the transcripts so far are under `docs/science-ultrapowers/evals/`. A report that quotes a session where a skill failed under pressure is the most useful kind.

## The terminology standard

Every text in the plugin follows `docs/science-ultrapowers/terminology.md`: its writing rules, its controlled dictionary and its American spelling. A contribution that uses a term from its not-approved list, a stage code or a British spelling does not follow it. `tests/claude-code/test-terminology.sh` enforces the lists.

## Rules for maintainers

These rules apply to the repository owner's own work. [AGENTS.md](AGENTS.md) holds the full contributor guide.

- Runtime dependencies are bash, node 22 or later and the Python 3.11 standard library. No pip packages and no Git Large File Storage (LFS).
- The plugin holds nothing project-specific and nothing that belongs to the tool it was migrated from. `tests/claude-code/test-no-foreign-harness.sh` enforces this.
- The repository owner's own project strings, which the disclosure check must never find in a tracked file, live in `tests/private-strings.txt`. That file is git-ignored; `tests/private-strings.example` shows its form.
- Nothing is ever written under `${CLAUDE_PLUGIN_ROOT}`, and there is no `CLAUDE.md` at the repository root.
- Versions change only through `scripts/bump-version.sh <version>`, with a matching `## <version>` heading at the top of `RELEASE-NOTES.md`. `scripts/bump-version.sh --check` reports drift.
- One problem per change.

## Running the tests (repository owner)

The license grants no right to clone the repository, so this section describes the repository owner's own checks. A reporter describes what a session did; the repository owner reproduces it here.

```
bash tests/claude-code/run-tests.sh
claude plugin validate . --strict
```

The first command runs every shell, Python and Node test. You need Git Bash, jq, node 22 or later and Python 3.11 or later. [docs/testing.md](docs/testing.md) lists what each test covers. A single file runs on its own, for example `bash tests/claude-code/test-version-sync.sh`.

## Windows

- Use Git for Windows; the scripts and hooks run under its bash.
- Git records new files as mode 100644 here, so stage every script and hook with `git add --chmod=+x`.
- `.gitattributes` keeps hooks and scripts on LF line endings. Do not convert them to CRLF.
- Hooks run through `hooks/run-hook.cmd`.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
