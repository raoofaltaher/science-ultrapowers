"""Offline tests for verify_doi's retraction-check failure path, the command line
(main), --csv, --registry-bib and the network failure path.

Every test patches the HTTP function (`crossref_get`, `doi_to_bibtex` or
`urllib.request.urlopen`); none reaches the network.
"""

from __future__ import annotations

import contextlib
import io
import json
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
        self.assertEqual(result["status"], "ERROR")
        self.assertIn("retraction check could not run (HTTP 503)", result["problems"])
        self.assertEqual(len(fake.work_calls(GOOD_DOI)), 1, "the fetched work must be reused")

    def test_update_query_404_is_not_a_failure(self):
        fake = FakeCrossref(update_code=404)
        with mock.patch.object(verify_doi, "crossref_get", fake):
            result = verify_doi.verify_doi(GOOD_DOI, title=TITLE, first_author="Alam", year=2018)
        self.assertEqual(result["status"], "VERIFIED")

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
        self.assertEqual(result["status"], "RETRACTED")


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
        self.assertEqual(result["status"], "MISMATCH")
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
        self.assertEqual(result["status"], "MISMATCH")
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
        self.assertEqual(json.loads(out)["summary"], {"RESOLVES_UNCHECKED": 1})
        self.assertEqual(code, 0, err)

    def test_retracted_doi_exits_one(self):
        code, out, err = self.extract("Cited: %s and %s." % (GOOD_DOI, RETRACTED_DOI), FakeCrossref())
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["summary"], {"RESOLVES_UNCHECKED": 1, "RETRACTED": 1})

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
        self.assertEqual(json.loads(out)["results"][0]["status"], "RESOLVES_UNCHECKED")
        self.assertEqual(code, 1)


REGISTRY_HEADER = "ref_id,doi,title,first_author,year,lab_status,retraction_status\n"


class CsvTests(unittest.TestCase):
    def test_csv_with_one_row_verifies_it(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "REGISTRY.csv"
            path.write_text(
                REGISTRY_HEADER + "R1,%s,%s,Alam,2018,ADMITTED,no retraction\n" % (GOOD_DOI, TITLE),
                encoding="utf-8",
            )
            with mock.patch.object(verify_doi, "crossref_get", FakeCrossref()):
                code, out, err = run_main("--csv", str(path))
        self.assertEqual(code, 0, err)
        report = json.loads(out)
        self.assertEqual(report["summary"], {"VERIFIED": 1})

    def test_csv_row_without_a_doi_is_no_doi_and_exits_one(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "REGISTRY.csv"
            path.write_text(REGISTRY_HEADER + "R1,,%s,Alam,2018,ADMITTED,\n" % TITLE, encoding="utf-8")
            with mock.patch.object(verify_doi, "crossref_get", FakeCrossref()):
                code, out, err = run_main("--csv", str(path))
        self.assertEqual(json.loads(out)["summary"], {"NO_DOI": 1})
        self.assertEqual(code, 1)


class RegistryBibTests(unittest.TestCase):
    def test_registry_bib_writes_the_verified_admitted_row(self):
        with tempfile.TemporaryDirectory() as folder:
            registry = Path(folder) / "REGISTRY.csv"
            out_bib = Path(folder) / "REGISTRY.bib"
            registry.write_text(
                REGISTRY_HEADER
                + "R1,%s,%s,Alam,2018,ADMITTED,no retraction\n" % (GOOD_DOI, TITLE)
                + "R2,%s,%s,Alam,2018,PENDING_FULLTEXT,\n" % (GOOD_DOI, TITLE),
                encoding="utf-8",
            )
            with mock.patch.object(verify_doi, "crossref_get", FakeCrossref()), \
                    mock.patch.object(verify_doi, "doi_to_bibtex", return_value="@article{R1,\n  title={x}\n}") as bib:
                code, out, err = run_main("--registry-bib", str(registry), "--out", str(out_bib))
            self.assertEqual(code, 0, err)
            report = json.loads(out)
            self.assertEqual(report["written"], ["R1"])
            self.assertEqual([row[0] for row in report["skipped"]], ["R2"])
            self.assertEqual(bib.call_args.kwargs["key"], "R1")
            self.assertIn("@article{R1,", out_bib.read_text(encoding="utf-8"))

    def test_registry_bib_reverification_failure_exits_one_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            registry = Path(folder) / "REGISTRY.csv"
            registry.write_text(
                REGISTRY_HEADER + "R1,%s,A different title,Alam,2018,ADMITTED,\n" % GOOD_DOI,
                encoding="utf-8",
            )
            with mock.patch.object(verify_doi, "crossref_get", FakeCrossref()), \
                    mock.patch.object(verify_doi, "doi_to_bibtex") as bib:
                code, out, err = run_main("--registry-bib", str(registry), "--out", str(Path(folder) / "x.bib"))
            self.assertEqual(code, 1)
            self.assertEqual(json.loads(out)["written"], [])
            bib.assert_not_called()


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
        self.assertEqual(result["status"], "ERROR")
        self.assertIn("HTTP -1", result["problems"][0])

    def test_bibtex_request_failure_raises_runtime_error(self):
        with mock.patch.object(verify_doi.urllib.request, "urlopen", side_effect=urllib.error.URLError("down")), \
                mock.patch.object(verify_doi.time, "sleep"):
            with self.assertRaises(RuntimeError):
                verify_doi.doi_to_bibtex(GOOD_DOI)


if __name__ == "__main__":
    unittest.main()
