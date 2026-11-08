"""The terminology rename: archive path, provenance, --task, reviewer findings, milestone and working.

Each new name works, each old name still works as a hidden alias, each legacy value is read
and reported with the new word, and an old-layout lab exits 2 with the exact message."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import artifacts
from _helpers import make_git_lab, make_lab, run_cli, write_file

SCRIPT = Path(__file__).resolve().parents[1] / "artifacts.py"
OLD_LAYOUT = "this lab uses the 0.1 layout; run science-ultrapowers:initializing-a-research-lab to migrate it"
FINDING_FIELDS = [
    "id", "version_id", "claim", "verdict", "severity", "evidence", "rebuttal",
    "reviewer_role", "status", "resolution", "created_at", "source_ref",
]


class RenameTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self._tmp.cleanup)
        self.t = Path(self._tmp.name)

    def _store(self, git: bool = False):
        lab = make_git_lab(self.t) if git else make_lab(self.t)
        s = artifacts.LabStore(lab)
        return s, s.project_root

    def _saved(self, git: bool = False):
        s, proj = self._store(git)
        r = s.save([write_file(proj / "f1.txt", "one")], role="r", task="TASK-0001")[0]
        return s, proj, r

    def _finding(self, s, r, **extra):
        row = dict.fromkeys(FINDING_FIELDS)
        row.update(
            id="abcdef0001", version_id=r["version_id"], claim="x", verdict="fail",
            reviewer_role="rev", status="open", created_at=artifacts.now_iso(),
        )
        row.update(extra)
        s.append("verification_checks", row)
        return row["id"]


class ArchivePathTest(RenameTestBase):
    def test_saves_land_in_the_archive(self):
        s, proj, r = self._saved()
        self.assertEqual(r["storage_path"], f"artifacts/archive/{r['artifact_id']}/v001_f1.txt")
        self.assertTrue((s.lab / "artifacts" / "archive" / r["artifact_id"] / "v001_f1.txt").is_file())
        self.assertFalse((s.lab / "artifacts" / "store").exists())

    def test_gitattributes_names_the_archive(self):
        s, proj, r = self._saved()
        lines = (s.root / ".gitattributes").read_text(encoding="utf-8").split("\n")
        self.assertIn("archive/** -text", lines)
        self.assertNotIn("store/** -text", lines)
        self.assertIn("artifact archive", lines[0])

    def test_a_migrated_row_with_the_old_storage_path_is_read_from_the_archive(self):
        s, proj, r = self._saved()
        rows = s.rows("versions")
        rows[0]["storage_path"] = f"artifacts/store/{r['artifact_id']}/v001_f1.txt"  # legacy
        s.rewrite("versions", rows)
        self.assertEqual(s.path(r["version_id"]), s.lab / "artifacts" / "archive" / r["artifact_id"] / "v001_f1.txt")
        self.assertEqual(s.locate(r["version_id"])["status"], "ok")

    def test_messages_say_archive_and_table(self):
        s, proj, r = self._saved()
        rows = s.rows("versions")
        rows[0]["storage_path"] = "artifacts/archive/../../../outside.txt"
        s.rewrite("versions", rows)
        with self.assertRaises(artifacts.StoreError) as cm:
            s.path(r["version_id"])
        self.assertIn("outside the archive", str(cm.exception))
        with self.assertRaises(artifacts.StoreError) as cm:
            s.rows("no_such_table")
        self.assertIn("unknown table", str(cm.exception))


class OldLayoutTest(RenameTestBase):
    def _assert_exit_2(self, lab):
        code, out, err = run_cli(["--lab", str(lab), "search"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertEqual(err.strip(), OLD_LAYOUT)

    def test_a_store_folder_without_an_archive_is_the_old_layout(self):
        lab = make_lab(self.t)
        (lab / "artifacts" / "store").mkdir(parents=True)
        self._assert_exit_2(lab)
        with self.assertRaises(artifacts.OldLayout):
            artifacts.LabStore(lab)

    def test_a_numbered_folder_without_an_archive_is_the_old_layout(self):
        lab = make_lab(self.t)
        (lab / "02_findings_ledger").mkdir()
        self._assert_exit_2(lab)

    def test_exits_2_for_every_subcommand(self):
        lab = make_lab(self.t)
        (lab / "artifacts" / "store").mkdir(parents=True)
        for argv in (["save", "x", "--role", "r", "--task", "t"], ["provenance", "abcdef"],
                     ["findings", "list"], ["lfs-check"]):
            code, out, err = run_cli(["--lab", str(lab), *argv])
            self.assertEqual((code, err.strip()), (2, OLD_LAYOUT), argv)

    def test_an_archive_beside_numbered_folders_is_not_old(self):
        lab = make_lab(self.t)
        (lab / "02_findings_ledger").mkdir()
        (lab / "artifacts" / "archive").mkdir(parents=True)
        code, out, err = run_cli(["--lab", str(lab), "search"])
        self.assertEqual((code, json.loads(out)), (0, []))

    def test_a_new_lab_is_not_old(self):
        lab = make_lab(self.t)
        code, out, err = run_cli(["--lab", str(lab), "search"])
        self.assertEqual((code, json.loads(out)), (0, []))


class ProvenanceTest(RenameTestBase):
    def test_provenance_verb(self):
        s, proj, r = self._saved()
        code, out, err = run_cli(["--lab", str(s.lab), "provenance", r["version_id"]])
        self.assertEqual(code, 0, err)
        self.assertEqual(set(json.loads(out)), {"version", "artifact", "inputs", "findings"})

    def test_lineage_still_works_as_a_hidden_alias(self):
        s, proj, r = self._saved()
        lab = str(s.lab)
        new = run_cli(["--lab", lab, "provenance", r["version_id"]])
        old = run_cli(["--lab", lab, "lineage", r["version_id"]])
        self.assertEqual(old, new)
        self.assertEqual(old[0], 0)

    def test_python_alias(self):
        s, proj, r = self._saved()
        self.assertEqual(s.lineage(r["version_id"]), s.provenance(r["version_id"]))


class HiddenAliasHelpTest(RenameTestBase):
    def _help(self, *args):
        out = subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--help"], capture_output=True, text=True, encoding="utf-8"
        )
        self.assertEqual(out.returncode, 0, out.stderr)
        return out.stdout

    def test_top_level_help_names_the_new_verbs_only(self):
        text = self._help()
        for shown in ("provenance", "findings", "respond", "archive"):
            self.assertIn(shown, text)
        for hidden in ("lineage", "mark-addressed", "  check "):
            self.assertNotIn(hidden, text)
        self.assertNotRegex(text, r"store")

    def test_save_help_names_task_not_command_or_the_old_destinations(self):
        text = self._help("save")
        self.assertIn("--task", text)
        self.assertNotIn("--command", text)
        self.assertIn("milestone", text)
        self.assertNotIn("snapshot", text)
        self.assertNotIn("working_data", text)

    def test_findings_help_names_the_new_statuses(self):
        text = self._help("findings", "review")
        self.assertIn("closed", text)
        self.assertIn("re-opened", text)
        self.assertNotIn("unaddressed", text)
        self.assertNotIn("resolved", text)

    def test_link_help_names_task(self):
        text = self._help("link")
        self.assertIn("--task", text)
        self.assertNotIn("--command", text)


class TaskFlagTest(RenameTestBase):
    def test_task_flag_is_stored_under_the_same_ledger_key(self):
        s, proj = self._store()
        f = write_file(proj / "a.md", "a\n")
        code, out, err = run_cli(["--lab", str(s.lab), "save", str(f), "--role", "r", "--task", "TASK-0007", "--no-stage"])
        self.assertEqual(code, 0, err)
        self.assertEqual(s.rows("versions")[0]["producing_command"], "TASK-0007")

    def test_command_flag_is_a_hidden_alias(self):
        s, proj = self._store()
        f = write_file(proj / "a.md", "a\n")
        code, out, err = run_cli(["--lab", str(s.lab), "save", str(f), "--role", "r", "--command", "pytest", "--no-stage"])
        self.assertEqual(code, 0, err)
        self.assertEqual(s.rows("versions")[0]["producing_command"], "pytest")

    def test_link_takes_both_forms(self):
        s, proj = self._store()
        a = write_file(proj / "a.csv", "a\n")
        b = write_file(proj / "b.csv", "b\n")
        self.assertEqual(run_cli(["--lab", str(s.lab), "link", str(a), "--role", "r", "--task", "TASK-0002", "--no-stage"])[0], 0)
        self.assertEqual(run_cli(["--lab", str(s.lab), "link", str(b), "--role", "r", "--command", "old", "--no-stage"])[0], 0)
        self.assertEqual([v["producing_command"] for v in s.rows("versions")], ["TASK-0002", "old"])

    def test_one_of_the_two_is_required(self):
        s, proj = self._store()
        f = write_file(proj / "a.md", "a\n")
        code, out, err = run_cli(["--lab", str(s.lab), "save", str(f), "--role", "r"])
        self.assertEqual(code, 2)
        self.assertIn("--task", err)

    def test_python_keyword_alias(self):
        s, proj = self._store()
        f = write_file(proj / "a.md", "a\n")
        s.save([f], role="r", command="pytest")
        self.assertEqual(s.rows("versions")[0]["producing_command"], "pytest")
        with self.assertRaises(artifacts.StoreError):
            s.save([write_file(proj / "b.md", "b\n")], role="r")


class FindingsTest(RenameTestBase):
    def _cli(self, s, *argv):
        return run_cli(["--lab", str(s.lab), *argv])

    def test_findings_add_list_review_respond(self):
        s, proj, r = self._saved()
        code, out, err = self._cli(
            s, "findings", "add", "--version", r["version_id"], "--claim", "FND-0001 holds?",
            "--verdict", "fail", "--reviewer", "rev",
        )
        self.assertEqual(code, 0, err)
        row = json.loads(out)
        self.assertEqual(row["status"], "open")
        cid = row["id"]
        code, out, err = self._cli(s, "findings", "list")
        self.assertEqual([c["id"] for c in json.loads(out)], [cid])
        code, out, err = self._cli(s, "respond", cid, "--note", "recomputed")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["status"], "author-responded")
        self.assertEqual(s.rows("verification_checks")[0]["status"], "author-responded")
        code, out, err = self._cli(s, "findings", "review", cid, "--status", "re-opened", "--reviewer", "rev")
        self.assertEqual(json.loads(out)["status"], "re-opened")
        self.assertEqual(s.rows("verification_checks")[0]["status"], "re-opened")
        self._cli(s, "respond", cid, "--note", "again")
        code, out, err = self._cli(s, "findings", "review", cid, "--status", "closed", "--reviewer", "rev")
        self.assertEqual(json.loads(out)["status"], "closed")
        self.assertEqual(s.rows("verification_checks")[0]["status"], "closed")
        self.assertEqual(self._cli(s, "findings", "list")[1].strip(), "[]")

    def test_old_verbs_still_work(self):
        s, proj, r = self._saved()
        code, out, err = self._cli(
            s, "check", "add", "--version", r["version_id"], "--claim", "c", "--verdict", "warn", "--reviewer", "rev",
        )
        self.assertEqual(code, 0, err)
        cid = json.loads(out)["id"]
        self.assertEqual(len(json.loads(self._cli(s, "check", "list")[1])), 1)
        code, out, err = self._cli(s, "mark-addressed", cid, "--note", "n")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["status"], "author-responded")
        code, out, err = self._cli(s, "check", "review", cid, "--status", "unaddressed", "--reviewer", "rev")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["status"], "re-opened")
        code, out, err = self._cli(s, "check", "review", cid, "--status", "resolved", "--reviewer", "rev")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["status"], "closed")
        self.assertEqual(s.rows("verification_checks")[0]["status"], "closed")

    def test_legacy_statuses_are_reported_with_the_new_word(self):
        s, proj, r = self._saved()
        ids = {
            "claimed": self._finding(s, r, id="aaaaaa0001", status="claimed"),
            "unaddressed": self._finding(s, r, id="aaaaaa0002", status="unaddressed"),
            "resolved": self._finding(s, r, id="aaaaaa0003", status="resolved"),
        }
        code, out, err = self._cli(s, "findings", "list", "--all")
        self.assertEqual(code, 0, err)
        reported = {c["id"]: c["status"] for c in json.loads(out)}
        self.assertEqual(reported, {
            ids["claimed"]: "author-responded", ids["unaddressed"]: "re-opened", ids["resolved"]: "closed",
        })
        # a read does not rewrite the file
        self.assertEqual([c["status"] for c in s.rows("verification_checks")], ["claimed", "unaddressed", "resolved"])
        # only the re-opened one is outstanding
        code, out, err = self._cli(s, "findings", "list")
        self.assertEqual([c["id"] for c in json.loads(out)], [ids["unaddressed"]])
        self.assertEqual([c["status"] for c in json.loads(out)], ["re-opened"])

    def test_a_legacy_unaddressed_finding_can_receive_a_response(self):
        s, proj, r = self._saved()
        cid = self._finding(s, r, status="unaddressed")
        self.assertEqual(s.respond(cid, "fixed")["status"], "author-responded")

    def test_a_legacy_resolved_finding_is_closed(self):
        s, proj, r = self._saved()
        cid = self._finding(s, r, status="resolved")
        with self.assertRaises(artifacts.StoreError) as cm:
            s.finding_review(cid, status="closed", reviewer_role="rev")
        self.assertIn("already closed", str(cm.exception))
        with self.assertRaises(artifacts.StoreError) as cm:
            s.respond(cid, "x")
        self.assertIn("only open or re-opened", str(cm.exception))

    def test_a_legacy_review_status_inside_the_resolution_is_reported_new(self):
        s, proj, r = self._saved()
        cid = self._finding(
            s, r, status="unaddressed",
            resolution={"note": "n", "review": {"status": "unaddressed", "by": "rev", "note": None, "at": "x"}},
        )
        got = [c for c in s.findings() if c["id"] == cid][0]
        self.assertEqual(got["resolution"]["review"]["status"], "re-opened")

    def test_review_accepts_only_closed_or_reopened(self):
        s, proj, r = self._saved()
        c = s.finding_add(r["version_id"], claim="c", verdict="warn", reviewer_role="rev")
        with self.assertRaises(artifacts.StoreError) as cm:
            s.finding_review(c["id"], status="open", reviewer_role="rev")
        self.assertIn("closed or re-opened", str(cm.exception))

    def test_python_aliases(self):
        s, proj, r = self._saved()
        c = s.check_add(r["version_id"], claim="c", verdict="warn", reviewer_role="rev")
        self.assertEqual(s.mark_addressed(c["id"], "n")["status"], "author-responded")
        self.assertEqual(s.check_review(c["id"], status="resolved", reviewer_role="rev")["status"], "closed")
        self.assertEqual(len(s.checks()), 1)

    def test_messages_say_reviewer_finding(self):
        s, proj, r = self._saved()
        with self.assertRaises(artifacts.StoreError) as cm:
            s.finding_add(r["version_id"], claim=" ", verdict="warn", reviewer_role="rev")
        self.assertEqual(str(cm.exception), "a reviewer finding needs a claim")
        with self.assertRaises(artifacts.StoreError) as cm:
            s.finding_add(r["version_id"], claim="c", verdict="warn", reviewer_role="")
        self.assertEqual(str(cm.exception), "a reviewer finding needs a reviewer role")
        with self.assertRaises(artifacts.UnknownId) as cm:
            s.respond("ffffff", "x")
        self.assertIn("unknown reviewer finding", str(cm.exception))
        c = s.finding_add(r["version_id"], claim="c", verdict="warn", reviewer_role="rev")
        with self.assertRaises(artifacts.StoreError) as cm:
            s.respond(c["id"], "  ")
        self.assertIn("respond needs a note", str(cm.exception))

    def test_provenance_reports_findings_with_new_words(self):
        s, proj, r = self._saved()
        self._finding(s, r, status="claimed")
        got = s.provenance(r["version_id"])["findings"]
        self.assertEqual([c["status"] for c in got], ["author-responded"])


class DestinationTest(RenameTestBase):
    def _cli_save(self, s, f, *extra):
        return run_cli(["--lab", str(s.lab), "save", str(f), "--role", "r", "--task", "TASK-0001", "--no-stage", *extra])

    def test_milestone_and_working_are_written(self):
        s, proj = self._store()
        f = write_file(proj / "a.md", "a\n")
        self.assertEqual(self._cli_save(s, f, "--destination", "working")[0], 0)
        self.assertEqual(s.rows("versions")[0]["destination"], "working")
        self.assertEqual(s.rows("artifacts")[0]["destination"], "working")
        g = write_file(proj / "b.md", "b\n")
        self.assertEqual(self._cli_save(s, g, "--destination", "milestone")[0], 0)
        self.assertEqual(s.rows("versions")[1]["destination"], "milestone")

    def test_default_is_milestone(self):
        s, proj, r = self._saved()
        self.assertEqual(s.rows("versions")[0]["destination"], "milestone")
        self.assertEqual(s.rows("artifacts")[0]["destination"], "milestone")

    def test_legacy_values_are_accepted_and_written_as_new_words(self):
        s, proj = self._store()
        f = write_file(proj / "a.md", "a\n")
        self.assertEqual(self._cli_save(s, f, "--destination", "working_data")[0], 0)
        self.assertEqual(s.rows("versions")[0]["destination"], "working")
        g = write_file(proj / "b.md", "b\n")
        self.assertEqual(self._cli_save(s, g, "--destination", "snapshot")[0], 0)
        self.assertEqual(s.rows("versions")[1]["destination"], "milestone")

    def test_an_unknown_destination_is_refused(self):
        s, proj = self._store()
        f = write_file(proj / "a.md", "a\n")
        code, out, err = self._cli_save(s, f, "--destination", "nowhere")
        self.assertEqual(code, 2)
        self.assertIn("milestone", err)
        with self.assertRaises(artifacts.StoreError) as cm:
            s.save([f], role="r", task="t", destination="nowhere")
        self.assertIn("milestone or working", str(cm.exception))

    def test_a_legacy_working_row_is_replaced_by_the_next_working_save(self):
        s, proj = self._store()
        f = write_file(proj / "state.json", "1\n")
        r1 = s.save([f], role="r", task="t", destination="working")[0]
        rows = s.rows("versions")
        rows[0]["destination"] = "working_data"
        s.rewrite("versions", rows)
        arts = s.rows("artifacts")
        arts[0]["destination"] = "working_data"
        s.rewrite("artifacts", arts)
        f.write_text("2\n", encoding="utf-8")
        r2 = s.save([f], role="r", task="t", version_of=r1["artifact_id"])[0]  # sticky: inherits the old working value
        self.assertEqual(s.rows("versions")[-1]["destination"], "working")
        old = [v for v in s.rows("versions") if v["id"] == r1["version_id"]][0]
        self.assertEqual(old["status"], "replaced")
        self.assertFalse((s.lab / r1["storage_path"]).exists())
        self.assertTrue((s.lab / r2["storage_path"]).is_file())
        with self.assertRaises(artifacts.StoreError) as cm:
            s.locate(r1["version_id"])
        self.assertIn("working save", str(cm.exception))

    def test_a_legacy_snapshot_row_is_kept(self):
        s, proj = self._store()
        f = write_file(proj / "state.json", "1\n")
        r1 = s.save([f], role="r", task="t")[0]
        rows = s.rows("versions")
        rows[0]["destination"] = "snapshot"
        s.rewrite("versions", rows)
        f.write_text("2\n", encoding="utf-8")
        s.save([f], role="r", task="t", version_of=r1["artifact_id"], destination="working")
        first = [v for v in s.rows("versions") if v["id"] == r1["version_id"]][0]
        self.assertEqual(first["status"], "ok")
        self.assertTrue((s.lab / r1["storage_path"]).is_file())


if __name__ == "__main__":
    unittest.main()
