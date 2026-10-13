# Career knowledge base project

Goal: turn a folder of messy resume versions into one structured, source-cited
career knowledge base. The `resume-kb` skill was used to build the knowledge base
(it is not vendored in this repo). For job applications, use the `apply` skill.

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
8. Resumes contain personal data. This repo may be pushed only to the owner's
   private GitHub repository (devcd6/career-pkm), on feature branches, never to
   main without the owner's approval. Do not push to any other remote, and do
   not paste file contents into web searches or external tools. In application
   sessions, only company and role text from the job description may leave the
   repo.
   GitHub Issues, issue comments and PR text count as external: never put
   resume or KB text in them, only claim IDs and file paths.

## Application mode (job applications)

Applies to sessions that tailor resumes or cover letters for a specific job.
Workflow and rules: `HANDOFF.md`, the `apply` skill, `applications/preferences.md`.

- Facts come only from `kb/` (load `kb/_views/claims.md`; regenerate with
  `python scripts/build_claims_view.py`). Cite claim IDs. Numbers are copied
  exactly from a claim's metrics. Owner rulings in `kb/_user_decisions.md` win.
- Style comes from `writing/style-guide.md` and `writing/samples/`.
- Write under `applications/<YYYY-MM-DD>_<org>_<role>/`. `_raw/` is always
  read-only. `kb/`, `resumes/`, `writing/` are read-only except for approved
  additions (below). New facts go to `proposals.md` in the application folder
  first; only the owner verifies them.
- Approved additions to root (branches `apply/<YYYY-MM-DD>_<org>_<role>`): write
  to root only after the user explicitly approves the item in the same session.
  Additive only. Allowed targets: new `### A-...` blocks and new `variants:` or
  bracketed alternatives in `kb/roles/*.md`; new entries in `kb/skills.md`,
  `kb/summaries.md`, `kb/stories.md`, `kb/education.md`; new files in
  `writing/samples/`; a new `kb/_user_decisions.md` entry quoting the user's
  approval words and date; a new `kb/_conflicts.md` block when an addition
  disagrees with an existing number, date, scope or employer detail (never pick
  a winner). Never edit or delete an existing `canonical`, tier or conflict
  resolution; never invent, round or merge facts. Tier is `single-source` (cite
  the application file and the user's words), or `verified` only when the user
  says it is accurate (rule 5). Put root additions in their own commit,
  `kb: add <what> (approved)`, and rebuild `INDEX.md` and lint in it.
- Notion is the application tracker only, never a fact source. Never offer to
  edit Notion.
- Only company and role text from the JD leaves the repo (web search or fetch).
  Never send resume or KB text to external tools.
- At the start of an application session, read `applications/<slug>/handoff.md` if it exists (the `SessionStart` hook prints it on web; read the file yourself if it did not appear). It is a redacted summary of the last session, never a fact source. Write a fresh one at the end (`apply` step 5).
- End every session by confirming `git diff --stat origin/main...HEAD` shows
  only `applications/<slug>/` plus root paths covered by an approval entry in
  `kb/_user_decisions.md` on the same branch.

## Superpowers plugin

The Superpowers plugin (brainstorming, plans, TDD, debugging, worktrees,
finishing-a-branch skills) may be enabled on the owner's account. Where it
conflicts with this file, this file wins.

- Use it only for tooling work on `tooling/*` branches (`scripts/`, `.claude/`,
  `CLAUDE.md`, tests).
- Do not use it in application mode or on knowledge-base work. The `apply`
  skill, its `plan.md` approval gate and the Hard rules replace its
  brainstorm, plan and finish steps there.
- Never let it create worktrees or branches, change the designated branch, push,
  or open a PR without the owner's instruction. Rules 2, 4, 6 and 8 still apply.
- Superpowers output and plans stay out of `applications/`, `kb/` and `writing/`.

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

- Target roles: Project Coordinator; Program Coordinator; Program Associate; Project Assistant / Project Specialist; Community Outreach / Public Education Coordinator; Coordinator, Marketing and Communications
- Constraints (location, seniority, industries):
  - Location: Remote/Hybrid in USA; Remote/Hybrid in Texas, USA; Remote/Hyrbid/On-site within 50 miles of Dallas, Texas
  - Seniority: New Grad or 1-3 years of experience
  - Industries: Behavioral health and substance use nonprofits and membership associations; healthcare professional associations and medical education; public health    and health services consulting/research; academic medical centers and healthcare innovation; health policy and government-facing alliances; global health nonprofits
- Name as it should appear on resumes: Devika C. Dixit

## Agent skills

### Issue tracker

Issues live in GitHub Issues for devcd6/career-pkm. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-label vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context, with this repo's real domain sources (the "Using this project as knowledge and context" section above, `kb/_user_decisions.md`, `kb/_conflicts.md`) listed in `docs/agents/domain.md`.
