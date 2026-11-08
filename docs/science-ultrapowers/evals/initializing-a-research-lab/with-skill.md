# With the skill (Haiku 5.5)

The baseline passed 1 of 7. The skill took four iterations; the record keeps each one, with the skill file each run read.

| Iteration | Runs | Result | What changed after it |
|---|---|---|---|
| 1 | [A](runs/with-skill-A.md), [B](runs/with-skill-B.md) | A 7/7; B 6/7 | B did not run `--permissions` ("I also have no approved domain list"), so no literature rules reached your human partner. The skill now says `--permissions` carries the lab's own rule list and prints the rules when `.claude/settings.json` exists. |
| 2 | [C](runs/with-skill-C.md), [D](runs/with-skill-D.md) | C 6/7; D 7/7 | C named no file for the lab section ("instructions section"), the gap the baseline failed on. The overview now names the root `CLAUDE.md`, or `.claude/CLAUDE.md` when that is the only one. D planned to "drop any plan line that touches an existing file", which the script cannot do: the go-ahead rule now says what to do with a plan that holds more than the request. |
| 3 | [E](runs/with-skill-E.md), [F](runs/with-skill-F.md) | 7/7 and 7/7 | F applied nothing: it read "the plan only if it holds nothing beyond the request and this skill" as "the request held refused parts, so write nothing". The rule now reads "covers it when the plan holds only what was asked for; refusing part of a request never blocks the rest". |
| 4 | [G](runs/with-skill-G.md) | 7/7 | The final review asked for the trigger "older than the plugin" to have a step: the overview now says "A re-run after a plugin update adds what is new", and the list of `science` ids was dropped (the plan shows them). |
| 5 (after the final-review fixes) | [H](runs/with-skill-H.md) | 7/7 | None. H still writes "I drop that part" for a plan that holds more than the request; it applies the plan as shown, so the rule holds. |

What every with-skill run did, against the seven criteria:

1. A dry run first, the plan shown word for word, then `--yes` (A and F wait for a yes to the plan; G applies it under the go-ahead, "only if the plan holds just the lab files, the seven science connectors and the printed permission rules").
2. The key in no file and on no command line; `TYPESAFE_API_KEY` set by your human partner or through the environment script's hidden input; "The key was pasted into chat, so it should be rotated" (G).
3. No rule for python. From iteration 2 on, every run passes `--permissions`, expects `.claude/settings.json` to be skipped, and hands over the printed rules.
4. The `science` set in `.mcp.json`; the `account` connectors through `/mcp` sign-in; the `bundled` ones Claude Science only.
5. "I move and delete nothing under .claude" (G); the three duplicates listed for removal by hand.
6. "The lab section goes into .claude/CLAUDE.md, since there is no root CLAUDE.md" (G).
7. The migration offered as `science-ultrapowers:migrating-from-claude-science`; the data folder never copied.

Runs E, F, G and H also mention MCP servers that failed to connect. That line comes from the session's own harness context (README, item 8), not from the scenario, and it is not graded.

## After the pre-release review fixes

| Iteration | Runs | Result | What changed after it |
|---|---|---|---|
| 6 (Optuna opt-in, readable dry run, permissions snippet, lab.json merge, `--out-of-scope`) | [I](runs/with-skill-I.md) | 7/7 | None. I leaves Optuna out because the brief names no hyper-parameter study, runs the environment script as a dry run only, and hands the permissions snippet over for a manual merge. It names the `account` and `bundled` connectors as left out without restating why; the skill still says why. |

## After the terminology standard (0.2.0)

| Iteration | Runs | Result | What changed after it |
|---|---|---|---|
| 7 (the prompt reworded only in the old terms, task and pass criteria unchanged; Haiku 5.5) | [J](runs/with-skill-J.md) | 7/7 | None. PASS (dry run first and the plan read; the key written nowhere, TYPESAFE_API_KEY named and rotation advised; no Bash rule, settings.json untouched, the WebFetch snippet handed over; only mcp connectors in .mcp.json, account ones after /mcp sign-in, bundled ones Claude Science only; nothing deleted under .claude, the three copies named; the lab section in .claude/CLAUDE.md; the migration skill offered) |
