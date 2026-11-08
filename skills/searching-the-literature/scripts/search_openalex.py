#!/usr/bin/env python3
"""Find candidate works in OpenAlex and print them as a JSON list.

Usage:
  python "${CLAUDE_PLUGIN_ROOT}/skills/searching-the-literature/scripts/search_openalex.py" --query "<text>" [--limit 25] [--from-year Y] [--json-in FILE]
  python "${CLAUDE_PLUGIN_ROOT}/skills/searching-the-literature/scripts/search_openalex.py" --cited-by <OpenAlex id> [--limit 25] [--from-year Y]
  python "${CLAUDE_PLUGIN_ROOT}/skills/searching-the-literature/scripts/search_openalex.py" --references <OpenAlex id> [--limit 25] [--from-year Y]

--cited-by lists the works that cite the given work (forward snowball); --references
lists the works it cites (backward snowball). The output shape is the same as --query.
The output is candidates, never sources: a role screens them, and
science-ultrapowers:verifying-evidence-by-doi checks each one against Crossref before
anything cites it. Record each query and its screening decisions in the screening log, a
file in research_lab/literature/search_logs/.
"""

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API_ORIGIN = "https://api.openalex.org/"
API_BASE = API_ORIGIN + "works"
USER_AGENT = "science-ultrapowers-literature-search/0.2.0"
TIMEOUT_SECONDS = 30
BACKOFF_SECONDS = (1, 2)
MAX_PER_PAGE = 200
DOI_PREFIX = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:)", re.IGNORECASE)
ARXIV_DOI_PREFIX = "10.48550/"
OPENALEX_ID = re.compile(r"^W\d+$")
REFERENCE_CHUNK = 50
ROW_KEYS = ("doi", "title", "year", "type", "venue", "is_preprint", "openalex_id")


class OpenAlexError(Exception):
    """A request to OpenAlex failed for good."""


def build_url(query, limit=25, from_year=None):
    params = {"search": query, "per-page": limit}
    if from_year is not None:
        # "from year Y" means publication year Y or later, so the filter is > Y-1.
        params["filter"] = f"publication_year:>{from_year - 1}"
    return f"{API_BASE}?{urllib.parse.urlencode(params)}"


def _clean_doi(raw):
    if not raw:
        return None
    return DOI_PREFIX.sub("", raw.strip())


def _openalex_id(raw):
    if not raw:
        return None
    return raw.rstrip("/").rsplit("/", 1)[-1]


def normalize_openalex_id(text):
    """`W123`, `w123` or `https://openalex.org/W123` -> `W123`; None when it is not an OpenAlex work id."""
    candidate = (_openalex_id(str(text).strip()) or "").upper()
    return candidate if OPENALEX_ID.match(candidate) else None


def build_work_url(openalex_id):
    return f"{API_BASE}/{openalex_id}"


def build_cites_url(openalex_id, limit=25, cited_by_api_url=None):
    """URL listing the works that cite `openalex_id`. The work's own `cited_by_api_url` is used
    only when it points at api.openalex.org; anything else is data from the network and is ignored."""
    if cited_by_api_url and cited_by_api_url.startswith(API_ORIGIN) and "?" in cited_by_api_url:
        return f"{cited_by_api_url}&{urllib.parse.urlencode({'per-page': limit})}"
    return f"{API_BASE}?{urllib.parse.urlencode({'filter': 'cites:' + openalex_id, 'per-page': limit})}"


def build_references_url(openalex_ids):
    params = {"filter": "openalex:" + "|".join(openalex_ids), "per-page": len(openalex_ids)}
    return f"{API_BASE}?{urllib.parse.urlencode(params)}"


def snowball_payload(mode, openalex_id, limit):
    """Fetch the work, then the works it cites (`references`) or the works citing it (`cited-by`)."""
    work = fetch(build_work_url(openalex_id))
    if mode == "cited-by":
        return fetch(build_cites_url(openalex_id, limit, work.get("cited_by_api_url")))
    reference_ids = [i for i in (_openalex_id(r) for r in work.get("referenced_works") or []) if i][:limit]
    results = []
    for start in range(0, len(reference_ids), REFERENCE_CHUNK):
        chunk = reference_ids[start:start + REFERENCE_CHUNK]
        results.extend(fetch(build_references_url(chunk)).get("results") or [])
    return {"results": results}


def parse_works(payload):
    rows = []
    for work in payload.get("results") or []:
        location = work.get("primary_location") or {}
        source = location.get("source") or {}
        doi = _clean_doi(work.get("doi"))
        work_type = work.get("type")
        is_preprint = work_type == "preprint" or bool(doi and doi.startswith(ARXIV_DOI_PREFIX))
        rows.append(
            {
                "doi": doi,
                "title": work.get("title"),
                "year": work.get("publication_year"),
                "type": work_type,
                "venue": source.get("display_name"),
                "is_preprint": is_preprint,
                "openalex_id": _openalex_id(work.get("id")),
            }
        )
    return rows


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(len(BACKOFF_SECONDS) + 1):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:  # before URLError: it is a subclass
            reason = f"HTTP {error.code}"
            retry = error.code == 429 or error.code >= 500
        except OSError as error:  # URLError, timeouts and connection resets while reading
            reason = getattr(error, "reason", error)
            retry = True
        except ValueError as error:  # invalid JSON or a body that is not UTF-8
            reason = f"invalid response body ({error})"
            retry = False
        if not retry or attempt == len(BACKOFF_SECONDS):
            raise OpenAlexError(str(reason))
        time.sleep(BACKOFF_SECONDS[attempt])


def _positive_limit(text):
    value = int(text)
    if not 1 <= value <= MAX_PER_PAGE:
        raise argparse.ArgumentTypeError(f"must be between 1 and {MAX_PER_PAGE}")
    return value


def build_parser():
    parser = argparse.ArgumentParser(
        description="Find candidate works in OpenAlex. Results are candidates, never sources.",
        epilog="Record each query and its screening decisions in the screening log, a file in research_lab/literature/search_logs/.",
    )
    parser.add_argument("--query", help="search text (required unless --json-in is given)")
    parser.add_argument("--limit", type=_positive_limit, default=25, help="works to return, 1-200 (default 25)")
    parser.add_argument("--cited-by", metavar="ID", help="OpenAlex work id (W123): list the works that cite it")
    parser.add_argument("--references", metavar="ID", help="OpenAlex work id (W123): list the works it cites (its referenced_works)")
    parser.add_argument("--from-year", type=int, help="only works published in this year or later")
    parser.add_argument("--json-in", metavar="FILE", help="read an OpenAlex payload from FILE instead of the network")
    return parser


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(argv)
    modes = [name for name, value in (("--query", args.query), ("--cited-by", args.cited_by), ("--references", args.references)) if value]
    if len(modes) > 1:
        parser.error("give only one of --query, --cited-by and --references")
    if args.json_in is None and not modes:
        parser.error("--query (or --cited-by or --references) is required unless --json-in is given")
    snowball_mode, snowball_id = None, None
    if args.json_in is None and not args.query:
        snowball_mode = "cited-by" if args.cited_by else "references"
        snowball_id = normalize_openalex_id(args.cited_by or args.references)
        if snowball_id is None:
            parser.error(f"--{snowball_mode} needs an OpenAlex work id such as W2741809807")

    if args.json_in is not None:
        try:
            with open(args.json_in, encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, ValueError) as error:
            print(f"error: cannot read {args.json_in}: {error}", file=sys.stderr)
            return 2
    else:
        try:
            if snowball_mode:
                payload = snowball_payload(snowball_mode, snowball_id, args.limit)
            else:
                payload = fetch(build_url(args.query, limit=args.limit, from_year=args.from_year))
        except OpenAlexError as error:
            print(f"error: OpenAlex request failed: {error}", file=sys.stderr)
            return 1

    rows = parse_works(payload)
    if snowball_mode and args.from_year is not None:
        rows = [row for row in rows if row["year"] is not None and row["year"] >= args.from_year]
    print(json.dumps(rows, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
