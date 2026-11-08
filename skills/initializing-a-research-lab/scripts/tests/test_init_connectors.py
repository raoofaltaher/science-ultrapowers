"""init_lab.py --connectors: the catalogue selection merged into the project's .mcp.json."""

import codecs
import json
import tempfile
import unittest
from pathlib import Path

from test_init_fresh import run_script

SCIENCE = ["firecrawl", "pubmed", "biorxiv", "chembl", "clinical-trials", "microsoft-learn"]


class ConnectorsCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.proj = self.tmp / "proj"
        self.proj.mkdir()
        self.mcp = self.proj / ".mcp.json"

    def run_init(self, *extra, yes=True):
        args = ["--project-root", str(self.proj), "--name", "Connect", *extra]
        if yes:
            args.append("--yes")
        args.append("--json")
        return run_script(args, self.tmp)

    def report(self, *extra, yes=True):
        result = self.run_init(*extra, yes=yes)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return json.loads(result.stdout)

    def servers(self):
        return json.loads(self.mcp.read_text(encoding="utf-8"))["mcpServers"]


class TestConnectors(ConnectorsCase):
    def test_science_selects_the_tagged_mcp_entries(self):
        plan = self.report("--connectors", "science", yes=False)
        self.assertEqual(len(SCIENCE), 6)
        self.assertEqual(list(plan["connectors"]), SCIENCE)
        self.assertNotIn("optuna", plan["connectors"])
        self.assertIn(".mcp.json", plan["create"])
        self.assertFalse(self.mcp.exists())
        self.report("--connectors", "science")
        self.assertEqual(list(self.servers()), SCIENCE)

    def test_server_shapes(self):
        self.report("--connectors", "firecrawl,optuna,asana")
        servers = self.servers()
        self.assertEqual(
            servers["firecrawl"], {"type": "http", "url": "https://mcp.firecrawl.dev/v2/mcp-search"}
        )
        self.assertEqual(servers["asana"], {"type": "sse", "url": "https://mcp.asana.com/sse"})
        self.assertEqual(set(servers["optuna"]), {"type", "command", "args"})
        self.assertEqual(servers["optuna"]["type"], "stdio")
        self.assertEqual(servers["optuna"]["command"], "uvx")
        self.assertRegex(servers["optuna"]["args"][0], r"^optuna-mcp==\d+(\.\d+)*$")
        self.assertEqual(servers["optuna"]["args"][1], "--storage")
        text = self.mcp.read_text(encoding="utf-8")
        self.assertTrue(text.endswith("}\n"))
        self.assertTrue(text.splitlines()[1].startswith('  "mcpServers"'))

    def test_merge_keeps_existing_servers(self):
        existing = {
            "mcpServers": {
                "Optuna": {"type": "stdio", "command": "mine", "args": ["--x"]},
                "other": {"type": "http", "url": "https://example.invalid/mcp"},
            }
        }
        self.mcp.write_text(json.dumps(existing, indent=4) + "\n", encoding="utf-8")
        report = self.report("--connectors", "science,optuna")
        servers = self.servers()
        self.assertEqual(servers["Optuna"], existing["mcpServers"]["Optuna"])
        self.assertEqual(servers["other"], existing["mcpServers"]["other"])
        self.assertNotIn("optuna", servers)
        self.assertEqual(len(servers), 2 + 6)
        self.assertEqual(list(servers)[:2], ["Optuna", "other"])
        lines = self.mcp.read_text(encoding="utf-8").splitlines()
        self.assertTrue(lines[1].startswith("    ") and not lines[1].startswith("     "), lines[1])
        self.assertIn(".mcp.json", report["append"])
        self.assertIn('.mcp.json: optuna (already configured as "Optuna")', report["skip"])
        lab = json.loads((self.proj / "research_lab" / "lab.json").read_text(encoding="utf-8"))
        self.assertEqual(lab["connectors"], SCIENCE + ["optuna"])

    def test_merge_keeps_other_top_level_keys_and_adds_the_servers_key(self):
        self.mcp.write_text('{\n  "note": [1, 2]\n}', encoding="utf-8")
        report = self.report("--connectors", "pubmed")
        data = json.loads(self.mcp.read_text(encoding="utf-8"))
        self.assertEqual(list(data), ["note", "mcpServers"])
        self.assertEqual(data["note"], [1, 2])
        self.assertIn(".mcp.json", report["append"])
        self.assertTrue(self.mcp.read_text(encoding="utf-8").endswith("\n"))

    def test_nothing_new_to_add_is_a_skip(self):
        self.report("--connectors", "pubmed")
        before = self.mcp.read_bytes()
        report = self.report("--connectors", "pubmed")
        self.assertEqual(self.mcp.read_bytes(), before)
        self.assertIn(".mcp.json", report["skip"])
        self.assertNotIn(".mcp.json", report["append"])
        self.assertNotIn(".mcp.json", report["create"])
        self.assertEqual(report["connectors"], {})

    def test_invalid_existing_mcp_json_is_left_alone(self):
        raw = b'{"mcpServers": {"a": {"type": "http", "url": "https://x"},}}'
        self.mcp.write_bytes(raw)
        report = self.report("--connectors", "pubmed,firecrawl")
        self.assertEqual(self.mcp.read_bytes(), raw)
        warns = [w for w in report["warn"] if ".mcp.json" in w]
        self.assertEqual(len(warns), 1, report["warn"])
        self.assertIn("not valid JSON", warns[0])
        self.assertIn("left unchanged", warns[0])
        self.assertEqual(report["connectors"], {})
        self.assertTrue((self.proj / "research_lab" / "lab.json").is_file())

    def test_lab_json_lists_no_connector_when_mcp_json_is_invalid(self):
        self.mcp.write_bytes(b'{"mcpServers": {"a": 1,}}')
        self.report("--connectors", "pubmed")
        lab = json.loads((self.proj / "research_lab" / "lab.json").read_text(encoding="utf-8"))
        self.assertEqual(lab["connectors"], [])

    def test_mcp_json_with_bom_is_merged(self):
        body = json.dumps({"mcpServers": {"other": {"type": "http", "url": "https://example.invalid/mcp"}}}, indent=2)
        self.mcp.write_bytes(codecs.BOM_UTF8 + (body + "\n").encode("utf-8"))
        report = self.report("--connectors", "pubmed")
        self.assertIn(".mcp.json", report["append"])
        self.assertFalse([w for w in report["warn"] if ".mcp.json" in w], report["warn"])
        raw = self.mcp.read_bytes()
        self.assertFalse(raw.startswith(codecs.BOM_UTF8))
        self.assertEqual(list(self.servers()), ["other", "pubmed"])

    def test_mcp_servers_that_is_not_an_object_is_left_alone(self):
        raw = b'{"mcpServers": []}'
        self.mcp.write_bytes(raw)
        report = self.report("--connectors", "pubmed")
        self.assertEqual(self.mcp.read_bytes(), raw)
        self.assertTrue(any(".mcp.json is not valid JSON" in w for w in report["warn"]), report["warn"])

    def test_unknown_connector_id_exits_2_before_writing(self):
        for yes in (True, False):
            result = self.run_init("--connectors", "pubmed,nope,also-nope", yes=yes)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("unknown connector id: nope", result.stderr)
            self.assertIn("unknown connector id: also-nope", result.stderr)
            self.assertEqual(list(self.proj.iterdir()), [])

    def test_account_and_bundled_ids_are_warnings(self):
        report = self.report("--connectors", "scispace,bundled:literature")
        self.assertFalse(self.mcp.exists())
        self.assertNotIn(".mcp.json", report["create"] + report["append"] + report["skip"])
        warns = [w for w in report["warn"] if w.startswith(("scispace:", "bundled:literature:"))]
        self.assertEqual(len(warns), 2, report["warn"])
        self.assertIn("claude.ai sign-in", warns[0])
        self.assertIn("Claude Science only", warns[1])
        self.assertEqual(report["connectors"], {})
        self.assertEqual(json.loads((self.proj / "research_lab" / "lab.json").read_text(encoding="utf-8"))["connectors"], [])

    def test_project_root_placeholder_in_args_is_posix(self):
        report = self.report("--connectors", "optuna")
        args = self.servers()["optuna"]["args"]
        self.assertEqual(args[2], f"sqlite:///{report['projectRoot']}/outputs/optuna/optuna.db")
        self.assertNotIn("\\", args[2])
        self.assertNotIn("{{", args[2])
        db = f"{report['projectRoot']}/outputs/optuna/optuna.db"
        warns = [w for w in report["warn"] if w.startswith("optuna:")]
        self.assertEqual(len(warns), 1, report["warn"])
        self.assertEqual(
            warns[0],
            f"optuna: needs uv; its .mcp.json entry holds this machine's path {db} "
            "(create outputs/optuna/ before first use; a collaborator edits the path)",
        )

    def test_lab_json_records_connectors(self):
        self.report("--connectors", " pubmed , firecrawl,pubmed,scispace")
        data = json.loads((self.proj / "research_lab" / "lab.json").read_text(encoding="utf-8"))
        self.assertEqual(data["connectors"], ["firecrawl", "pubmed"])
        self.assertEqual(list(self.servers()), ["firecrawl", "pubmed"])

    def test_without_connectors_there_is_no_mcp_json_in_the_plan(self):
        plan = self.report(yes=False)
        self.assertNotIn(".mcp.json", plan["create"] + plan["append"] + plan["skip"])
        self.assertEqual(plan["connectors"], {})
        self.report()
        self.assertFalse(self.mcp.exists())

    def test_no_backslashes_in_written_json(self):
        self.report("--connectors", "science")
        for path in (self.mcp, self.proj / "research_lab" / "lab.json"):
            self.assertNotIn("\\", path.read_text(encoding="utf-8"), path.as_posix())

    def test_files_are_lf(self):
        self.report("--connectors", "science")
        self.assertNotIn(b"\r", self.mcp.read_bytes())


if __name__ == "__main__":
    unittest.main()
