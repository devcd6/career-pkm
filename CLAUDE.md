# Career knowledge base project

Goal: turn a folder of messy resume versions into one structured, source-cited
career knowledge base. Use the `resume-kb` skill for the workflow.

## Using this project as knowledge and context

This project's files (`kb/`, `resumes/`, `_raw/`, `INDEX.md`) may be supplied
as background knowledge with no particular task attached. When they are, read
and interpret them as follows; no purpose is assumed.

Layers: `_raw/` (original resumes, wording ground truth) -> `resumes/` (organized
copies with frontmatter) -> `kb/` (reconciled, source-cited claims) -> `INDEX.md`
(generated catalog, one row per resume with raw name and keywords). `README.md`
describes the layout. Follow `sources` in a `kb/` claim to `resumes/`, then
`source_original` to `_raw/`.

Reading `kb/roles/*.md` (one file per employer role; achievements are `### A-...`
blocks):
- `canonical` is the drafted wording; `variants` hold every original wording;
  `metrics` list the numbers; `notes` explain differences.
- `tier`: `verified` = confirmed by the user; `consistent` = 2+ versions agree;
  `single-source` = one version; `conflicting` = a fact is disputed and the
  value is not settled.
- `[A | B | C]` in a canonical line = interchangeable verb/ownership wordings
  (first is the preferred draft). `15+ [20-25]` = canonical value followed by
  other values found in versions. Bracketed values are alternatives the user
  accepts as accurate unless a conflict says otherwise.
- `Title 1 | Title 2` = title variants for the same role. The NCMW title is
  always "Project Coordinator".
- `kb/_conflicts.md`: `status: open` entries are unsettled facts (numbers,
  dates, scope, employer or credential details); do not state them as settled.
  `status: resolved` entries cite the user's words as the resolution.
- `kb/_user_decisions.md`: the user's own rulings; the authority behind any
  resolved item and any `verified` tier.
- `kb/skills.md`, `kb/education.md`, `kb/summaries.md`: skills, credentials and
  summary statements with their source resumes.

Interpretation rules:
- All active resumes carry equal weight; ignore any notion of "latest" or
  "superseded". `resumes/_archive/` holds files set aside for incomplete content
  or merged bullets; they remain valid sources for the wording they contain.
- Differences in verb, ownership, seniority or tailoring wording are variations,
  not contradictions. Number, date, scope and employer/education disagreements
  that are still open are real.
- Dates in TA4/TA6/TA7/TA8 are the user's authoritative dates. File dates are
  lower bounds taken from content, not exact.
- The KB records what the resumes say and what the user has confirmed. Do not
  add facts, round numbers, or merge distinct claims when drawing on it. Cite
  the role or source when quoting a claim.
- Personal data is present. Do not send file contents to external services.

## Hard rules

These govern building and editing the knowledge base.

1. `_raw/` is read-only. Never edit, rename, move, or delete anything in it.
2. Plan before moving. Write `_work/plan.csv`, wait for approval, then run
   `python scripts/apply_plan.py` (dry run first).
3. Never invent, inflate, round, or merge facts. Every claim in `kb/` must
   cite the resume file(s) it came from.
4. When versions disagree, record a conflict in `kb/_conflicts.md`. Never pick
   a winner. Only the user resolves conflicts.
5. Only the user can mark a claim `verified`.
6. Stop at every human gate listed in `PROGRESS.md` and wait for the user.
7. Commit to git after each phase with a message naming the phase.
8. Resumes contain personal data. Push only to the private remote
   `devcd6/career-pkm`, and only to `apply/*` and `handoff/*` branches. Push to
   `main` only on the user's explicit instruction for that push. Do not push to
   any other remote, and do not paste file contents into web searches or
   external tools.

## Application mode (branches named `apply/<YYYY-MM-DD>_<org>_<role>`)

Application work lives in `applications/<slug>/`. Facts come from `kb/` only.

- New facts, bullets, content or context surfaced during an application go first
  to `applications/<slug>/proposals.md`, each with its source (the user's words
  or a resume/JD line).
- Approval gate: write to root only after the user explicitly approves the item
  in the same session. No approval, no root write.
- Additive only. Allowed root targets: new `### A-...` blocks and new
  `variants:` or bracketed alternatives in `kb/roles/*.md`; new entries in
  `kb/skills.md`, `kb/summaries.md`, `kb/stories.md`, `kb/education.md`; new
  files in `writing/samples/`; a new `kb/_user_decisions.md` entry quoting the
  user's approval words and date; a new `kb/_conflicts.md` block when an
  addition disagrees with an existing number, date, scope or employer detail
  (never pick a winner).
- Never: touch `_raw/`; edit or delete an existing `canonical`, tier or conflict
  resolution; invent, round or merge facts; reorganize `resumes/`.
- Tier of an approved addition is `single-source` (cite the application file and
  the user's words). It is `verified` only when the user says it is accurate
  (rule 5).
- Root additions go in their own commit, `kb: add <what> (approved)`, separate
  from `applications/` commits. Rebuild `INDEX.md` and lint in that commit.
- Before finishing, `git diff --stat origin/main...HEAD` must show only
  `applications/<slug>/` plus root paths covered by an approval entry in
  `kb/_user_decisions.md` on the same branch.

## Conventions

- Naming: `YYYY-MM_<role-family>_<company-or-general>_v<N>.md`
- Dates in KB files: `YYYY-MM` or `present`
- Frontmatter: flat `key: value`, lists as `[a, b]`
- Schema details: see the skill's `references/schema.md`

## User overrides to conflict rules (take precedence over the skill's conflict-rules.md)

- Differences in bullet structure, verbs, or degree of ownership ("supported" vs
  "led", "managed" vs "directed") are NOT conflicts to escalate. Draft the best
  version as `canonical:` and put the alternative verbs/wordings in brackets,
  e.g. `[Led | Directed | Managed] billing migration`. Keep every original in `variants:`.
- Numbers, dates, scope facts and employer/education details that disagree are
  still real conflicts and go in `kb/_conflicts.md`.
- NCMW role title is always "Project Coordinator". "Junior Project Coordinator"
  and similar variants are not conflicts; record them only as title variants.

## Target (fill in)

- Target roles:
- Constraints (location, seniority, industries):
- Name as it should appear on resumes:
