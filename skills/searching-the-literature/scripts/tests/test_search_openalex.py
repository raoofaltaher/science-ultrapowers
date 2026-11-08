import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "search_openalex.py"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import search_openalex as so  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "openalex_works.json"
ROW_KEYS = {"doi", "title", "year", "type", "venue", "is_preprint", "openalex_id"}


def load_fixture():
    with FIXTURE.open(encoding="utf-8") as handle:
        return json.load(handle)


class ParseWorksTest(unittest.TestCase):
    def setUp(self):
        self.rows = so.parse_works(load_fixture())

    def test_returns_four_rows_with_exact_keys_in_order(self):
        self.assertEqual(len(self.rows), 4)
        for row in self.rows:
            self.assertEqual(set(row.keys()), ROW_KEYS)
        self.assertEqual(
            [row["openalex_id"] for row in self.rows], ["W111", "W222", "W333", "W444"]
        )

    def test_journal_article_row(self):
        row = self.rows[0]
        self.assertEqual(row["doi"], "10.1000/xyz123")
        self.assertEqual(row["venue"], "Journal of Examples")
        self.assertIs(row["is_preprint"], False)
        self.assertEqual(row["openalex_id"], "W111")
        self.assertEqual(row["year"], 2021)
        self.assertEqual(row["title"], "Calibration of Example Classifiers")
        self.assertEqual(row["type"], "article")

    def test_arxiv_item_is_preprint_by_doi_prefix(self):
        row = self.rows[1]
        self.assertIs(row["is_preprint"], True)
        self.assertEqual(row["doi"], "10.48550/arXiv.2101.00001")

    def test_preprint_type_with_null_primary_location(self):
        row = self.rows[2]
        self.assertIs(row["is_preprint"], True)
        self.assertIsNone(row["venue"])
        self.assertEqual(row["doi"], "10.5281/zenodo.1234567")

    def test_work_without_doi_or_source(self):
        row = self.rows[3]
        self.assertIsNone(row["doi"])
        self.assertIsNone(row["venue"])
        self.assertIs(row["is_preprint"], False)
        self.assertEqual(row["type"], "book-chapter")

    def test_missing_results_returns_empty_list(self):
        self.assertEqual(so.parse_works({}), [])

    def test_doi_prefix_variants_are_stripped(self):
        payload = {
            "results": [
                {"id": "https://openalex.org/W1", "doi": "http://doi.org/10.1/a"},
                {"id": "https://openalex.org/W2", "doi": "doi:10.1/b"},
                {"id": "https://openalex.org/W3", "doi": "10.1/c"},
            ]
        }
        self.assertEqual(
            [row["doi"] for row in so.parse_works(payload)],
            ["10.1/a", "10.1/b", "10.1/c"],
        )


class BuildUrlTest(unittest.TestCase):
    def test_query_with_limit_and_from_year(self):
        self.assertEqual(
            so.build_url("calibration of classifiers", limit=25, from_year=2020),
            "https://api.openalex.org/works?search=calibration+of+classifiers"
            "&per-page=25&filter=publication_year%3A%3E2019",
        )

    def test_no_filter_without_from_year(self):
        url = so.build_url("calibration of classifiers", limit=25)
        self.assertEqual(
            url,
            "https://api.openalex.org/works?search=calibration+of+classifiers&per-page=25",
        )
        self.assertNotIn("filter", url)


class _Response:
    """A stand-in for the urlopen response: a context manager whose read() returns fixed bytes."""

    def __init__(self, body):
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self._body


class FetchTest(unittest.TestCase):
    def test_connection_reset_is_retried_then_reported_as_openalex_error(self):
        from unittest import mock

        with mock.patch.object(so.urllib.request, "urlopen", side_effect=ConnectionResetError("reset")) as op, \
                mock.patch.object(so.time, "sleep"):
            with self.assertRaises(so.OpenAlexError):
                so.fetch("https://api.openalex.org/works?search=x")
        self.assertEqual(op.call_count, len(so.BACKOFF_SECONDS) + 1)

    def test_body_that_is_not_utf8_is_reported_without_retry(self):
        from unittest import mock

        with mock.patch.object(so.urllib.request, "urlopen", return_value=_Response(b"\xff\xfe{")) as op, \
                mock.patch.object(so.time, "sleep"):
            with self.assertRaises(so.OpenAlexError):
                so.fetch("https://api.openalex.org/works?search=x")
        self.assertEqual(op.call_count, 1)


class JsonInErrorTest(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(Path(so.__file__)), *args],
                              capture_output=True, text=True, encoding="utf-8", timeout=60)

    def test_missing_json_in_file_is_a_clean_error(self):
        r = self.run_cli("--json-in", os.path.join(os.path.dirname(__file__), "fixtures", "missing.json"))
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("error: cannot read", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_json_in_file_that_is_not_json_is_a_clean_error(self):
        r = self.run_cli("--json-in", __file__)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("error: cannot read", r.stderr)
        self.assertNotIn("Traceback", r.stderr)


class CliTest(unittest.TestCase):
    def offline_env(self):
        env = dict(os.environ)
        for name in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
            env[name] = "http://127.0.0.1:9"
        return env

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=self.offline_env(),
            timeout=60,
        )

    def test_json_in_prints_parsed_rows_without_network(self):
        result = self.run_cli("--query", "x", "--json-in", str(FIXTURE))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), so.parse_works(load_fixture()))

    def test_json_in_without_query_is_allowed(self):
        result = self.run_cli("--json-in", str(FIXTURE))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), so.parse_works(load_fixture()))

    def test_limit_zero_is_usage_error(self):
        result = self.run_cli("--query", "x", "--limit", "0", "--json-in", str(FIXTURE))
        self.assertEqual(result.returncode, 2)

    def test_limit_201_is_usage_error(self):
        result = self.run_cli("--query", "x", "--limit", "201", "--json-in", str(FIXTURE))
        self.assertEqual(result.returncode, 2)

    def test_missing_query_without_json_in_is_usage_error(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)


class SnowballTest(unittest.TestCase):
    """--cited-by and --references, with fetch patched: no test here reaches the network."""

    WORK = {
        "id": "https://openalex.org/W111",
        "cited_by_api_url": "https://api.openalex.org/works?filter=cites:W111",
        "referenced_works": [
            "https://openalex.org/W11",
            "https://openalex.org/W12",
            "https://openalex.org/W13",
        ],
    }

    def run_main(self, *args, responses):
        """Run main(args) with fetch answering from `responses` in order; return (code, stdout, stderr, urls)."""
        import contextlib
        import io
        from unittest import mock

        urls = []
        queue = list(responses)

        def fake_fetch(url):
            urls.append(url)
            reply = queue.pop(0)
            if isinstance(reply, Exception):
                raise reply
            return reply

        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(so, "fetch", fake_fetch),                 contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = so.main(list(args))
            except SystemExit as exit_:
                code = exit_.code
        return code, out.getvalue(), err.getvalue(), urls

    def test_cited_by_fetches_the_work_then_its_citing_works(self):
        code, out, err, urls = self.run_main("--cited-by", "W111", responses=[self.WORK, load_fixture()])
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out), so.parse_works(load_fixture()))
        self.assertEqual(urls[0], "https://api.openalex.org/works/W111")
        self.assertIn("filter=cites:W111", urls[1])
        self.assertIn("per-page=25", urls[1])

    def test_cited_by_accepts_the_openalex_url_and_lowercase(self):
        code, out, err, urls = self.run_main("--cited-by", "https://openalex.org/w111", responses=[self.WORK, load_fixture()])
        self.assertEqual(code, 0, err)
        self.assertEqual(urls[0], "https://api.openalex.org/works/W111")

    def test_cited_by_ignores_a_cited_by_url_that_is_not_openalex(self):
        work = dict(self.WORK, cited_by_api_url="https://evil.example/works?filter=cites:W111")
        code, out, err, urls = self.run_main("--cited-by", "W111", responses=[work, load_fixture()])
        self.assertEqual(code, 0, err)
        self.assertTrue(urls[1].startswith("https://api.openalex.org/works?"), urls[1])

    def test_references_fetches_the_referenced_works_by_id(self):
        from urllib.parse import parse_qs, urlparse

        code, out, err, urls = self.run_main("--references", "W111", responses=[self.WORK, load_fixture()])
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out), so.parse_works(load_fixture()))
        self.assertEqual(urls[0], "https://api.openalex.org/works/W111")
        query = parse_qs(urlparse(urls[1]).query)
        self.assertEqual(query["filter"], ["openalex:W11|W12|W13"])
        self.assertEqual(query["per-page"], ["3"])

    def test_references_respects_the_limit(self):
        from urllib.parse import parse_qs, urlparse

        code, out, err, urls = self.run_main("--references", "W111", "--limit", "2", responses=[self.WORK, load_fixture()])
        self.assertEqual(code, 0, err)
        self.assertEqual(parse_qs(urlparse(urls[1]).query)["filter"], ["openalex:W11|W12"])

    def test_references_of_a_work_with_none_prints_an_empty_list(self):
        code, out, err, urls = self.run_main("--references", "W111", responses=[{"id": "https://openalex.org/W111"}])
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out), [])
        self.assertEqual(len(urls), 1)

    def test_from_year_filters_both_snowball_directions(self):
        code, out, err, urls = self.run_main(
            "--references", "W111", "--from-year", "2022", responses=[self.WORK, load_fixture()]
        )
        self.assertEqual([row["openalex_id"] for row in json.loads(out)], ["W333"])

    def test_a_malformed_id_is_a_usage_error_and_nothing_is_fetched(self):
        code, out, err, urls = self.run_main("--cited-by", "not-an-id", responses=[])
        self.assertEqual(code, 2)
        self.assertEqual(urls, [])

    def test_the_three_modes_are_mutually_exclusive(self):
        code, out, err, urls = self.run_main("--query", "x", "--cited-by", "W111", responses=[])
        self.assertEqual(code, 2)
        code, out, err, urls = self.run_main("--cited-by", "W111", "--references", "W111", responses=[])
        self.assertEqual(code, 2)

    def test_a_failed_request_is_exit_one_with_a_message(self):
        code, out, err, urls = self.run_main("--cited-by", "W111", responses=[so.OpenAlexError("HTTP 404")])
        self.assertEqual(code, 1)
        self.assertIn("error: OpenAlex request failed: HTTP 404", err)

    def test_query_mode_is_unchanged(self):
        code, out, err, urls = self.run_main("--query", "x", responses=[load_fixture()])
        self.assertEqual(code, 0, err)
        self.assertEqual(urls, [so.build_url("x", limit=25)])


if __name__ == "__main__":
    unittest.main()
