"""Regression tests for `verify_doi`'s full author-list + initials check.

Before this check existed, `verify_doi`'s only author-level check was
`first_author` (the family name of author #1 alone). A wrong CO-AUTHOR (any
author after the first) or a wrong INITIAL on any author -- including the
first -- passed silently. This suite drives the opt-in `authors=` parameter
with recorded, Crossref-shaped fixture data: dicts shaped exactly like the
`message` object Crossref's `/works/{doi}` endpoint returns (`title`,
`author[].given/family`, `issued.date-parts`, `container-title`, `type`,
`publisher` -- the only fields `verify_doi` reads), standing in for
`crossref_get`. No test in this file makes a live network call; the
DOI/title/author names are fixture placeholders, not a live-fetched record.

The original `first_author`-only contract is also pinned here: omitting
`authors` (the default) must return a dict IDENTICAL in shape to the one
`verify_doi` returned before the author-list check was added (no new keys),
for both the VERIFIED and MISMATCH cases.
"""

from __future__ import annotations

import inspect
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import verify_doi  # noqa: E402

# ---------------------------------------------------------------------------
# A recorded, Crossref-shaped `/works/{doi}` response (three authors), reused
# across most tests below. The shape matches the real Crossref REST schema;
# the DOI/title are fixture placeholders, not a live-fetched record.
# ---------------------------------------------------------------------------
THREE_AUTHOR_CROSSREF_MESSAGE = {
    "title": ["Deep learning for disaster response classification"],
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

TEST_DOI = "10.9999/example-fixture-doi"
TEST_TITLE = "Deep learning for disaster response classification"


class FakeCrossrefTestCase(unittest.TestCase):
    """Patches `crossref_get` to return the fixed, Crossref-shaped message
    for TEST_DOI (and an empty items list for any bibliographic search)."""

    def setUp(self):
        def _fake_crossref_get(path, params=None, retries=3):
            if path == "/works/" + TEST_DOI:
                return 200, {"message": THREE_AUTHOR_CROSSREF_MESSAGE}
            if path == "/works":
                return 200, {"message": {"items": []}}
            raise AssertionError(f"unexpected crossref_get path in test: {path!r}")

        patcher = mock.patch.object(verify_doi, "crossref_get", _fake_crossref_get)
        patcher.start()
        self.addCleanup(patcher.stop)


# ---------------------------------------------------------------------------
# Backward compatibility of the return contract (omitting `authors`)
# ---------------------------------------------------------------------------


class BackwardCompatibilityTests(FakeCrossrefTestCase):
    def test_omitting_authors_returns_identical_dict_to_pre_fix_behaviour(self):
        """The call shape used before the author-list check existed --
        doi/title/first_author/year, no `authors` -- must return a dict with NO
        `author_list_problems` key and the same VERIFIED status as before."""
        result = verify_doi.verify_doi(TEST_DOI, title=TEST_TITLE, first_author="Alam", year=2018)
        self.assertEqual(result["status"], "VERIFIED")
        self.assertNotIn("author_list_problems", result)
        self.assertEqual(result["problems"], [])

    def test_omitting_authors_still_catches_a_wrong_first_author(self):
        """The pre-existing `first_author` check itself is unchanged: a wrong
        first author is still a MISMATCH when `authors` is not supplied."""
        result = verify_doi.verify_doi(TEST_DOI, title=TEST_TITLE, first_author="Nakamura", year=2018)
        self.assertEqual(result["status"], "MISMATCH")
        self.assertNotIn("author_list_problems", result)
        self.assertTrue(any("first-author mismatch" in p for p in result["problems"]))


# ---------------------------------------------------------------------------
# The full author-list + initials check (opt-in via `authors=`)
# ---------------------------------------------------------------------------


class AuthorListCheckTests(FakeCrossrefTestCase):
    def test_correct_full_author_list_is_verified_with_no_problems(self):
        result = verify_doi.verify_doi(
            TEST_DOI,
            title=TEST_TITLE,
            first_author="Alam",
            year=2018,
            authors=["Firoj Alam", "Ferda Ofli", "Muhammad Imran"],
        )
        self.assertEqual(result["status"], "VERIFIED")
        self.assertEqual(result["author_list_problems"], [])

    def test_wrong_co_author_is_caught_though_first_author_check_alone_would_miss_it(self):
        """The first failure mode: a wrong CO-AUTHOR (not author #1) that the
        old, first-author-only check would never see."""
        result = verify_doi.verify_doi(
            TEST_DOI,
            title=TEST_TITLE,
            first_author="Alam",  # correct -- the old check alone would PASS this record
            year=2018,
            authors=["Firoj Alam", "Someone Else", "Muhammad Imran"],
        )
        self.assertEqual(result["status"], "MISMATCH")
        self.assertEqual(len(result["author_list_problems"]), 1)
        self.assertIn("author #2 family-name mismatch", result["author_list_problems"][0])

    def test_wrong_initial_on_first_author_is_caught(self):
        """The other failure mode: a correct family name with a WRONG initial,
        which the old check (family name only) would never see."""
        result = verify_doi.verify_doi(
            TEST_DOI,
            title=TEST_TITLE,
            first_author="Alam",  # family name alone still matches -- old check would PASS
            year=2018,
            authors=["Zeynep Alam", "Ferda Ofli", "Muhammad Imran"],
        )
        self.assertEqual(result["status"], "MISMATCH")
        self.assertEqual(len(result["author_list_problems"]), 1)
        self.assertIn("author #1 initials mismatch", result["author_list_problems"][0])

    def test_wrong_initial_on_a_co_author_is_caught(self):
        result = verify_doi.verify_doi(
            TEST_DOI,
            title=TEST_TITLE,
            first_author="Alam",
            year=2018,
            authors=["Firoj Alam", "Zeynep Ofli", "Muhammad Imran"],
        )
        self.assertEqual(result["status"], "MISMATCH")
        self.assertEqual(len(result["author_list_problems"]), 1)
        self.assertIn("author #2 initials mismatch", result["author_list_problems"][0])

    def test_author_count_mismatch_is_reported_and_remaining_positions_still_checked(self):
        """A dropped co-author is reported once as a count mismatch, and the
        positions that DO exist in both lists are still compared (so a second,
        independent error is not masked by the count mismatch)."""
        result = verify_doi.verify_doi(
            TEST_DOI,
            title=TEST_TITLE,
            first_author="Alam",
            year=2018,
            authors=["Firoj Alam", "Someone Else"],  # 2 supplied vs 3 in Crossref
        )
        self.assertEqual(result["status"], "MISMATCH")
        problems = result["author_list_problems"]
        self.assertTrue(
            any("author count mismatch: supplied 2 author(s) vs Crossref 3 author(s)" in p for p in problems)
        )
        self.assertTrue(any("author #2 family-name mismatch" in p for p in problems))

    def test_comma_form_name_is_parsed_correctly(self):
        """'Family, Given' is a common citation-manager export form and must be
        parsed the same as 'Given Family'."""
        result = verify_doi.verify_doi(
            TEST_DOI,
            title=TEST_TITLE,
            first_author="Alam",
            year=2018,
            authors=["Alam, Firoj", "Ofli, Ferda", "Imran, Muhammad"],
        )
        self.assertEqual(result["status"], "VERIFIED")
        self.assertEqual(result["author_list_problems"], [])

    def test_missing_given_name_on_supplied_side_does_not_fail_initials(self):
        """A bare family name (no given name at all) has nothing to contradict on
        initials -- only the family name is checked for that entry."""
        result = verify_doi.verify_doi(
            TEST_DOI,
            title=TEST_TITLE,
            first_author="Alam",
            year=2018,
            authors=["Alam", "Ofli", "Imran"],
        )
        self.assertEqual(result["status"], "VERIFIED")
        self.assertEqual(result["author_list_problems"], [])


class UserAgentTests(unittest.TestCase):
    def test_user_agent_names_the_plugin(self):
        self.assertEqual(verify_doi.DOI_USER_AGENT, "science-ultrapowers-doi-verifier/0.1")


class EarlyExitTests(unittest.TestCase):
    def test_authors_check_is_skipped_for_an_early_exit_status(self):
        """`authors=` must never be evaluated once `verify_doi` has already
        decided on an early-exit status (e.g. PREPRINT from the DOI prefix
        alone): `author_list_problems` must not appear, and passing `authors`
        must not raise even though no Crossref record was ever fetched."""
        result = verify_doi.verify_doi("10.48550/arxiv.9999.99999", authors=["Anybody At All"])
        self.assertEqual(result["status"], "PREPRINT")
        self.assertNotIn("author_list_problems", result)


# ---------------------------------------------------------------------------
# Direct unit tests of the helper functions (fast, no Crossref fixture)
# ---------------------------------------------------------------------------


class HelperFunctionTests(unittest.TestCase):
    def test_split_person_name_given_family_form(self):
        self.assertEqual(verify_doi._split_person_name("Firoj Alam"), ("Firoj", "Alam"))

    def test_split_person_name_given_middle_family_form(self):
        self.assertEqual(verify_doi._split_person_name("Muhammad Ali Khan"), ("Muhammad Ali", "Khan"))

    def test_split_person_name_comma_form(self):
        self.assertEqual(verify_doi._split_person_name("Alam, Firoj"), ("Firoj", "Alam"))

    def test_split_person_name_single_token(self):
        self.assertEqual(verify_doi._split_person_name("Alam"), ("", "Alam"))

    def test_split_person_name_empty(self):
        self.assertEqual(verify_doi._split_person_name(""), ("", ""))
        self.assertEqual(verify_doi._split_person_name(None), ("", ""))

    def test_name_initials_basic(self):
        self.assertEqual(verify_doi._name_initials("Firoj"), "f")
        self.assertEqual(verify_doi._name_initials("Muhammad Ali"), "ma")
        self.assertEqual(verify_doi._name_initials("M."), "m")
        self.assertEqual(verify_doi._name_initials(""), "")
        self.assertEqual(verify_doi._name_initials(None), "")

    def test_initials_compatible_prefix_rule(self):
        self.assertIs(verify_doi._initials_compatible("Firoj", "F"), True)
        self.assertIs(verify_doi._initials_compatible("F", "Firoj"), True)
        self.assertIs(verify_doi._initials_compatible("Firoj", "Firoj"), True)
        self.assertIs(verify_doi._initials_compatible("Muhammad", "Firoj"), False)

    def test_initials_compatible_empty_side_passes(self):
        self.assertIs(verify_doi._initials_compatible("", "Firoj"), True)
        self.assertIs(verify_doi._initials_compatible("Firoj", ""), True)
        self.assertIs(verify_doi._initials_compatible("", ""), True)

    def test_family_name_matches_reuses_original_first_author_rule(self):
        self.assertIs(verify_doi._family_name_matches("Alam", "Alam"), True)
        self.assertIs(verify_doi._family_name_matches("Firoj Alam", "Alam"), True)  # last-token rule
        self.assertIs(verify_doi._family_name_matches("Alam", "Ofli"), False)

    def test_author_list_mismatches_direct_unit_call(self):
        crossref_records = [
            {"given": "Firoj", "family": "Alam"},
            {"given": "Ferda", "family": "Ofli"},
        ]
        self.assertEqual(verify_doi._author_list_mismatches(["Firoj Alam", "Ferda Ofli"], crossref_records), [])
        problems = verify_doi._author_list_mismatches(["Firoj Alam", "Wrong Person"], crossref_records)
        self.assertEqual(len(problems), 1)
        self.assertIn("author #2 family-name mismatch", problems[0])


# ---------------------------------------------------------------------------
# Regression: registry_to_bib's default status filter
# ---------------------------------------------------------------------------


class RegistryToBibTests(unittest.TestCase):
    def test_registry_to_bib_default_status_filter_is_admitted_not_doi_verified(self):
        """A review confirmed the ADMITTED build is correct; the default must
        select `ADMITTED` rows, not `DOI_VERIFIED`."""
        signature = inspect.signature(verify_doi.registry_to_bib)
        self.assertEqual(signature.parameters["statuses"].default, ("ADMITTED",))


if __name__ == "__main__":
    unittest.main()
