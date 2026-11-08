---
name: requesting-reference-access
description: Use when a needed paper is paywalled or missing in full text, a candidate DOI needs human confirmation, or a DOI-less peer-reviewed source needs approval
---

# Requesting Reference Access

## Overview

Your human partner is the lab's References & Resources Specialist, with library and database access. Agents never try to get around paywalls.

**Core principle:** A claim waits for the full text. The abstract, the Crossref metadata and citing papers are never evidence for it.

## 1. Before filing

1. Search locally: `references/` (full texts, at the project root), `research_lab/01_reference_registry/REGISTRY.csv`, `research_lab/01_reference_registry/evidence_cards/`.
2. Get the Crossref record (title, authors, year, venue): `python "${CLAUDE_PLUGIN_ROOT}/skills/verifying-evidence-by-doi/scripts/verify_doi.py" <doi>`. Never request a retracted paper.
3. Try legitimate open access from `https://doi.org/<doi>`: publisher open-access pages, PubMed Central, institutional repositories, the authors' accepted manuscripts, each only if page 1 shows the same title and authors. Download only openly licensed full texts. A preprint of the published paper may locate a passage; the claim is confirmed in the published version.

## 2. File the request

Append one row to `research_lab/05_access_requests/ACCESS_REQUESTS.md`:

| Field | Content |
|---|---|
| REQ-id | `REQ-0001`, sequential |
| Type | `FULLTEXT` · `CONFIRM_DOI` · `APPROVAL` (Tier B exception) |
| DOI / identifier | DOI, or the official proceedings URL for Tier B |
| Citation | First author, year, title, venue (from Crossref, not from notes) |
| Requested by / date | role + date |
| Needed for | task or gate, and the exact claim(s) it must support |
| Priority | `P1` blocks a gate · `P2` this cycle · `P3` background |
| Status | `OPEN` → `FULFILLED` / `APPROVED` / `DECLINED` / `UNAVAILABLE` |
| Delivered file | path, on fulfilment |

## 3. On delivery

1. Your human partner saves the PDF as `references/<FirstAuthor>_<Year>_<ShortTitle>.pdf`.
2. The requester re-runs that command with `--title ... --first-author ... --year ...` read from page 1 of the PDF. Only `VERIFIED` passes; a mismatch means the wrong file was delivered, so reopen the request.
3. Read the needed passages, write the evidence cards, update the registry row (`PENDING_FULLTEXT` → `ADMITTED`), and set the request to `FULFILLED`.
4. `UNAVAILABLE` or `DECLINED`: the claim cannot be used. Record this in the task hand-off and find another source.

## 4. Tier B approvals (`APPROVAL` requests)

Include the official proceedings URL, confirmation that title, authors and year match that page, the reason no DOI exists, and why no Tier-A source can support the claim. The decision is logged in `research_lab/01_reference_registry/EXCEPTIONS.md` with the REQ-id.

## 5. Never

Use shadow libraries or pirate sites · bypass paywalls or DRM · ask your human partner for passwords, tokens or login details · store their account information · repeat personal information from saved publisher pages (such as logged-in-user banners).

## From a role

A role cannot ask your human partner. File the row, then put this block at the TOP of the final report, above everything else:

```
ACCESS REQUEST REQ-xxxx (P1/P2/P3): <First author Year, Title, Venue> - https://doi.org/<doi>
Needed for: <task / claim>. Please save the PDF to references/<FirstAuthor>_<Year>_<ShortTitle>.pdf
```

Never bury it lower. Meanwhile the claim waits for the full text.
