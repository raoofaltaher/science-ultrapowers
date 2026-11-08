"""Offline tests for verify_doi's retraction-check failure path, the command line
(main), --csv, --sources-bib (and its hidden alias --registry-bib) and the network failure path.

Every test patches the HTTP function (`crossref_get`, `doi_to_bibtex` or
`urllib.request.urlopen`); none reaches the network.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import verify_doi  # noqa: E402

GOOD_DOI = "10.9999/good-fixture"
RETRACTED_DOI = "10.9999/retracted-fixture"
TITLE = "Deep learning for disaster response classification"

GOOD_MESSAGE = {
    "title": [TITLE],
    "author": [
        {"given": "Firoj", "family": "Alam"},
        {"given": "Ferda", "family": "Ofli"},
        {"given": "Muhammad", "family": "Imran"},
    ],
    "issued": {"date-parts": [[2018]]},
    "container-title": ["Proceedings of Example Conference"],
    "type": "proceedings-article",
    "publisher": "Example Publisher",
}

RETRACTED_MESSAGE = dict(GOOD_MESSAGE, **{"updated-by": [{"type": "retraction", "DOI": "10.9999/notice", "source": "retraction-watch"}]})


class FakeCrossref:
    """A stand-in for `crossref_get`: records every call, answers from fixed data."""

    def __init__(self, works=None, update_code=200, search_code=200, search_items=None):
        self.works = works if works is not None else {GOOD_DOI: GOOD_MESSAGE, RETRACTED_DOI: RETRACTED_MESSAGE}
        self.update_code = update_code
        self.search_code = search_code
        self.search_items = search_items or []
        self.calls = []

    def __call__(self, path, params=None, retries=3):
        self.calls.append((path, dict(params or {})))
        if path.startswith("/works/"):
            doi = path[len("/works/"):]
            if doi in self.works:
                return 200, {"message": self.works[doi]}
            return 404, None
        if path == "/works":
            if params and "filter" in params:
                if self.update_code != 200:
                    return self.update_code, None
                return 200, {"message": {"items": []}}
            if self.search_code != 200:
                return self.search_code, None
            return 200, {"message": {"items": self.search_items}}
        raise AssertionError("unexpected path %r" % (path,))

    def work_calls(self, doi):
        return [c for c in self.calls if c[0] == "/works/" + doi]


def run_main(*args):
    """Run verify_doi.main() with `args` as the command line; return (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with mock.patch.object(sys, "argv", ["verify_doi.py", *args]), \
            mock.patch.object(verify_doi.time, "sleep"), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = verify_doi.main()
        except SystemExit as exit_:  # argparse errors
            code = exit_.code
    return code, out.getvalue(), err.getvalue()


class UpdateQueryFailureTests(unittest.TestCase):
    def test_update_query_failure_is_error_not_verified(self):
        fake = FakeCrossref(update_code=503)
        with mock.patch.object(verify_doi, "crossref_get", fake):
            result = verify_doi.verify_doi(GOOD_DOI, title=TITLE, first_author="Alam", year=2018)
        self.assertEqual(result["status"], "error")
        self.assertIn("retraction check could not run (HTTP 503)", result["problems"])
        self.assertEqual(len(fake.work_calls(GOOD_DOI)), 1, "the fetched work must be reused")

    def test_update_query_404_is_not_a_failure(self):
        fake = FakeCrossref(update_code=404)
        with mock.patch.object(verify_doi, "crossref_get", fake):
            result = verify_doi.verify_doi(GOOD_DOI, title=TITLE, first_author="Alam", year=2018)
        self.assertEqual(result["status"], "matched")

    def test_crossref_updates_returns_notices_and_ok(self):
        with mock.patch.object(verify_doi, "crossref_get", FakeCrossref()):
            notices, ok = verify_doi.crossref_updates(RETRACTED_DOI)
        self.assertTrue(ok)
        self.assertEqual([n["type"] for n in notices], ["retraction"])
        with mock.patch.object(verify_doi, "crossref_get", FakeCrossref(update_code=500)):
            notices, ok = verify_doi.crossref_updates(GOOD_DOI)
        self.assertFalse(ok)

    def test_retraction_is_still_reported_when_the_update_query_fails(self):
        fake = FakeCrossref(update_code=503)
        with mock.patch.object(verify_doi, "crossref_get", fake):
            result = verify_doi.verify_doi(RETRACTED_DOI, title=TITLE, first_author="Alam", year=2018)
        self.assertEqual(result["status"], "retracted")


class SearchTests(unittest.TestCase):
    def test_search_http_failure_exits_one_with_a_message(self):
        with mock.patch.object(verify_doi, "crossref_get", FakeCrossref(search_code=503)):
            code, out, err = run_main("--search", "some title")
        self.assertEqual(code, 1)
        self.assertIn("error: Crossref search failed (HTTP 503)", err)
        self.assertNotIn("Traceback", err)
        self.assertEqual(out.strip(), "")

    def test_search_prints_unescaped_titles(self):
        items = [{"DOI": GOOD_DOI, "title": ["Fish &amp; Chips: a &lt;study&gt;"], "author": [{"family": "Alam"}],
                  "issued": {"date-parts": [[2018]]}, "container-title": ["J &amp; Co"], "type": "journal-article"}]
        with mock.patch.object(verify_doi, "crossref_get", FakeCrossref(search_items=items)):
            code, out, err = run_main("--search", "Fish and Chips")
        self.assertEqual(code, 0, err)
        rows = json.loads(out)
        self.assertEqual(rows[0]["title"], "Fish & Chips: a <study>")
        self.assertNotIn("&amp;", out)


class TitleUnescapeTests(unittest.TestCase):
    def test_verify_doi_unescapes_the_crossref_title_everywhere_it_is_printed(self):
        message = dict(GOOD_MESSAGE, title=["Fish &amp; Chips"])
        fake = FakeCrossref(works={GOOD_DOI: message})
        with mock.patch.object(verify_doi, "crossref_get", fake):
            result = verify_doi.verify_doi(GOOD_DOI, title="Something else entirely", first_author="Alam", year=2018)
        self.assertEqual(result["crossref_title"], "Fish & Chips")
        self.assertEqual(result["status"], "mismatch")
        self.assertTrue(any("'Fish & Chips'" in p for p in result["problems"]), result["problems"])
        self.assertNotIn("&amp;", json.dumps(result))


class AuthorsFlagTests(unittest.TestCase):
    def test_semicolon_authors_run_the_author_list_check(self):
        with mock.patch.object(verify_doi, "crossref_get", FakeCrossref()):
            code, out, err = run_main(GOOD_DOI, "--title", TITLE, "--first-author", "Alam", "--year", "2018",
                                      "--authors", "Firoj Alam; Ferda Ofli; Muhammad Imran")
            self.assertEqual(code, 0, err)
            self.assertEqual(json.loads(out)["results"][0]["author_list_problems"], [])
            code, out, err = run_main(GOOD_DOI, "--title", TITLE, "--first-author", "Alam", "--year", "2018",
                                      "--authors", "Firoj Alam; Ferda Ofli; Muhammad Ali Khan")
        self.assertEqual(code, 1)
        result = json.loads(out)["results"][0]
        self.assertEqual(result["status"], "mismatch")
        self.assertTrue(any("author #3" in p for p in result["author_list_problems"]), result)


class ExtractExitCodeTests(unittest.TestCase):
    def extract(self, text, fake):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "manuscript.md"
            path.write_text(text, encoding="utf-8")
            with mock.patch.object(verify_doi, "crossref_get", fake):
                return run_main("--extract-from", str(path))

    def test_resolves_unchecked_alone_exits_zero(self):
        code, out, err = self.extract("See https://doi.org/%s for details." % GOOD_DOI, FakeCrossref())
        self.assertEqual(json.loads(out)["summary"], {"resolves unchecked": 1})
        self.assertEqual(code, 0, err)

    def test_retracted_doi_exits_one(self):
        code, out, err = self.extract("Cited: %s and %s." % (GOOD_DOI, RETRACTED_DOI), FakeCrossref())
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["summary"], {"resolves unchecked": 1, "retracted": 1})

    def test_unresolved_doi_exits_one(self):
        code, out, err = self.extract("Cited: 10.9999/not-there.", FakeCrossref())
        self.assertEqual(code, 1)

    def test_preprint_exits_one(self):
        code, out, err = self.extract("Cited: 10.48550/arxiv.2101.00001.", FakeCrossref())
        self.assertEqual(code, 1)

    def test_error_exits_one(self):
        code, out, err = self.extract("Cited: %s." % GOOD_DOI, FakeCrossref(update_code=500))
        self.assertEqual(code, 1)

    def test_a_doi_command_with_resolves_unchecked_still_exits_one(self):
        with mock.patch.object(verify_doi, "crossref_get", FakeCrossref()):
            code, out, err = run_main(GOOD_DOI)
        self.assertEqual(json.loads(out)["results"][0]["status"], "resolves unchecked")
        self.assertEqual(code, 1)


SOURCES_HEADER = "source_id,title,first_author,year,doi,source_class,doi_status,status,evidence_records,notes\n"
LEGACY_HEADER = "ref_id,doi,title,first_author,year,lab_status,retraction_status\n"
OLD_LAYOUT_MESSAGE = "this lab uses the 0.1 layout; run science-ultrapowers:initializing-a-research-lab to migrate it"


def source_row(source_id, status, doi=GOOD_DOI, title=TITLE, doi_status="matched"):
    return "%s,%s,Alam,2018,%s,peer-reviewed matched doi,%s,%s,EVR-0001,\n" % (source_id, title, doi, doi_status, status)


class CsvTests(unittest.TestCase):
    def test_csv_with_one_row_matches_it(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "SOURCES.csv"
            path.write_text(SOURCES_HEADER + source_row("S1", "citable"), encoding="utf-8")
            with mock.patch.object(verify_doi, "crossref_get", FakeCrossref()):
                code, out, err = run_main("--csv", str(path))
        self.assertEqual(code, 0, err)
        report = json.loads(out)
        self.assertEqual(report["summary"], {"matched": 1})

    def test_csv_row_without_a_doi_is_no_doi_and_exits_one(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "SOURCES.csv"
            path.write_text(SOURCES_HEADER + source_row("S1", "citable", doi=""), encoding="utf-8")
            with mock.patch.object(verify_doi, "crossref_get", FakeCrossref()):
                code, out, err = run_main("--csv", str(path))
        self.assertEqual(json.loads(out)["summary"], {"no doi": 1})
        self.assertEqual(code, 1)

    def test_csv_in_the_legacy_column_layout_still_reads(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "REGISTRY.csv"
            path.write_text(LEGACY_HEADER + "R1,%s,%s,Alam,2018,ADMITTED,no retraction\n" % (GOOD_DOI, TITLE), encoding="utf-8")
            with mock.patch.object(verify_doi, "crossref_get", FakeCrossref()):
                code, out, err = run_main("--csv", str(path))
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["summary"], {"matched": 1})


class SourcesBibTests(unittest.TestCase):
    def build(self, flag, header, rows):
        with tempfile.TemporaryDirectory() as folder:
            sources = Path(folder) / "SOURCES.csv"
            out_bib = Path(folder) / "SOURCES.bib"
            sources.write_text(header + rows, encoding="utf-8")
            with mock.patch.object(verify_doi, "crossref_get", FakeCrossref()), \
                    mock.patch.object(verify_doi, "doi_to_bibtex", return_value="@article{S1,\n  title={x}\n}") as bib:
                code, out, err = run_main(flag, str(sources), "--out", str(out_bib))
            text = out_bib.read_text(encoding="utf-8") if out_bib.exists() else ""
        return code, out, err, bib, text

    def test_sources_bib_writes_the_matched_citable_row(self):
        rows = source_row("S1", "citable") + source_row("S2", "awaiting full text")
        code, out, err, bib, text = self.build("--sources-bib", SOURCES_HEADER, rows)
        self.assertEqual(code, 0, err)
        report = json.loads(out)
        self.assertEqual(report["written"], ["S1"])
        self.assertEqual([row[0] for row in report["skipped"]], ["S2"])
        self.assertIn("source status awaiting full text", report["skipped"][0][1])
        self.assertEqual(bib.call_args.kwargs["key"], "S1")
        self.assertIn("@article{S1,", text)
        self.assertIn("source table", text)

    def test_registry_bib_is_a_hidden_alias_for_sources_bib(self):
        code, out, err, bib, text = self.build("--registry-bib", SOURCES_HEADER, source_row("S1", "citable"))
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["written"], ["S1"])
        help_code, help_out, help_err = run_main("--help")
        self.assertNotIn("--registry-bib", help_out)
        self.assertIn("--sources-bib", help_out)

    def test_legacy_admitted_status_and_legacy_columns_are_read(self):
        rows = "R1,%s,%s,Alam,2018,ADMITTED,no retraction\nR2,%s,%s,Alam,2018,PENDING_FULLTEXT,\n" % (GOOD_DOI, TITLE, GOOD_DOI, TITLE)
        code, out, err, bib, text = self.build("--sources-bib", LEGACY_HEADER, rows)
        self.assertEqual(code, 0, err)
        report = json.loads(out)
        self.assertEqual(report["written"], ["R1"])
        self.assertEqual([row[0] for row in report["skipped"]], ["R2"])
        self.assertIn("awaiting full text", report["skipped"][0][1])
        self.assertEqual(bib.call_args.kwargs["key"], "R1")

    def test_a_row_whose_doi_status_is_retracted_is_skipped_and_the_legacy_token_too(self):
        for token in ("retracted", "RETRACTED", "concern"):
            code, out, err, bib, text = self.build("--sources-bib", SOURCES_HEADER, source_row("S1", "citable", doi_status=token))
            report = json.loads(out)
            self.assertEqual(report["written"], [], token)
            self.assertIn("doi status", report["skipped"][0][1])
            bib.assert_not_called()

    def test_rematch_failure_exits_one_and_writes_nothing(self):
        code, out, err, bib, text = self.build("--sources-bib", SOURCES_HEADER, source_row("S1", "citable", title="A different title"))
        self.assertEqual(code, 1)
        report = json.loads(out)
        self.assertEqual(report["written"], [])
        self.assertIn("re-check mismatch", report["errors"][0][1])
        bib.assert_not_called()


class OldLayoutTests(unittest.TestCase):
    def run_in(self, lab_setup, *args):
        with tempfile.TemporaryDirectory() as folder:
            lab_setup(Path(folder))
            here = Path.cwd()
            os.chdir(folder)
            try:
                return run_main(*args)
            finally:
                os.chdir(here)

    @staticmethod
    def old_lab(root):
        old = root / "research_lab" / "01_reference_registry"
        old.mkdir(parents=True)
        (old / "REGISTRY.csv").write_text(LEGACY_HEADER, encoding="utf-8")

    def test_csv_in_a_lab_with_the_old_layout_exits_two_with_the_exact_message(self):
        code, out, err = self.run_in(self.old_lab, "--csv", "research_lab/literature/SOURCES.csv")
        self.assertEqual(code, 2)
        self.assertEqual(err.strip(), OLD_LAYOUT_MESSAGE)
        self.assertEqual(out, "")

    def test_a_path_inside_the_numbered_folder_is_the_old_layout_too(self):
        code, out, err = self.run_in(self.old_lab, "--sources-bib", "research_lab/01_reference_registry/REGISTRY.csv")
        self.assertEqual(code, 2)
        self.assertEqual(err.strip(), OLD_LAYOUT_MESSAGE)

    def test_a_lab_with_the_new_layout_is_not_the_old_layout(self):
        def setup(root):
            (root / "research_lab" / "01_reference_registry").mkdir(parents=True)
            new = root / "research_lab" / "literature"
            new.mkdir(parents=True)
            (new / "SOURCES.csv").write_text(SOURCES_HEADER + source_row("S1", "citable"), encoding="utf-8")
        with mock.patch.object(verify_doi, "crossref_get", FakeCrossref()):
            code, out, err = self.run_in(setup, "--csv", "research_lab/literature/SOURCES.csv")
        self.assertEqual(code, 0, err)


class StatusWordTests(unittest.TestCase):
    def test_every_status_is_a_lower_case_word(self):
        seen = {}
        with mock.patch.object(verify_doi, "crossref_get", FakeCrossref()):
            seen["matched"] = verify_doi.verify_doi(GOOD_DOI, title=TITLE, first_author="Alam", year=2018)["status"]
            seen["resolves unchecked"] = verify_doi.verify_doi(GOOD_DOI)["status"]
            seen["mismatch"] = verify_doi.verify_doi(GOOD_DOI, title="Something else entirely")["status"]
            seen["retracted"] = verify_doi.verify_doi(RETRACTED_DOI)["status"]
            seen["unresolved"] = verify_doi.verify_doi("10.9999/not-there")["status"]
        seen["preprint"] = verify_doi.verify_doi("10.48550/arxiv.2101.00001")["status"]
        with mock.patch.object(verify_doi, "crossref_get", FakeCrossref(update_code=500)):
            seen["error"] = verify_doi.verify_doi(GOOD_DOI)["status"]
        for expected, got in seen.items():
            self.assertEqual(got, expected)
        self.assertEqual(
            verify_doi.DOI_STATUSES,
            ("matched", "mismatch", "resolves unchecked", "unresolved", "retracted", "concern", "preprint", "no doi", "error"),
        )

    def test_concern_status_for_an_expression_of_concern(self):
        message = dict(GOOD_MESSAGE, **{"updated-by": [{"type": "expression_of_concern", "DOI": "10.9999/notice"}]})
        with mock.patch.object(verify_doi, "crossref_get", FakeCrossref(works={GOOD_DOI: message})):
            self.assertEqual(verify_doi.verify_doi(GOOD_DOI)["status"], "concern")

    def test_old_upper_case_tokens_are_read_as_the_new_words(self):
        legacy = {"VERIFIED": "matched", "MISMATCH": "mismatch", "RESOLVES_UNCHECKED": "resolves unchecked",
                  "UNRESOLVED": "unresolved", "RETRACTED": "retracted", "CONCERN": "concern",
                  "PREPRINT": "preprint", "NO_DOI": "no doi", "ERROR": "error"}
        for old, new in legacy.items():
            self.assertEqual(verify_doi.normalize_doi_status(old), new)
            self.assertEqual(verify_doi.normalize_doi_status(new), new)
        self.assertEqual(verify_doi.normalize_doi_status("  Verified "), "matched")
        self.assertEqual(verify_doi.normalize_doi_status("something else"), "something else")

    def test_old_source_status_tokens_are_read_as_the_new_words(self):
        legacy = {"ADMITTED": "citable", "ADMITTED_EXCEPTION": "citable by exception", "DOI_VERIFIED": "metadata matched",
                  "PENDING_FULLTEXT": "awaiting full text", "PENDING_APPROVAL": "awaiting approval", "CANDIDATE_DOI": "candidate",
                  "EXCLUDED_PREPRINT": "excluded: preprint", "EXCLUDED_RETRACTED": "excluded: retracted",
                  "REJECTED_MISMATCH": "rejected: mismatch"}
        for old, new in legacy.items():
            self.assertEqual(verify_doi.normalize_source_status(old), new)
            self.assertEqual(verify_doi.normalize_source_status(new), new)


class EvidenceRecordTests(unittest.TestCase):
    def test_the_evidence_record_is_rendered_in_the_new_words(self):
        result = {"status": "matched", "checked_at": "2026-11-08T00:00:00Z", "updates": []}
        text = verify_doi.evidence_record_md("EVR-0001", "A claim", "a quote", "p. 3", GOOD_DOI, "Alam 2018", result, "literature-researcher")
        self.assertIn("### EVR-0001", text)
        self.assertIn("| DOI status | matched (checked 2026-11-08T00:00:00Z) |", text)
        self.assertIn("| Checked by | PENDING |", text)
        self.assertNotIn("card", text.lower())
        self.assertNotIn("VERIFIED", text)

    def test_an_unchecked_record_says_not_run(self):
        text = verify_doi.evidence_record_md("EVR-0002", "c", "q", "p. 1", GOOD_DOI, "x", None, "role")
        self.assertIn("| DOI status | not run (checked ) |", text)

    def test_the_old_function_name_is_kept_as_an_alias(self):
        self.assertIs(verify_doi.evidence_card_md, verify_doi.evidence_record_md)


class MessageWordTests(unittest.TestCase):
    def test_search_candidates_are_labelled_in_the_new_words(self):
        items = [{"DOI": GOOD_DOI, "title": [TITLE], "author": [{"family": "Alam"}], "issued": {"date-parts": [[2018]]},
                  "container-title": ["J"], "type": "journal-article"}]
        with mock.patch.object(verify_doi, "crossref_get", FakeCrossref(search_items=items)):
            code, out, err = run_main("--search", TITLE)
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)[0]["label"], "candidate: confirm against the full text")

    def test_problems_use_the_new_words_and_no_tier_letters(self):
        preprint = verify_doi.verify_doi("10.48550/arxiv.2101.00001")
        with mock.patch.object(verify_doi, "crossref_get", FakeCrossref()):
            resolves = verify_doi.verify_doi(GOOD_DOI)
        for result in (preprint, resolves):
            text = " ".join(result["problems"])
            self.assertNotRegex(text, r"Tier [A-X]")
            self.assertNotIn("registry", text.lower())
        self.assertIn("not peer-reviewed", preprint["problems"][0])
        self.assertIn("to match", resolves["problems"][0])

    def test_help_names_the_source_table_and_the_new_statuses(self):
        code, out, err = run_main("--help")
        self.assertIn("SOURCES.csv", out)
        self.assertIn("research_lab/literature/SOURCES.csv", out)
        self.assertNotIn("REGISTRY", out)
        self.assertNotIn("01_reference_registry", out)


class NetworkFailureTests(unittest.TestCase):
    def test_crossref_get_reports_minus_one_when_the_network_is_down(self):
        with mock.patch.object(verify_doi.urllib.request, "urlopen", side_effect=urllib.error.URLError("down")) as op, \
                mock.patch.object(verify_doi.time, "sleep"):
            code, js = verify_doi.crossref_get("/works/10.1/x")
        self.assertEqual((code, js), (-1, None))
        self.assertEqual(op.call_count, 3)

    def test_network_down_gives_error_status_and_exit_one(self):
        with mock.patch.object(verify_doi.urllib.request, "urlopen", side_effect=urllib.error.URLError("down")), \
                mock.patch.object(verify_doi.time, "sleep"):
            code, out, err = run_main(GOOD_DOI, "--title", TITLE, "--first-author", "Alam", "--year", "2018")
        self.assertEqual(code, 1)
        result = json.loads(out)["results"][0]
        self.assertEqual(result["status"], "error")
        self.assertIn("HTTP -1", result["problems"][0])

    def test_bibtex_request_failure_raises_runtime_error(self):
        with mock.patch.object(verify_doi.urllib.request, "urlopen", side_effect=urllib.error.URLError("down")), \
                mock.patch.object(verify_doi.time, "sleep"):
            with self.assertRaises(RuntimeError):
                verify_doi.doi_to_bibtex(GOOD_DOI)


if __name__ == "__main__":
    unittest.main()
