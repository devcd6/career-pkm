---
name: apply
description: Run the five-step job application workflow (research, analyze JD, tailor resume, cover letter, check) grounded in the career-pkm knowledge base. Use when the owner gives a job description or says she is applying to a role.
---

# apply

Orchestrates one application. Read `CLAUDE.md` (Application mode), `applications/preferences.md`, `writing/style-guide.md` and load all of `kb/_views/claims.md` first. Open a role file in `kb/roles/` only to see variants for one claim ID.

Slug: `applications/<YYYY-MM-DD>_<org>_<role>/` (lowercase, hyphens). Before starting, look in `applications/` and `INDEX.md` for an existing version for the same employer and tell the owner. Every step saves its file and also prints to chat. Stop between steps when the owner wants to review, and ask rather than assume.

1. **/research** (`research.md`). Deep company and team research: mission, language, hiring patterns, team members, reviews. Web queries contain only the employer and role named in the JD, never resume or KB text. Mark estimates as estimates and cite sources.
2. **/analyze-jd** (`keywords.md`, `match.md`). Use the `job-description-analyzer` skill with the exact-phrase rules in preferences. `match.md` has the match score, real gaps, open questions. Use `resume-tailor/scripts/exact_phrase_matcher.py` for phrase counts. Flag "forced keywords" (hard filters the JD requires verbatim).
3. **/tailor** (`resume.md`, `claims-used.md`). Use `resume-tailor`, `resume-bullet-writer`, `resume-section-builder` and `resume-ats-optimizer`. Every bullet maps to a claim ID; `claims-used.md` lists bullet, claim ID, tier and verb chosen from the claim's brackets. Titles, dates and employer names come from the role header in the claims view. Re-screen each bullet as listed in preferences. Print the resume in a markdown code block.
4. **/cover-letter** (`cover-letter.md`). Use `cover-letter-generator` with `writing/style-guide.md` and the two closest samples in `writing/samples/`. Frame gaps honestly here. Numbers only from claim metrics.
5. **/check**. Run `python scripts/check_application.py applications/<slug>` and `node scripts/detect_ai_writing.js applications/<slug>/cover-letter.md` and the vendored `avoid-ai-writing` skill in detect mode on cover-letter.md (never rewrite or edit mode on resume.md), then confirm `git status` shows no change outside `applications/`. Report failures; do not weaken the checks.

Rules that never bend: no invented, inflated, rounded or merged facts; new facts go to `proposals.md`; never offer to edit Notion; the owner marks anything verified.
