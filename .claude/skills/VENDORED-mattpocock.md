Vendored from https://github.com/mattpocock/skills (MIT, license in LICENSE-mattpocock-skills), skills/productivity,
commit 49dd158d1076134a641b33efb035946536778336 (checked out 2026-10-09). Unmodified except that each skill's
agents/openai.yaml (Codex-only metadata) was left out.
Skills: grill-me, grilling, handoff, teach, to-questionnaire, wait-what, writing-for-agents.
Reviewed 2026-10-09: markdown only, no scripts, no network calls, no shell commands.
Installed this way because plugins do not load in cloud sessions; the plugin install failed (marketplace missing).
All but grilling and writing-for-agents set disable-model-invocation, so they run only when typed (/grill-me, /handoff, ...).
Project cautions:
- teach writes MISSION.md, lessons/, reference/, learning-records/, assets/ into the current directory. Never run it in the repo root. Use a scratch directory.
- handoff writes to $TMPDIR, outside the repo. Handoff text can contain resume or KB content: redact personal data, and do not paste it into external tools.
- grilling and grill-me ask questions only; the owner's answers still go to proposals.md, not the KB.
- wait-what expects GLOSSARY.md; this repo has none, so it falls back to plain re-pitching.
- Application sessions still write only under applications/. These skills do not change that rule.
