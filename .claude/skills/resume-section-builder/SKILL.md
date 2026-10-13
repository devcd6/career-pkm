---
name: resume-section-builder
description: Build the summary and skills sections of a career-pkm resume from KB sources, tailored to a target role
---

# Resume Section Builder (career-pkm)

Original generic body replaced; see git history.

## Sections
- **Summary:** compose from statements in `kb/summaries.md` and claims. Facts only from the KB. End with one short mission-tie sentence ("Committed to...", "Dedicated to...") that matches the employer's mission without copying it; patterns are in `applications/preferences.md`.
- **Skills:** group lines from `kb/skills.md`. Include a skill or tool only if the KB lists it. Mirror JD wording only where the KB already supports the skill.
- **Education and certifications:** from `kb/education.md` and the role headers in the claims view; the standard header/tail in `scripts/build_application.py` applies.
- Experience bullets belong to `resume-bullet-writer`; titles, dates and employers come from the claims view role header.

## Rules
No invented, inflated, rounded or merged facts. Numbers only from claim metrics. Section order and layout follow `applications/preferences.md`. Write under `applications/<slug>/` only. No em dashes.
