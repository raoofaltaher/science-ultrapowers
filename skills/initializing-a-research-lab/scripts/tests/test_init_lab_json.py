"""init_lab.py on a lab that already has a lab.json: the file is merged, never replaced, and only when a value changed."""

import json
import tempfile
import unittest
from pathlib import Path

from test_init_fresh import run_script

PLUGIN_JSON = Path(__file__).resolve().parents[4] / ".claude-plugin" / "plugin.json"
LAB_JSON = "research_lab/lab.json"


def plugin_version():
    return json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))["version"]


class LabJsonCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.proj = self.tmp / "proj"
        self.proj.mkdir()
        self.path = self.proj / "research_lab" / "lab.json"
        self.settings = self.proj / ".claude" / "settings.json"

    def run_init(self, *extra, yes=True):
        args = ["--project-root", str(self.proj), "--name", "Merge", *extra]
        if yes:
            args.append("--yes")
        args.append("--json")
        return run_script(args, self.tmp)

    def report(self, *extra, yes=True):
        result = self.run_init(*extra, yes=yes)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return json.loads(result.stdout)

    def data(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def edit(self, **changes):
        data = self.data()
        data.update(changes)
        self.path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


class TestLabJsonMerge(LabJsonCase):
    def test_rerun_merges_connectors_into_lab_json(self):
        self.report()
        self.edit(custom={"keep": True}, description="hand edited")
        again = self.report("--connectors", "pubmed")
        self.assertIn(LAB_JSON, again["append"])
        self.assertNotIn(LAB_JSON, again["skip"])
        self.assertEqual(self.data()["connectors"], ["pubmed"])
        later = self.report("--connectors", "firecrawl,optuna")
        self.assertIn(LAB_JSON, later["append"])
        data = self.data()
        self.assertEqual(data["connectors"], ["firecrawl", "pubmed", "optuna"])
        self.assertEqual(data["custom"], {"keep": True})
        self.assertEqual(data["description"], "hand edited")
        self.assertFalse([w for w in later["warn"] if "connectors list was not updated" in w], later["warn"])

    def test_rerun_keeps_a_connector_the_catalogue_does_not_know(self):
        self.report()
        self.edit(connectors=["somebody-elses", "pubmed"])
        self.report("--connectors", "firecrawl")
        self.assertEqual(self.data()["connectors"], ["firecrawl", "pubmed", "somebody-elses"])

    def test_rerun_records_a_connector_already_in_mcp_json(self):
        (self.proj / ".mcp.json").write_text(
            json.dumps({"mcpServers": {"pubmed": {"type": "http", "url": "https://example.invalid/mcp"}}}) + "\n",
            encoding="utf-8",
        )
        self.report()
        again = self.report("--connectors", "pubmed")
        self.assertIn(LAB_JSON, again["append"])
        self.assertEqual(self.data()["connectors"], ["pubmed"])

    def test_rerun_refreshes_plugin_version(self):
        self.report()
        self.edit(pluginVersion="0.0.1")
        before = self.data()
        again = self.report()
        self.assertIn(LAB_JSON, again["append"])
        after = self.data()
        self.assertEqual(after["pluginVersion"], plugin_version())
        before["pluginVersion"] = after["pluginVersion"]
        self.assertEqual(after, before)

    def test_lab_json_untouched_when_nothing_changes(self):
        self.report("--connectors", "pubmed")
        raw = self.path.read_text(encoding="utf-8")
        self.path.write_text(json.dumps(json.loads(raw), indent=4) + "\n", encoding="utf-8")
        before = self.path.read_bytes()
        again = self.report("--connectors", "pubmed")
        self.assertEqual(self.path.read_bytes(), before)
        self.assertIn(LAB_JSON, again["skip"])
        self.assertNotIn(LAB_JSON, again["append"] + again["create"] + again["written"])
        plan = json.loads(self.run_init("--connectors", "pubmed", yes=False).stdout)
        self.assertIn(LAB_JSON, plan["skip"])
        self.assertNotIn(LAB_JSON, plan["append"])

    def test_a_rewrite_keeps_the_files_indent(self):
        self.report()
        self.path.write_text(json.dumps(self.data(), indent=4) + "\n", encoding="utf-8")
        self.report("--connectors", "pubmed")
        lines = self.path.read_text(encoding="utf-8").splitlines()
        self.assertTrue(lines[1].startswith("    ") and not lines[1].startswith("     "), lines[1])
        self.assertEqual(self.data()["connectors"], ["pubmed"])

    def test_rerun_with_permissions_marks_them_written(self):
        self.report()
        self.assertFalse(self.data()["permissions"]["written"])
        again = self.report("--permissions")
        self.assertTrue(self.settings.is_file())
        self.assertIn(LAB_JSON, again["append"])
        self.assertTrue(self.data()["permissions"]["written"])
        self.assertFalse([w for w in again["warn"] if "permissions.written" in w], again["warn"])

    def test_permissions_stay_unwritten_when_settings_already_exist(self):
        self.report()
        self.settings.parent.mkdir()
        self.settings.write_text("{}", encoding="utf-8")
        again = self.report("--permissions")
        self.assertNotIn(LAB_JSON, again["append"])
        self.assertFalse(self.data()["permissions"]["written"])

    def test_a_hand_made_lab_json_gets_the_merge_and_keeps_its_keys(self):
        lab = self.proj / "research_lab"
        lab.mkdir()
        (lab / "lab.json").write_text('{"name": "mine", "connectors": []}\n', encoding="utf-8")
        self.report("--connectors", "pubmed", "--permissions")
        data = self.data()
        self.assertEqual(data["name"], "mine")
        self.assertEqual(data["connectors"], ["pubmed"])
        self.assertEqual(data["permissions"], {"written": True})
        self.assertEqual(data["pluginVersion"], plugin_version())

    def test_an_invalid_lab_json_is_left_alone_with_a_warning(self):
        lab = self.proj / "research_lab"
        lab.mkdir()
        (lab / "lab.json").write_text("{not json", encoding="utf-8")
        report = self.report("--connectors", "pubmed")
        self.assertEqual((lab / "lab.json").read_text(encoding="utf-8"), "{not json")
        self.assertTrue(any(w.startswith(LAB_JSON) and "valid JSON" in w for w in report["warn"]), report["warn"])
        self.assertIn(LAB_JSON, report["skip"])


if __name__ == "__main__":
    unittest.main()
