# Plan: master resume (full superset)

Owner: Devika C. Dixit. Status: awaiting approval. No resume text written yet.

## Sources (local only, nothing leaves the repo)
- kb/roles/*.md (5 roles, 259 claim blocks), kb/skills.md, kb/education.md, kb/summaries.md
- kb/_user_decisions.md rulings win. Open conflicts are none (all resolved). Existing KB files are read-only.

## Added sources (owner instruction, this session): user-generated or verified claims in proposals
- `kb/interviews/2026-10-12_apa_center-coordinator/proposals.md`: its promoted answers are already KB claims A-ncmw-project-coordinator-121 to -127 (tier `single-source`; owner approved promotion, did not call each one accurate). They are used from `kb/roles/`, flagged as single-source. The raw answers are not used directly. Items the owner left unresolved there (a federally funded claim, the "Vice President and Senior Advisor" title, 20-25+ weekly touchpoints whose `metrics` are empty) stay out of bullets or use the KB wording only.
- `applications/2026-10-12_apa_center-coordinator/proposals.md` item 1: four Casa Serena bullets in the owner's own words (she corrected the submitted resume). Not in the KB. They go into the Casa Serena section marked as owner-provided wording, mapped to the claims it names (-11, -12, -22, -30, -20, -15, -17, -13, -14, -16), and listed in `proposals.md` for her to decide on promotion.
- The other three applications' proposals.md contain process notes and unverified suggestions, no owner-written claims; nothing is taken from them.
- Nothing is written to `kb/` or to either repository's source material.

## Outputs (all under _work/master-resume/)
- master-resume.md: single-column, plain text, single-spaced, Markdown, no page cap (per applications/preferences.md).
- claims-used.md: every bullet mapped to its claim ID(s); numbers copied exactly from `metrics`.
- proposals.md: anything the KB lacks or any gap, for the owner to decide. Nothing added to kb/.
- Run scripts/check_application.py-style checks only where they apply locally; no external services.

## Structure
1. Header: Devika C. Dixit (contact line left for the owner to fill, not in KB unless found).
2. Summary: from kb/summaries.md, general (not tailored), 4+ years experience, one mission-tie closer.
3. Skills: grouped from kb/skills.md; user-confirmed items included, nothing added.
4. Experience, reverse chronological, using KB dates and title variants "Title 1 | Title 2", no full/part-time labels:
   NCMW (Project Coordinator, Oct 2025 - May 2026, 9-14 bullets), UCSB (Jun 2021 - Jan 2025, 5-8),
   Sanctuary Centers (Sept 2022 - Nov 2023, 8-11), ASEI (Jan 2021 - Sept 2022, 4-7), Casa Serena (Sept 2021 - Aug 2022, 4-6).
5. Education/credentials: BA Communications 2025, CAPM in progress, as in kb/education.md.

## Rules applied
- Prefer `verified` tier claims; use `consistent`/`single-source` only if needed to reach the range, and flag them.
- Pick the first bracketed wording; vary the starting verb within each role from bracketed alternatives.
- Scope brackets like "15+ [20-25]": print the canonical value only. NatCon26 18+ sessions, 6,000+ attendees, newsletter 8,000+, scan "50 states and DC (51 jurisdictions)". No Recovery Ready publication status.
- No merging, rounding or promoting of facts. No em dashes in prose.

## Approval needed
Reply "approved" (or edits) and I will build the files above, then show them for review. Nothing gets committed or pushed until you say so.
