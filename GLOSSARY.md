# Career knowledge base

Terms for the career-pkm repo, which turns the owner's resume versions into a source-cited knowledge base and uses it to prepare job applications and interviews.

## Language

**Claim**:
One achievement or fact in a `### A-...` block in `kb/roles/*`, with canonical wording, variants, metrics, sources and a tier. Numbers in any output come only from a claim's metrics.
_Avoid_: Bullet, achievement, fact

**Story**:
A STAR-format narrative in `kb/stories.md` (`S...`), kept in the owner's own wording and used to answer interview questions. Always single-source unless the owner verifies it. A story adds context to claims; it never supplies numbers a claim lacks.
_Avoid_: Anecdote, example

**Tier**:
How well a claim is supported: `verified` (the owner confirmed it), `consistent` (two or more versions agree), `single-source` (one version), `conflicting` (a fact is disputed and unsettled). Only the owner can mark a claim verified.
_Avoid_: Confidence, rating

**Proposal**:
An unverified new fact, in the owner's words, recorded in an application's `proposals.md`. It becomes a claim only with the owner's explicit in-session approval and a separate `kb:` commit.
_Avoid_: Suggestion, draft claim

**Application**:
One job application's folder under `applications/<date>_<org>_<role>/`, holding the job description, research, analysis, resume, letter and any interview prep for that role.
_Avoid_: Job, submission

**Gate**:
A point listed in `PROGRESS.md` where work stops until the owner decides.
_Avoid_: Checkpoint, milestone
