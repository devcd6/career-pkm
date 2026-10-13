# Career knowledge base project

Goal: turn a folder of messy resume versions into one structured, source-cited
career knowledge base. The `resume-kb` skill was used to build the knowledge base
(it is not vendored in this repo). Job applications live in `devcd6/career-applications`; interviews and career questions use `interview-prep` and `career-advisor` here.

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
8. Resumes contain personal data. This repository may be pushed only to the
   owner's private GitHub repository `devcd6/career-pkm`, on feature branches;
   never to `main` without owner approval. The separate private repository
   `devcd6/career-applications` is owner-approved for application files only;
   its initial content is approved for direct commit to `main` on 2026-10-13.
   Never push `career-pkm` content to that remote or to other remotes. Do not
   paste file contents into web searches or external tools. In application
   sessions, only company and role text from the JD may leave the repo.
   GitHub Issues, issue comments and PR text count as external: never put
   resume or KB text in them, only claim IDs and file paths.

## Interview and career-advice mode

Job applications are produced in the separate private repository `devcd6/career-applications`; this repository does not hold application folders, tailoring skills, or application checks.

- Application-facts packets: `python scripts/rank_claims.py` ranks claims locally from a JD and keyword list; the owner selects IDs and runs `python scripts/build_claim_packet.py`, which writes only under `_work/application-packets/`. The owner copies the packet into the application repository.
- Interview handoff: the owner brings an interview packet from the application repository and runs `python scripts/import_interview_packet.py <packet.md>`, which stores it at `kb/interviews/<slug>/packet.md`. Use the `interview-prep` skill from there. Write only inside `kb/interviews/<slug>/`.
- Career questions: use the `career-advisor` skill. Save reusable research only on request, as dated notes in `kb/research/employers/` or `kb/research/industries/`.
- Facts come only from `kb/`; cite claim IDs; copy numbers exactly from `metrics`; owner rulings in `kb/_user_decisions.md` win. Label statements as fact, inference, or external (URL and date).
- Only public text (employer, role, program, credential, industry names) may leave the repo in web searches or fetches. Never send resume or KB text to external tools.
- Additions to `kb/` need the owner's explicit in-session approval, are additive only (never edit an existing `canonical`, tier or conflict resolution), and go in their own commit, `kb: add <what> (approved)`, with `INDEX.md` rebuilt and linted in it. Tier is `single-source`, or `verified` only when the owner says it is accurate (rule 5).
- Notion is a tracker only, never a fact source. Never offer to edit Notion.

## Superpowers plugin

The Superpowers plugin (brainstorming, plans, TDD, debugging, worktrees,
finishing-a-branch skills) may be enabled on the owner's account. Where it
conflicts with this file, this file wins.

- Use it only for tooling work on `tooling/*` branches (`scripts/`, `.claude/`,
  `CLAUDE.md`, tests).
- Do not use it on knowledge-base or interview work. The Hard rules replace its
  brainstorm, plan and finish steps there.
- Never let it create worktrees or branches, change the designated branch, push,
  or open a PR without the owner's instruction. Rules 2, 4, 6 and 8 still apply.
- Superpowers output and plans stay out of `kb/`.

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
  - Industries: Behavioral health and substance use nonprofits and membership associations; healthcare professional associations and medical education; public health and health services consulting/research; academic medical centers and healthcare innovation; health policy and government-facing alliances; global health nonprofits
- Name as it should appear on resumes: Devika C. Dixit

## Agent skills

### Issue tracker

Issues live in GitHub Issues for devcd6/career-pkm. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-label vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context, with this repo's real domain sources (the "Using this project as knowledge and context" section above, `kb/_user_decisions.md`, `kb/_conflicts.md`) listed in `docs/agents/domain.md`.
