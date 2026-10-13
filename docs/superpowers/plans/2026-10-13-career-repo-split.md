# Career Repository Split Implementation Plan

> **For agentic workers:** Use this plan task-by-task. The owner must approve the file-level migration manifest before any content is moved or removed.

**Goal:** Separate career knowledge, research, and interview preparation from job-application production while preserving provenance and minimizing default agent context.

**Architecture:** `career-pkm` remains the source of truth for career facts and owns career queries, reusable research, and future interview preparation. A new private `career-applications` repository owns application records and tailoring. Repositories exchange owner-initiated Markdown packets; neither agent writes directly into the other repository.

**Tech Stack:** Markdown instructions and records; Python standard-library scripts and `unittest`; existing Bash and JavaScript checks; Git with separate histories.

**Spec:** `docs/superpowers/specs/2026-10-13-career-repo-split-design.md`

## Global Constraints

- Keep `_raw/` read-only and preserve its contents and history.
- Do not change, verify, round, merge, or otherwise rewrite career facts or claims without the owner's approval.
- Keep both repositories private; do not create or push a remote repository until the owner explicitly approves its name and hosting.
- Update the current push allowlist in `CLAUDE.md` only after the second private remote is explicitly approved; keep all other remotes prohibited.
- Never include private resume, claim, STAR-story, or career-history text in web queries or external services.
- A claims packet contains only owner-selected claims, canonical wording, tier, allowed metrics, and needed role-header facts.
- An interview packet contains only the JD, submitted resume, claim mapping, role-specific research with sources, and known gaps.
- Do not copy the full `career-pkm` Git history into the application repository.
- Before any move, write the file-level plan, wait for owner approval, and run `scripts/apply_plan.py` in dry-run mode first. Its path guard must not be bypassed.
- Commit completed phases on `tooling/repo-split`; do not push without separate owner instruction.

## Review Focus

- A claim packet includes only selected IDs, and each copied canonical line, tier, and metrics value exactly matches the current claims view.
- Unknown, duplicate, or malformed claim IDs fail validation rather than producing a partial packet.
- The application checker works from the imported packet without a local `kb/` directory or full claims view.
- The interview workflow rejects packets missing the submitted-resume or claim-mapping sections and keeps reported questions linked to dated sources.
- Transfer validation detects a missing, extra, or byte-different file before any original is removed.

---

### Task 1: Define and Validate Cross-Repository Packets

**Files:**

- Create: `tests/test_claim_packet.py`
- Create: `scripts/build_claim_packet.py`
- Create: `scripts/check_claim_packet.py`
- Test: `tests/test_claim_packet.py`

**Interfaces:**

- Consumes: explicit claim IDs and the generated `kb/_views/claims.md`.
- Produces: `python scripts/build_claim_packet.py --claims <id,id,...> --out <file>`; a Markdown packet containing only those claims and the role-header facts required to interpret them.
- Validator: `python scripts/check_claim_packet.py <packet>`; nonzero for unknown/duplicate IDs, missing fields, canonical/tier/metrics mismatches, or unselected claims.

- [ ] **Step 1: Add failing unit tests** for exact claim copying, exact metrics preservation, unknown and duplicate IDs, and missing packet fields.
- [ ] **Step 2: Run `python -m unittest discover -s tests -p "test_claim_packet.py" -v`** and confirm the expected failures.
- [ ] **Step 3: Implement the exporter and validator** with the standard library only; keep selection explicit rather than silently choosing claims.
- [ ] **Step 4: Rerun the focused unit tests** and then `python -m unittest discover -s tests -v`.
- [ ] **Step 5: Commit** the packet contract phase.

### Task 2: Separate Knowledge and Application Workflows

**Files:**

- Modify: `.claude/skills/apply/SKILL.md`, `.claude/skills/company-research/SKILL.md`, `.claude/commands/research.md`
- Modify: `scripts/check_application.py`, `scripts/check_research.py`, `scripts/rank_claims.py`
- Create: `tests/test_application_packet.py`
- Test: the new application-packet tests and existing application/research validators

**Interfaces:**

- Application tailoring accepts the claims packet as its evidence source; it does not require a local `kb/` tree or full claims view.
- `rank_claims.py` remains in `career-pkm`; it ranks claims locally from a JD and exact keyword list, and the owner selects IDs for export.
- Career and interview-prep workflows are handled in Task 4 using the generated interview packet and canonical facts from the local KB.
- Basic role-specific company research stays with application records and covers mission, programs, role context, and sourced language only; reusable employer and industry research and future interview prep live in `career-pkm`.

- [ ] **Step 1: Write failing tests** for application validation from an imported claims packet.
- [ ] **Step 2: Run `python -m unittest discover -s tests -p "test_application_packet.py" -v`** and confirm assertions fail because packet-based validation is not implemented.
- [ ] **Step 3: Implement the smallest path and input changes** needed to remove cross-repo path assumptions.
- [ ] **Step 4: Update root instructions, glossary, handoff, commands, and skills** so each repo has one clear owner for each workflow and one authoritative copy of each rule.
- [ ] **Step 5: Run focused tests, `python scripts/build_index.py --check`, `python scripts/build_claims_view.py --check`, and all applicable application/research/interview validators.**
- [ ] **Step 6: Commit** the workflow-separation phase.

### Task 3: Prepare the Application Repository

**Files:**

- Create in the new repository: `CLAUDE.md`, `README.md`, `.gitignore`, and `.claude/settings.json`.
- Copy: all existing `applications/` folders intact, including historical interview-prep files, plus `applications/preferences.md` and `applications/profile-insights.md`.
- Copy: `writing/style-guide.md` and all 10 files in `writing/samples/`.
- Copy commands: `.claude/commands/{analyze-jd,check,cover-letter,research,tailor}.md`.
- Copy skills: `.claude/skills/{apply,avoid-ai-writing,career-biographer,company-research,competitive-cartographer,cover-letter-generator,cv-creator,job-description-analyzer,resume-ats-optimizer,resume-bullet-writer,resume-section-builder,resume-tailor}/` including each selected skill's references, scripts, examples, and licenses.
- Copy scripts: `scripts/{build_application.py,check_application.py,check_research.py,check_scope.py,check_handoff.py,session_start_handoff.sh,test_session_start_handoff.sh,detect_ai_writing.js}` and `.claude/skills/resume-tailor/scripts/exact_phrase_matcher.py`.
- Copy app-specific tests: `tests/test_application_packet.py`.
- Archive: copy the current `HANDOFF.md` to `docs/history/application-workflow-handoff.md` in the application repository; replace the KB repo's handoff with current knowledge-repo guidance.
- Retain general KB and maintenance tools in `career-pkm`, including `scripts/build_index.py`, `scripts/build_claims_view.py`, `scripts/check_interview_prep.py`, and `scripts/apply_plan.py`.

**Interfaces:**

- Receives: the application-specific file inventory and the claims packet contract from Tasks 1 and 2.
- Produces: a private application repository with fresh history and no `_raw/`, `resumes/`, or full `kb/` copy.

- [ ] **Step 1: Complete the ownership audit** for every command, skill, script, settings hook, and documentation pointer; record any ambiguous ownership for owner decision.
- [ ] **Step 2: Obtain explicit owner approval** for the exact repository name, hosting, and remote creation before creating a remote.
- [ ] **Step 3: Create the new repository** with only the selected application files and updated app-specific guidance; do not copy full history.
- [ ] **Step 4: Run the application checks** in the new repository using a representative imported claims packet.
- [ ] **Step 5: Commit** the new repository bootstrap phase after the owner confirms its privacy and contents.

### Task 4: Build the Interview Handoff and Knowledge Query Path

**Files:**

- Create in the application repository: interview-packet output instructions, `scripts/build_interview_packet.py`, `scripts/check_interview_packet.py`, and `tests/test_build_interview_packet.py`.
- Create in `career-pkm`: `.claude/skills/career-advisor/SKILL.md`, interview-packet intake instructions, and `tests/test_interview_intake.py`.
- Modify in `career-pkm`: `.claude/skills/interview-prep/SKILL.md`, `.claude/commands/interview-prep.md`, and `scripts/check_interview_prep.py`.

**Interfaces:**

- Application repo produces a dated Markdown interview packet from the JD, actual submitted resume, claims-used mapping, role research/source ledger, and open gaps.
- `career-pkm` stores each imported packet and prep under `kb/interviews/<application-slug>/`; it stores reusable employer and industry research as dated notes under `kb/research/employers/` and `kb/research/industries/`.
- `career-pkm` reads the packet, then joins it with local claims, stories, user decisions, and on-demand web research.
- Career Q&A starts with the local KB and adds dated external sources when the question needs current career strategy, skills development, professional development, credential, or industry information. It saves new research only when requested.

- [ ] **Step 1: Add failing tests** for complete and incomplete interview-packet generation and intake, including source and claim references.
- [ ] **Step 2: Run `python -m unittest discover -s tests -p "test_build_interview_packet.py" -v` in the application repository and `python -m unittest discover -s tests -p "test_interview_intake.py" -v` in `career-pkm`; confirm assertions fail because the packet behaviors are missing.
- [ ] **Step 3: Implement packet generation and intake** without adding a database or external retrieval service.
- [ ] **Step 4: Add the career-advisor entry point** with explicit fact, inference, and external-research labeling and privacy boundaries.
- [ ] **Step 5: Rerun both focused test commands and `python scripts/check_interview_prep.py kb/interviews/<application-slug>`** against the migrated example.
- [ ] **Step 6: Commit** the interview and career-query phase.

### Task 5: Transfer Files and Remove Stale Ownership

**Files:**

- Modify: `_work/plan.csv` only after preserving its completed historical contents in Git history
- Transfer: approved files from `applications/`, application preferences/profile guidance, application writing references, application-owned `.claude/` files, and application-owned scripts
- Update: generated indexes and all remaining documentation and tool references
- Update: `CLAUDE.md` (including the private-remote allowlist), `README.md`, `GLOSSARY.md`, `HANDOFF.md`, `PROGRESS.md`, `.claude/settings.json`, and `scripts/build_index.py` in `career-pkm` after the app repository is verified.
- Test: file manifest/hash comparison and repository validators

- [ ] **Step 1: Produce the exact path-by-path `_work/plan.csv`** with in-repository staging destinations; do not use globs or external paths that `apply_plan.py` rejects.
- [ ] **Step 2: Stop for owner approval of that exact manifest.**
- [ ] **Step 3: Run `python scripts/apply_plan.py _work/plan.csv`** and inspect the dry run; apply only after the approved plan validates.
- [ ] **Step 4: Transfer staged files to the approved application repository** and compare relative paths, file counts, and SHA-256 hashes.
- [ ] **Step 5: Stop for owner approval before removing the source and staging copies.** Keep every original until the destination verification passes.
- [ ] **Step 6: Update generated indexes and remove stale single-repo instructions, then search all tracked files for old ownership/path assumptions.**
- [ ] **Step 7: Run all KB, packet, application, research, interview-prep, handoff, and scope checks; document the known United Way `SUMMARY` error without changing submitted content unless approved.**
- [ ] **Step 8: Commit** the verified migration and cleanup phase. Do not push without owner instruction.

## Execution Recommendation

Use native, sequential execution. Packet contracts, repository setup, and file transfer have blocking dependencies and explicit human gates; parallel implementation would risk mismatched paths or moving files before the destination is ready. The task observer should pause at each owner-approval gate rather than treating the plan as blanket permission to move data.
