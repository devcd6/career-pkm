# Career Repository Split Design

**Status:** Draft for owner approval  
**Date:** 2026-10-13

## Intent

Separate job-application production from the durable career knowledge and research system. Reduce default agent context, make each repository's instructions agree with its responsibilities, and retain provenance when application work moves into interview preparation.

## Goals

- Keep `career-pkm` as the private source of truth for career history, source resumes, claims, STAR stories, and user decisions.
- Create a second private repository, provisionally named `career-applications`, for application work and its historical records.
- Support basic, role-specific company research during application tailoring and deeper reusable company and industry research in `career-pkm`.
- Support interview preparation and career-development questions from `career-pkm`, combining local career context with current web research when useful.
- Keep private career material out of web queries and preserve citations, claim IDs, source dates, and the distinction between fact and inference.
- Reduce agent context by loading only the instructions, references, and selected claims needed for the current task.

## Non-goals

- Rewriting or reconciling career facts, changing claim tiers, or resolving open decisions on the owner's behalf.
- Sending resume, claim, STAR-story, or other personal career text to web search or external services.
- Building a vector database or a general-purpose search service in the first split.
- Copying the complete Git history into the application repository. The existing history remains with `career-pkm`.
- Reworking existing application content merely to make it look newer. Existing application folders are preserved intact unless a specific validation defect is owner-approved for correction.

## Repository Responsibilities

### `career-pkm`: knowledge, research, and interview preparation

Owns `_raw/`, `resumes/`, `kb/`, the claim and resume indexes, reusable career-development material, durable employer and industry research, and future interview-prep outputs. Its normal query path starts with the local KB. It uses web research for current external facts such as employer developments, industry context, professional-development options, and credential requirements. Answers cite claim/story IDs for career facts and dated links for external facts, and label analysis as analysis rather than promoting it to KB fact.

This repository produces a per-opening claims packet for application work. The packet includes only selected claim IDs, canonical wording, tiers, permitted metrics, and any necessary role-header facts. It is an export, not a second career source of truth.

### `career-applications`: applications and tailoring

Owns the existing application folders as historical records and all future application folders. It also owns application preferences, profile-insights guidance, and the writing guide and samples needed to produce application materials. It performs lightweight company research tied to the employer and role, plus JD analysis, tailoring, cover letters, and application checks.

It receives the generated claims packet and does not load or copy the full KB, source resumes, or raw files. After submission, it produces an interview handoff packet containing the JD, submitted resume, claims-used mapping, role-specific research and source links, and known gaps. The owner carries that packet into `career-pkm` for interview preparation.

Historical interview-prep files already inside application folders remain with those historical folders. New interview preparation and reusable research are owned by `career-pkm`.

## Cross-Repository Flow

1. The owner supplies a JD to `career-pkm`; it selects and exports relevant claims and provenance to a Markdown claims packet.
2. The owner places that packet in the matching application folder in `career-applications`. The application workflow uses the packet, application preferences, and JD, and performs only role-specific company research.
3. After submission, the application workflow generates an interview handoff packet. The owner imports it into `career-pkm` when requesting interview prep.
4. Each repository writes only to its own files. Handoffs are explicit files initiated by the owner; there is no runtime shared path or automatic cross-repository write.

The handoff format must be documented and checked for required sections, source paths, claim IDs, and accidental inclusion of unrelated application files. Personal packets remain inside the two private repositories.

## Agent Context and Information Ownership

- Each repository has a short root instruction file stating its purpose, data boundary, and the task-specific skill to load.
- Application skills and commands live in `career-applications`; career query, deep research, and interview-prep skills live in `career-pkm`.
- Detailed rules live once in their owning skill or reference. Root instructions point to them only when their task applies.
- Generated indexes remain generated and are checked against their source files.
- Application tailoring must stop loading the complete claims view by default. Claim selection and export should be based on the JD and only the chosen claims should enter application context.
- Scripts and validators use explicit paths or a repository-local root; neither repository assumes the other is adjacent on disk.

## Migration and Safety

1. Inventory every tracked file currently under `applications/` and identify application-specific preferences, profile guidance, writing references, commands, skills, scripts, indexes, and documentation that must move or be updated.
2. Create the application repository separately with a clean history. Do not copy the full `career-pkm` repository or its history into it.
3. Preserve existing application folder contents as historical records. Copy files to the destination and compare file counts and SHA-256 hashes before removing anything from `career-pkm`.
4. The current `scripts/apply_plan.py` cannot write outside its repository root. The approved move inventory therefore needs a staged transfer procedure; do not bypass its path guard or delete originals as part of an unverified copy.
5. Remove application-owned content from `career-pkm` only after the destination is created, verified, and the owner approves the final removal step. `_raw/`, `resumes/`, `kb/`, and career-source history stay in `career-pkm`.
6. Update every instruction, command, script, generated index, and handoff that names the old ownership or path. Keep historical application content intact unless the owner separately approves a content correction.

The new repository's hosting, exact name, and creation are pending explicit owner approval. No remote repository is created or pushed as part of this design approval.

## Acceptance Criteria

- Each repository has one coherent purpose and no instruction tells an agent to read or write the other repository's owned files directly.
- Application sessions work from a generated claims packet and do not need the full claims view or raw career files.
- Interview prep can use the final submitted resume and claims mapping together with canonical claims and STAR stories from `career-pkm`.
- Web research keeps personal career facts local; external findings carry URLs and dates, and inferences are labeled.
- Existing application folders are present in the new repository with matching file hashes before removal from `career-pkm`.
- Root docs, commands, skills, scripts, and indexes point to current ownership and paths; stale workflow instructions are removed or clearly labeled as historical.
- Existing index and claims-view checks pass. Application, research, interview-prep, handoff, and scope validators pass for the files they own, except documented warnings or owner-approved exceptions.
- The known missing `SUMMARY` validation error in the United Way application is reviewed in the destination repo without changing a submitted document unless the owner approves the correction.
