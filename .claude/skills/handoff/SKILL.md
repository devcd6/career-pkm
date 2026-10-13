---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

> **Project override (career-pkm). Takes precedence over everything below.**
> - Save location depends on the branch. On an application branch (its diff against origin/main touches `applications/`), save the redacted handoff to `applications/<slug>/handoff.md`, overwriting the previous one, start it with a dated header, commit it with the application, and run `python scripts/check_handoff.py` on it (it must pass). The `SessionStart` hook (`scripts/session_start_handoff.sh`) prints it at the start of the next web session. On any other branch, save outside the repo as stated below and never write it into the workspace.
> - Redact personal data: the owner's name, contact details, employer-identifying text from resumes, and any pasted job-description or upload content beyond company and role. Refer to the owner as "the owner" and to repo files by path.
> - Do not paste handoff text into external tools or searches.
> - No em dashes in narrative prose.

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to the temporary directory of the user's OS (`$TMPDIR`, else `/tmp`; `%TEMP%` on Windows) - not the current workspace.

Include a "suggested skills" section in the document, naming which skills the next agent should call the Skill tool for.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
