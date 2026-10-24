# HANDOFF: career-pkm (knowledge repository)

Updated 2026-10-24. The original single-repo application-workflow handoff is archived in `devcd6/career-applications` at `docs/history/application-workflow-handoff.md`.

- This repository owns `_raw/`, `resumes/`, `kb/`, and the interview and career-advice workflow. Rules are in `CLAUDE.md`.
- Application work happens in `career-applications`. Data crosses only as Markdown packets: application-facts packets out (`/build-packet` pushes the one approved file to the Opening's branch, ADR 0001, rule 8) and interview packets in (owner-imported).
- Open items: `PROGRESS.md` still describes the pre-split phases and is deny-listed for agents, so the owner updates it (live `applications/` folder, `check_scope.py`, push decision, empty target fields); the known United Way `SUMMARY` validation error is reviewed in the application repository, not here.
