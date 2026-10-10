- [x] Phase 0 setup (copy step skipped; resumes already in _raw)
- [x] Phase 1 inventory
- [x] GATE 1 clusters confirmed (user replied 2026-10-05; decisions in kb/_user_decisions.md; open: 10 vs 20, which files are "Master versions")
- [x] Phase 2 rename plan (_work/plan.csv, dry run valid)
- [x] GATE 2 plan approved and applied
- [x] Phase 3 frontmatter tagging
- [x] Phase 4 KB extraction
- [x] Phase 5 conflicts (63 logged: 11 resolved by Gate 1 decisions, 52 open)
- [x] GATE 3 conflicts resolved (all 64 resolved; 0 open)
- [x] Phase 6 index and verification (2026-10-06: lint 0 problems; 33 resumes, 208 achievements, 0 open conflicts)

## Added 2026-10-06: TA4, TA6, TA7, TA8
- [x] copied to _raw, plan applied (user approved), frontmatter tagged, merged into kb/roles, conflicts and summaries/education/skills updated, index rebuilt (0 lint problems)
- [x] resolved 2026-10-06: C-S12 and mismatched bullets fixed, telemedicine claim verified, AI agent development / iSpring skills user-confirmed. Still open for user: TA8 same lineage as 3.md?, Target fields in CLAUDE.md


## Added 2026-10-06: archive pass
- [x] 13 resumes with incomplete content or merged bullets moved to resumes/_archive (plan: _work/plan_archive.csv, user approved); statuses now active/archived only (user: treat all resumes equally); index shows raw file refs and keywords

## Added 2026-10-08: Notion Job Hunt Hub import
- [x] read-only snapshots in _raw/notion (master pages, writing samples, Job History, Responsibilities, Achievements, Skills, STAR Story Bank)
- [x] merged into kb/roles (56 responsibilities, 18 achievements; 3 unmatched rows added as single-source blocks), kb/stories.md, kb/skills.md; user rulings in kb/_user_decisions.md
- [ ] NOT imported by instruction: Documents & Application Material, Notes, application tracker
- [x] user ruled: do not merge Master Career Profile or Record
- [ ] Push decision pending: CLAUDE.md rule 8 forbids pushing this repo; commits are local only
- [x] Notion Documents import approved and applied 2026-10-08: 10 new tailored resumes in resumes/, 10 cover letters in writing/samples/, 5 duplicates of TA4/TA6/TA7/TA8 skipped; 367 bullet wordings added as variants and 41 new verified claims in kb/roles
- [x] comparison pass 2026-10-08: summaries (S-22..S-31), skills and title wording of the 10 new resumes merged; writing samples now exact export copies
- [x] writing/style-guide.md approved by the user 2026-10-08
- [x] user ruled: leave Education/Certifications database, Deep Dive, company-title strings and Insights Discovery Profile out
- [x] writing/style-guide.md rewritten as a descriptive record (still draft, awaiting owner approval); no generation prompt kept in repo
- [x] index review 2026-10-08: INDEX.md regenerated and checked (43 resume versions, 5 roles, 252 claims, 0 open conflicts, 0 lint problems); Notion resumes and letters renamed to role/industry/angle names; raw staging copies renamed N-R##/N-L##; build_index.py extended (categories, KB, writing, Notion sections, pipe-safe cells)

## Added 2026-10-09 to 2026-10-10: application workflow
- [x] scaffold built and merged to main: claims view (kb/_views/claims.md), patched skills and slash commands in .claude/, applications/ folder, check_application.py, build_application.py, detect_ai_writing.js
- [x] CLAUDE.md rule 8 rewritten (owner approved): push only to devcd6/career-pkm on feature branches, main only with owner approval
- [x] CLAUDE.md "Application mode": application branches may add to root (kb/, writing/samples/) only after in-session owner approval, additive only, separate `kb: add <what> (approved)` commit; scripts/check_scope.py checks the diff against main
- [x] .claude/settings.json deny list reduced by the owner to _raw and PROGRESS.md
- [x] worked example: applications/2026-10-09_aamc_* (awaits owner review); MAVEN test application deleted by the owner
- [x] 2026-10-10 branch cleanup: PR #3 closed; local handoff branch deleted
- [ ] Remote branches claude/compassionate-faraday-kw5tuy, claude/testing10.9 and handoff/application-workflow still exist (fully merged); the git proxy blocked deletion, so the owner deletes them in GitHub
- [ ] Target fields in CLAUDE.md still empty (owner)
