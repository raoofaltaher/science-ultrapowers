---
name: requesting-reference-access
description: Use when a needed paper is paywalled or missing in full text, a candidate DOI needs the researcher's confirmation, or a peer-reviewed source without a DOI needs approval
---

# Requesting Reference Access

## Overview

The researcher is the lab's Principal Researcher, with library and database access. Roles never try to get around paywalls.

**Core principle:** A claim waits for the full text. The abstract, the Crossref metadata and citing papers are never evidence for it.

## 1. Before filing

1. Search locally: `references/` (full texts, at the project root), `research_lab/literature/SOURCES.csv`, `research_lab/literature/evidence_records/`.
2. Get the Crossref record (title, authors, year, venue): `python "${CLAUDE_PLUGIN_ROOT}/skills/verifying-evidence-by-doi/scripts/verify_doi.py" <doi>`. Never request a retracted paper.
3. Try legitimate open access from `https://doi.org/<doi>`: publisher open-access pages, PubMed Central, institutional repositories, the authors' accepted manuscripts, each only if page 1 shows the same title and authors. Download only openly licensed full texts. A preprint of the published paper may locate a passage; the claim is confirmed in the published version.

## 2. File the request

Append one row to `research_lab/requests/ACCESS_REQUESTS.md`, under this header:

```
| REQ-id (request) | Type | DOI or identifier | Citation (from Crossref) | Requested by and date | Needed for | Priority | Status | Delivered file |
```

The fields:

| Field | Content |
|---|---|
| REQ-id | `REQ-0001`, sequential |
| Type | `full-text request` · `DOI confirmation` · `exception approval` (a peer-reviewed work without a DOI) |
| DOI or identifier | DOI, or the official proceedings URL for an exception approval |
| Citation (from Crossref) | First author, year, title, venue (from Crossref, not from notes) |
| Requested by and date | role + date |
| Needed for | task or stage, and the exact claim(s) it must support |
| Priority | `blocks a stage` · `this cycle` · `background` |
| Status | `open` → `fulfilled` / `approved` / `declined` / `unavailable` |
| Delivered file | path, on fulfillment |

## 3. On delivery

1. The researcher saves the PDF as `references/<FirstAuthor>_<Year>_<ShortTitle>.pdf`.
2. The requester re-runs that command with `--title ... --first-author ... --year ...` read from page 1 of the PDF. Only a matched DOI passes; a mismatch means the wrong file was delivered, so reopen the request.
3. Read the needed passages, write the evidence records, update the source row (`awaiting full text` → `citable`), and set the request to `fulfilled`.
4. `unavailable` or `declined`: the claim cannot be used. Record this in the task report and find another source.

## 4. Exception approvals (`exception approval` requests)

Include the official proceedings URL, confirmation that title, authors and year match that page, the reason no DOI exists, and why no peer-reviewed source with a matched DOI can support the claim. The decision is logged in `research_lab/literature/EXCEPTIONS.md` with the REQ-id.

## 5. Never

Use shadow libraries or pirate sites · bypass paywalls or DRM · ask the researcher for passwords, tokens or login details · store the researcher's account information · repeat personal information from saved publisher pages (such as logged-in-user banners).

## From a role

A role cannot ask the researcher. File the row, then put this block at the TOP of the task report, above everything else:

```
ACCESS REQUEST REQ-xxxx (blocks a stage / this cycle / background): <First author Year, Title, Venue> - https://doi.org/<doi>
Needed for: <task / claim>. Please save the PDF to references/<FirstAuthor>_<Year>_<ShortTitle>.pdf
```

Never bury it lower. Meanwhile the claim waits for the full text.
