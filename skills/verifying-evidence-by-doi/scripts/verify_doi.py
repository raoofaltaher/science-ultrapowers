#!/usr/bin/env python3
"""DOI verifier for the research lab (stdlib only).

Usage:
  python "${CLAUDE_PLUGIN_ROOT}/skills/verifying-evidence-by-doi/scripts/verify_doi.py" <doi> --title "<title>" --first-author <family-name> --year <year>
  python "${CLAUDE_PLUGIN_ROOT}/skills/verifying-evidence-by-doi/scripts/verify_doi.py" --search "<title>" --first-author <family-name> --year <year>
  python "${CLAUDE_PLUGIN_ROOT}/skills/verifying-evidence-by-doi/scripts/verify_doi.py" --csv research_lab/01_reference_registry/REGISTRY.csv
  python "${CLAUDE_PLUGIN_ROOT}/skills/verifying-evidence-by-doi/scripts/verify_doi.py" --extract-from <file>
  python "${CLAUDE_PLUGIN_ROOT}/skills/verifying-evidence-by-doi/scripts/verify_doi.py" <doi> --bibtex
  python "${CLAUDE_PLUGIN_ROOT}/skills/verifying-evidence-by-doi/scripts/verify_doi.py" --registry-bib <registry.csv> --out <out.bib>
  python "${CLAUDE_PLUGIN_ROOT}/skills/verifying-evidence-by-doi/scripts/verify_doi.py" <doi> --title "<title>" --first-author <family-name> --year <year> --authors "Given Family; Given Family; ..."
Exit code: 0 if all VERIFIED, 1 otherwise. With --extract-from, 1 only when a status is
RETRACTED, CONCERN, UNRESOLVED, ERROR, PREPRINT or MISMATCH (RESOLVES_UNCHECKED alone exits 0).
--search exits 1 when the Crossref search fails.
"""
import csv
import difflib
import html
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

CROSSREF_API = "https://api.crossref.org"
DOI_USER_AGENT = "science-ultrapowers-doi-verifier/0.1"
ALLOWED_URL_SCHEMES = ("https",)
DOI_REGEX = r"10\.\d{4,9}/[^\s\"<>\]\[,;{}\\|`]+"
RETRACTION_TYPES = ("retraction", "withdrawal", "removal", "retracted")
CONCERN_TYPES = ("expression_of_concern", "expression-of-concern")
EXTRACT_FAIL_STATUSES = ("RETRACTED", "CONCERN", "UNRESOLVED", "ERROR", "PREPRINT", "MISMATCH")
PREPRINT_PREFIXES = ("10.48550/", "10.2139/ssrn", "10.20944/preprints", "10.31219/", "10.36227/")


def doi_normalize(doi):
    """Strip URL/doi: prefixes and whitespace; lower-case (DOIs are case-insensitive)."""
    d = str(doi).strip()
    d = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", d, flags=re.I)
    return d.strip().rstrip(".").lower()


def doi_extract(text):
    """Return unique DOIs found in free text, in order of appearance."""
    seen, out = set(), []
    for m in re.findall(DOI_REGEX, str(text)):
        d = doi_normalize(m).rstrip(").:")
        if d not in seen:
            seen.add(d)
            out.append(d)
    return out


def crossref_get(path, params=None, retries=3):
    """GET a Crossref REST path. Returns (status_code, json_or_None)."""
    url = CROSSREF_API + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    _require_https_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": DOI_USER_AGENT})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:  # nosec B310
                return r.status, json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return 404, None
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            return e.code, None
        except urllib.error.URLError:
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            return -1, None
    return -1, None


def _require_https_url(url):
    """Raise ValueError unless `url`'s scheme is https.

    Called before every `urllib.request.urlopen` in this module (CWE-918 /
    bandit B310: an unchecked URL could point at `file://`, `ftp://` or another
    unintended scheme). Every URL this module opens is built from the fixed
    `CROSSREF_API` constant, so this should never fire in practice; it is a
    belt-and-braces guard, not a substitute for reviewing where `url` comes from.
    """
    scheme = urllib.parse.urlparse(url).scheme.lower()
    if scheme not in ALLOWED_URL_SCHEMES:
        raise ValueError("refusing to open non-https URL (scheme %r): %s" % (scheme, url))
    return url


def text_fold(s):
    """Lower-case, strip accents, collapse non-alphanumerics (for fuzzy comparison)."""
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def title_similarity(a, b):
    """SequenceMatcher ratio on folded titles; 1.0 if one folded title contains the other."""
    fa, fb = text_fold(a), text_fold(b)
    if not fa or not fb:
        return 0.0
    if fa in fb or fb in fa:
        return 1.0
    return round(difflib.SequenceMatcher(None, fa, fb).ratio(), 3)


def crossref_updates(doi, work=None):
    """All update notices (retraction/correction/EoC...) that target this DOI.

    Returns `(notices, ok)`. `ok` is False when the retraction check could not
    run: the update query answered neither 200 nor 404 (or, when `work` is not
    supplied, the work lookup did). `work` is the already-fetched `/works/<doi>`
    JSON (as returned by `crossref_get`); pass it to avoid a second request."""
    notices, code = _crossref_updates_code(doi, work)
    return notices, code in (200, 404)


def _crossref_updates_code(doi, work=None):
    """Like crossref_updates, but returns `(notices, http_code)` of the step that failed
    (the update query's own code when everything before it worked)."""
    d = doi_normalize(doi)
    notices = []
    js = work
    if js is None:
        code, js = crossref_get("/works/" + urllib.parse.quote(d, safe="/"))
        if code not in (200, 404):
            return notices, code
    if js:
        for u in js["message"].get("updated-by", []) or []:
            notices.append({"type": str(u.get("type", "")).lower(), "notice_doi": u.get("DOI"), "source": u.get("source", "")})
    code2, js2 = crossref_get("/works", {"filter": "updates:" + d, "rows": 20})
    if js2:
        for it in js2["message"].get("items", []):
            for u in it.get("update-to", []) or []:
                if doi_normalize(u.get("DOI", "")) == d:
                    notices.append({"type": str(u.get("type", "")).lower(), "notice_doi": it.get("DOI"), "source": "crossref-update-to"})
    uniq = {(n["type"], str(n["notice_doi"]).lower()): n for n in notices}
    return list(uniq.values()), code2


def _family_name_matches(supplied_family, crossref_family):
    """True iff a supplied family name is compatible with Crossref's, using
    the same fold/substring/last-token rule verify_doi has always applied to
    `first_author` (unchanged here; factored out so the new per-author check
    in the `authors` list reuses the identical rule, not a second one)."""
    fa = text_fold(supplied_family)
    cr = text_fold(crossref_family)
    return bool(fa and cr) and (
        fa == cr
        or re.search(r"\b" + re.escape(cr) + r"\b", fa) is not None
        or fa.split()[-1] == cr.split()[-1]
    )


def _split_person_name(name):
    """Best-effort split of a free-text person name into (given, family).

    Accepts "Given Family", "Given Middle Family", and the comma form
    "Family, Given". A single bare token is treated as a family name with
    no given name (initials are then simply not checked for that entry)."""
    text = str(name or "").strip()
    if not text:
        return "", ""
    if "," in text:
        family, _, given = text.partition(",")
        return given.strip(), family.strip()
    parts = text.split()
    if len(parts) == 1:
        return "", parts[0]
    return " ".join(parts[:-1]), parts[-1]


def _name_initials(given_name):
    """Fold a given name down to its bare initials: "Firoj" -> "f";
    "M. Ali" -> "ma"; "" -> ""."""
    return "".join(token[0].lower() for token in re.findall(r"[A-Za-z]+", str(given_name or "")))


def _initials_compatible(supplied_given, crossref_given):
    """True unless both sides give initials and neither is a prefix of the
    other. Empty on either side means nothing to contradict (citation styles
    omit or truncate given names inconsistently), so that case passes."""
    supplied = _name_initials(supplied_given)
    crossref = _name_initials(crossref_given)
    if not supplied or not crossref:
        return True
    return supplied.startswith(crossref) or crossref.startswith(supplied)


def _author_list_mismatches(supplied_authors, crossref_author_records):
    """Compare a supplied, ordered, full author list (free-text names read
    from the PDF in hand) against Crossref's raw `author` records position
    by position. Returns a list of human-readable problem strings (empty
    means compatible). A length mismatch is reported once; family name and
    initials are then compared up to the shorter list's length, so one added
    or dropped co-author does not mask a genuine error elsewhere in the
    list."""
    problems = []
    supplied_count, crossref_count = len(supplied_authors), len(crossref_author_records)
    if supplied_count != crossref_count:
        problems.append(
            "author count mismatch: supplied %d author(s) vs Crossref %d author(s)"
            % (supplied_count, crossref_count)
        )
    for index in range(min(supplied_count, crossref_count)):
        supplied_given, supplied_family = _split_person_name(supplied_authors[index])
        crossref_record = crossref_author_records[index]
        crossref_family = crossref_record.get("family") or crossref_record.get("name", "")
        crossref_given = crossref_record.get("given", "")
        if not _family_name_matches(supplied_family, crossref_family):
            problems.append(
                "author #%d family-name mismatch: supplied %r vs Crossref %r"
                % (index + 1, supplied_authors[index], crossref_family)
            )
            continue
        if not _initials_compatible(supplied_given, crossref_given):
            problems.append(
                "author #%d initials mismatch: supplied %r vs Crossref %r"
                % (index + 1, supplied_authors[index], ("%s %s" % (crossref_given, crossref_family)).strip())
            )
    return problems


def verify_doi(doi, title=None, first_author=None, year=None, min_title_sim=0.85, authors=None):
    """Verify one DOI against Crossref and against metadata taken FROM THE FULL TEXT IN HAND.

    Returns a dict with `status` in:
      VERIFIED            resolves, not retracted, not a preprint, and title/first-author/year match what you supplied
      RESOLVES_UNCHECKED  resolves, but you supplied no title/author/year from the PDF, so nothing was matched (NOT citable yet)
      MISMATCH            resolves to a different work than the metadata you supplied (see `problems`)
      PREPRINT            resolves to posted-content or a preprint server (Tier C: never evidence)
      RETRACTED           a retraction/withdrawal/removal notice targets this DOI (Tier X)
      CONCERN             an expression of concern targets this DOI (Tier X until resolved)
      UNRESOLVED          Crossref returns 404 (not registered with Crossref: may be DataCite or fabricated)
      ERROR               network/API failure, or the retraction check could not run; retry later (never a source)
    `corrections` lists correction/erratum/addendum notices (the work stays citable; cite the corrected version).

    `authors`, if given, is the FULL ordered author list read from the PDF in hand
    (free-text names, e.g. "Firoj Alam" or "Alam, Firoj"), checked position by
    position against Crossref's own author records for both family name and
    given-name initials -- catching a wrong co-author or a wrong initial that
    `first_author` alone (family name of author #1 only) would miss. Backward
    compatible: omitting `authors` (the default) leaves every existing check,
    and the returned dict's keys, exactly as before; passing it adds an
    `author_list_problems` key (list of strings, possibly empty) and folds any
    entries into the existing `problems`/`status` contract already in place.
    """
    d = doi_normalize(doi)
    out = {"doi": d, "status": None, "problems": [], "corrections": [], "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if d.startswith(PREPRINT_PREFIXES):
        out["status"] = "PREPRINT"
        out["problems"].append("Preprint-server DOI prefix (e.g. arXiv 10.48550, registered at DataCite): Tier C, never evidence; find the peer-reviewed version")
        return out
    code, js = crossref_get("/works/" + urllib.parse.quote(d, safe="/"))
    if code == 404:
        out["status"] = "UNRESOLVED"
        out["problems"].append("DOI not found in Crossref (check doi.org / DataCite; may be fabricated or mistyped)")
        return out
    if not js:
        out["status"] = "ERROR"
        out["problems"].append("Crossref request failed (HTTP %s)" % code)
        return out
    m = js["message"]
    crossref_author_records = m.get("author", []) or []
    out.update({
        "crossref_title": html.unescape((m.get("title") or [""])[0]),
        "crossref_authors": [
            "%s %s" % (a.get("given", ""), a.get("family", a.get("name", ""))) for a in crossref_author_records
        ],
        "crossref_first_author_family": (
            (crossref_author_records[0].get("family") or crossref_author_records[0].get("name", ""))
            if crossref_author_records
            else ""
        ),
        "crossref_year": ((m.get("issued", {}).get("date-parts") or [[None]])[0] or [None])[0],
        "venue": html.unescape((m.get("container-title") or [""])[0]),
        "type": m.get("type"),
        "publisher": m.get("publisher"),
    })
    notices, update_code = _crossref_updates_code(d, js)
    out["updates"] = notices
    kinds = [n["type"] for n in notices]
    out["corrections"] = [n for n in notices if n["type"] not in RETRACTION_TYPES + CONCERN_TYPES]
    if any(k in RETRACTION_TYPES for k in kinds) or text_fold(out["crossref_title"]).startswith("retracted"):
        out["status"] = "RETRACTED"
        return out
    if any(k in CONCERN_TYPES for k in kinds):
        out["status"] = "CONCERN"
        return out
    if update_code not in (200, 404):
        out["status"] = "ERROR"
        out["problems"].append("retraction check could not run (HTTP %s)" % update_code)
        return out
    if out["type"] == "posted-content" or d.startswith(PREPRINT_PREFIXES):
        out["status"] = "PREPRINT"
        out["problems"].append("Preprint / posted content (Tier C): find the peer-reviewed published version")
        return out
    if title is None and first_author is None and year is None:
        out["status"] = "RESOLVES_UNCHECKED"
        out["problems"].append("Supply title, first_author and year read from the PDF in hand to verify")
        return out
    if title is not None:
        sim = title_similarity(title, out["crossref_title"])
        out["title_similarity"] = sim
        if sim < min_title_sim:
            out["problems"].append("title mismatch (similarity %.2f): supplied %r vs Crossref %r" % (sim, title, out["crossref_title"]))
    if first_author is not None:
        if not _family_name_matches(first_author, out["crossref_first_author_family"]):
            out["problems"].append(
                "first-author mismatch: supplied %r vs Crossref %r" % (first_author, out["crossref_first_author_family"])
            )
    if authors is not None:
        author_list_problems = _author_list_mismatches(authors, crossref_author_records)
        out["author_list_problems"] = author_list_problems
        out["problems"].extend(author_list_problems)
    if year is not None and out["crossref_year"] is not None:
        try:
            if abs(int(year) - int(out["crossref_year"])) > 1:
                out["problems"].append("year mismatch: supplied %s vs Crossref %s" % (year, out["crossref_year"]))
        except (TypeError, ValueError):
            out["problems"].append("year not comparable: %r" % (year,))
    out["status"] = "MISMATCH" if out["problems"] else "VERIFIED"
    return out


class CrossrefSearchError(RuntimeError):
    """The Crossref bibliographic search did not answer 200."""

    def __init__(self, code):
        super().__init__("Crossref search failed (HTTP %s)" % code)
        self.code = code


def crossref_search(title, first_author=None, year=None, rows=5):
    """Find CANDIDATE DOIs for a work by bibliographic search. Candidates are NOT verified:
    confirm each against the full text, then run verify_doi with the PDF's metadata.
    Raises CrossrefSearchError when Crossref does not answer 200."""
    q = " ".join(str(x) for x in (title, first_author, year) if x)
    code, js = crossref_get("/works", {"query.bibliographic": q, "rows": rows})
    if code != 200 or js is None:
        raise CrossrefSearchError(code)
    out = []
    for it in (js or {}).get("message", {}).get("items", []):
        au = it.get("author", []) or []
        candidate_title = html.unescape((it.get("title") or [""])[0])
        out.append({
            "candidate_doi": doi_normalize(it.get("DOI", "")),
            "title": candidate_title,
            "first_author_family": (au[0].get("family") or au[0].get("name", "")) if au else "",
            "year": ((it.get("issued", {}).get("date-parts") or [[None]])[0] or [None])[0],
            "venue": html.unescape((it.get("container-title") or [""])[0]),
            "type": it.get("type"),
            "title_similarity": title_similarity(title, candidate_title),
            "label": "CANDIDATE - confirm against full text",
        })
    return sorted(out, key=lambda r: -r["title_similarity"])


def audit_dois(items, pause=0.2):
    """Batch-verify. `items`: list of DOI strings or dicts with keys doi[, title, first_author, year]."""
    results = []
    for it in items:
        if isinstance(it, dict):
            y = it.get("year")
            results.append(verify_doi(it["doi"], it.get("title") or None, it.get("first_author") or None, y if y not in ("", None) else None))
        else:
            results.append(verify_doi(it))
        time.sleep(pause)
    return results


def audit_summary(results):
    """Count statuses in a list of verify_doi results."""
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    return counts


def audit_csv(path, doi_col="doi", title_col="title", author_col="first_author", year_col="year"):
    """Verify every row of a CSV (e.g. a registry). Rows without a DOI get status NO_DOI."""
    out = []
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            d = (row.get(doi_col) or "").strip()
            if not d:
                out.append({"doi": "", "status": "NO_DOI", "title": row.get(title_col, "")})
                continue
            y = (row.get(year_col) or "").strip()
            out.append(verify_doi(d, (row.get(title_col) or "").strip() or None, (row.get(author_col) or "").strip() or None, y or None))
            time.sleep(0.2)
    return out


def evidence_card_md(card_id, claim, quote, location, doi, citation, verify_result, extracted_by, verified_by="", notes=""):
    """Render an evidence card (one claim from one source) as markdown for research_lab/01_reference_registry/evidence_cards/."""
    vr = verify_result or {}
    return (
        "### %s\n\n| Field | Value |\n|---|---|\n"
        "| Claim | %s |\n| Verbatim quote | \"%s\" |\n| Location (page/section/table) | %s |\n"
        "| Source | %s |\n| DOI | https://doi.org/%s |\n| DOI status | %s (checked %s) |\n"
        "| Corrections/updates | %s |\n| Extracted by | %s |\n| Verified by | %s |\n| Notes | %s |\n"
    ) % (card_id, claim, quote, location, citation, doi_normalize(doi), vr.get("status", "NOT RUN"), vr.get("checked_at", ""),
         ", ".join(n["type"] for n in vr.get("updates", [])) or "none", extracted_by, verified_by or "PENDING", notes)


BIBTEX_TRANSFORM = "/transform/application/x-bibtex"


def bibtex_pretty(bib):
    """One field per line for a single-line BibTeX record (brace-depth aware)."""
    out = []
    depth = 0
    for ch in bib.strip():
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        if ch == "," and depth == 1:
            out.append(",\n  ")
            continue
        out.append(ch)
    t = re.sub(r",\n  \s+", ",\n  ", "".join(out))
    if t.endswith("}"):
        t = t[:-1].rstrip() + "\n}"
    return re.sub(r"(?m)^(  month=)([A-Za-z]+)(,?)$", lambda m: m.group(1) + m.group(2)[:3].lower() + m.group(3), t)


def doi_to_bibtex(doi, key=None, retries=3, pretty=True):
    """BibTeX for one DOI via Crossref content negotiation.

    Use ONLY for sources that already passed the five checks (Tier A). `key`
    replaces Crossref's citation key (the lab uses the registry ref_id).
    Raises ValueError when Crossref does not know the DOI.
    """
    d = doi_normalize(doi)
    if not d:
        raise ValueError("not a DOI: %r" % (doi,))
    url = CROSSREF_API + "/works/" + urllib.parse.quote(d, safe="/") + BIBTEX_TRANSFORM
    _require_https_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": DOI_USER_AGENT, "Accept": "application/x-bibtex"})
    last = None
    for i in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310
                bib = resp.read().decode("utf-8", errors="replace").strip()
            if not bib.startswith("@"):
                raise ValueError("Crossref returned no BibTeX for %s" % d)
            if key:
                bib = re.sub(r"^(@\w+\{)[^,]*,", lambda m: m.group(1) + str(key) + ",", bib, count=1)
            return bibtex_pretty(bib) if pretty else bib
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise ValueError("DOI not registered with Crossref: %s" % d)
            last = e
        except urllib.error.URLError as e:
            last = e
        time.sleep(1.5 * (i + 1))
    raise RuntimeError("Crossref BibTeX request failed for %s: %s" % (d, last))


def registry_to_bib(registry_csv, out_bib=None, statuses=("ADMITTED",), key_col="ref_id", reverify=True, pause=0.2):
    """Bibliography generated from the lab registry only (never typed, never from memory or search hits).

    Emits one Crossref BibTeX record per row whose lab_status is in `statuses`, keyed by `key_col`.
    With reverify=True each DOI is re-checked with verify_doi (resolution, metadata match,
    retraction/preprint screen) at build time; anything but VERIFIED is reported, not written.
    Skipped: other statuses (e.g. PENDING_FULLTEXT, EXCLUDED_PREPRINT), rows without a DOI
    (Tier B: write that entry by hand from the approved exception), preprint DOIs, and rows
    whose retraction_status reports a retraction, withdrawal or expression of concern.
    Returns {"written": [ids], "skipped": [(id, reason)], "errors": [(id, reason)], "bib": text}.
    """
    with open(registry_csv, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    written, skipped, errors, entries = [], [], [], []
    for row in rows:
        rid = (row.get(key_col) or "").strip()
        status = (row.get("lab_status") or "").strip()
        doi = doi_normalize(row.get("doi") or "") if (row.get("doi") or "").strip() else ""
        retr = (row.get("retraction_status") or "").strip().lower()
        if status not in statuses:
            skipped.append((rid, "lab_status %s" % (status or "empty")))
            continue
        if not doi:
            skipped.append((rid, "no DOI: write a hand entry from the approved Tier B exception"))
            continue
        if doi.startswith(PREPRINT_PREFIXES):
            skipped.append((rid, "preprint DOI (Tier C)"))
            continue
        if retr and not retr.startswith(("no retraction", "n/a")) and re.search(r"retract|withdraw|remov|concern", retr):
            skipped.append((rid, "retraction_status: %s" % row.get("retraction_status")))
            continue
        if reverify:
            v = verify_doi(doi, (row.get("title") or "").strip() or None, (row.get("first_author") or "").strip() or None, (row.get("year") or "").strip() or None)
            time.sleep(pause)
            if v.get("status") != "VERIFIED":
                errors.append((rid, "re-verification %s: %s" % (v.get("status"), "; ".join(v.get("problems") or []))))
                continue
        try:
            entries.append(doi_to_bibtex(doi, key=rid))
            written.append(rid)
        except Exception as e:
            errors.append((rid, str(e)[:200]))
        time.sleep(pause)
    header = ("% Generated by verify_doi.py registry_to_bib from " + os.path.basename(registry_csv)
              + " on " + time.strftime("%Y-%m-%d") + ".\n% Tier A registry rows only, re-verified at build time. Do not edit by hand; regenerate.\n\n")
    text = header + "\n\n".join(entries) + ("\n" if entries else "")
    if out_bib:
        with open(out_bib, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    return {"written": written, "skipped": skipped, "errors": errors, "bib": text}


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Verify DOIs against Crossref (retractions, preprints, metadata match).")
    ap.add_argument("doi", nargs="*", help="DOI(s) to verify")
    ap.add_argument("--title")
    ap.add_argument("--first-author")
    ap.add_argument("--year")
    ap.add_argument("--authors", help='the FULL ordered author list from the PDF, separated by semicolons: "Given Family; Given Family; ..."')
    ap.add_argument("--search", help="bibliographic search for CANDIDATE DOIs (title)")
    ap.add_argument("--csv", help="audit a CSV with columns doi,title,first_author,year")
    ap.add_argument("--extract-from", help="extract and check every DOI in a text/tex/md file (resolution + retraction only)")
    ap.add_argument("--bibtex", action="store_true", help="print Crossref BibTeX for the given DOI(s); Tier A sources only")
    ap.add_argument("--registry-bib", help="build a .bib from REGISTRY.csv (ADMITTED rows, re-verified at build time)")
    ap.add_argument("--out", help="output .bib path for --registry-bib")
    a = ap.parse_args()
    if a.registry_bib:
        r = registry_to_bib(a.registry_bib, a.out)
        print(json.dumps({k: r[k] for k in ("written", "skipped", "errors")}, indent=2, ensure_ascii=False))
        if not a.out:
            print(r["bib"])
        return 0 if not r["errors"] else 1
    if a.bibtex:
        if not a.doi:
            ap.error("--bibtex needs at least one DOI")
        for d in a.doi:
            print(doi_to_bibtex(d))
            print()
        return 0
    if a.search:
        try:
            candidates = crossref_search(a.search, a.first_author, a.year)
        except CrossrefSearchError as error:
            print("error: %s" % error, file=sys.stderr)
            return 1
        print(json.dumps(candidates, indent=2, ensure_ascii=False))
        return 0
    if a.csv:
        res = audit_csv(a.csv)
    elif a.extract_from:
        with open(a.extract_from, encoding="utf-8", errors="replace") as fh:
            res = audit_dois(doi_extract(fh.read()))
    else:
        if not a.doi:
            ap.error("give a DOI, --search, --csv or --extract-from")
        author_list = [x.strip() for x in a.authors.split(";") if x.strip()] if a.authors else None
        res = [verify_doi(d, a.title, a.first_author, a.year, authors=author_list) for d in a.doi]
    print(json.dumps({"summary": audit_summary(res), "results": res}, indent=2, ensure_ascii=False))
    if a.extract_from:
        return 1 if any(r["status"] in EXTRACT_FAIL_STATUSES for r in res) else 0
    return 0 if all(r["status"] == "VERIFIED" for r in res) else 1


if __name__ == "__main__":
    raise SystemExit(main())
