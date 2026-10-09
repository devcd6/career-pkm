---
name: "resume-tailor"
description: >
  Tailor a resume to a job description by extracting keywords, scoring match,
  and rewriting bullets for impact. Use when applying to a role, optimizing
  for ATS keyword match, or customizing a cover letter.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: personal-productivity
  domain: career
  updated: 2026-05-04
  python-tools: exact_phrase_matcher.py
  tech-stack: ATS, job-search
---

> **Project override (career-pkm). Takes precedence over everything below.**
> - Facts come only from `kb/_views/claims.md` (claim IDs, canonical wording, tier, metrics) and `kb/` rulings in `kb/_user_decisions.md`. Never invent, inflate, round, estimate, or merge facts. Numbers are copied exactly from a claim's `metrics`.
> - Do not add skills, tools, credentials, scope or outcomes the KB lacks. Where the job asks for something the KB does not show, state it as a real gap and ask the owner. Frame gaps in the cover letter, never with resume overreach.
> - Write output only under `applications/<YYYY-MM-DD>_<org>_<role>/`. `kb/`, `resumes/`, `writing/`, `_raw/` are read-only. New facts go to `proposals.md` in that folder.
> - Web search or fetch may use only the employer and role named in the job description. Never send resume or KB text to any external tool.
> - Notion is the application tracker only. It is not a fact source, and never offer to edit it.
> - No em dashes in narrative prose. Follow `applications/preferences.md` and `writing/style-guide.md`.
> - Generic examples, placeholder numbers and sample names in this skill are illustrative only. They are not the owner's facts.
> - The old keyword-overlap `resume_matcher.py` is removed; use `scripts/exact_phrase_matcher.py` (exact JD phrases, no stemming or synonyms). Do not use keyword overlap as a score of fit.
> - Tailoring rules are in `applications/preferences.md` (bullet ranges per role, no page-length cap, output as a markdown code block and saved to `resume.md`, single spacing, unique high-impact starting verb per role chosen from the claim's bracketed alternatives, summary ends with a short mission-tie sentence). Also write `claims-used.md` mapping every bullet to a claim ID and the verb chosen.
> - Check `applications/` and `INDEX.md` for an existing version for the same employer before starting.
> - Ignore the "Two pages max" best practice and the "quantify wherever possible" step below.

# Resume Tailor

Tailor a base resume to a specific job description with keyword-match scoring, gap analysis, and rewritten-bullet suggestions.

---

## Table of Contents

- [Keywords](#keywords)
- [Quick Start](#quick-start)
- [Core Workflows](#core-workflows)
- [Tools](#tools)
- [Reference Guides](#reference-guides)
- [Templates](#templates)
- [Best Practices](#best-practices)

---

## Keywords

resume, CV, job application, ATS, applicant tracking system, keyword match, resume tailoring, cover letter, job description, hiring, recruiter, career, job search, bullet rewrite, accomplishment, impact statement

---

## Clarify First

Before tailoring the resume, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target job description** — the verbatim JD; it drives keyword extraction and the entire match score
- [ ] **Base resume content** — your actual experience and bullets; without it there is nothing to score or rewrite
- [ ] **Target seniority / title** — IC vs lead vs exec sets which keywords matter and the altitude of rewritten bullets
- [ ] **Truth boundary** — which listed skills you genuinely have vs. aspirational, so additions are honest rather than keyword-stuffed

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

---

## Quick Start

### Tailor a Resume in 5 Minutes

1. Save the job description as `jd.txt`
2. Save your base resume text as `resume.md`
3. Run the matcher:
   ```bash
   python .claude/skills/resume-tailor/scripts/exact_phrase_matcher.py --jd jd.txt --resume resume.md --phrases keywords.txt
   ```
4. Review the keyword-gap report
5. Rewrite low-scoring bullets using `references/bullet_rewrite_patterns.md`
6. Cross-check the final resume against the rewritten template in `assets/tailored_resume_template.md`

---

## Core Workflows

### Workflow 1: Match Score and Keyword Gap

**Goal:** Get a quantitative score for how well the current resume matches a target job description before submitting.

**Steps:**
1. Capture the job description verbatim into `jd.txt`
2. Run: `python .claude/skills/resume-tailor/scripts/exact_phrase_matcher.py --jd jd.txt --resume resume.md --phrases keywords.txt`
3. Review the score — anything below 70% means significant gaps
4. Read the missing-keywords list; classify each as (a) skills you have but did not list, (b) skills you do not have, (c) buzzwords that do not apply
5. Add (a) to the resume; ignore (c); be honest about (b)

**Expected Output:** A score, a kept-keyword list, and a missing-keyword list.

**Time Estimate:** 5-10 minutes per job description.

### Workflow 2: Bullet Rewrite for Impact

**Goal:** Convert task-oriented bullets ("responsible for…") into impact bullets that match recruiter and ATS expectations.

**Steps:**
1. Identify weak bullets — anything starting with "Responsible for" or "Helped with"
2. Apply the **CAR pattern** (Challenge, Action, Result) from `references/bullet_rewrite_patterns.md`
3. Quantify wherever possible (percentages, dollar amounts, time saved, scale)
4. Re-run the matcher to confirm score improvement

**Expected Output:** Bullet list rewritten in CAR format with metrics.

**Time Estimate:** 5 minutes per bullet.

### Workflow 3: Cover Letter Hooks

**Goal:** Pull the strongest 3-5 hooks from the resume that map directly to the top requirements in the job description.

**Steps:**
1. Run matcher in JSON mode: `python .claude/skills/resume-tailor/scripts/exact_phrase_matcher.py --jd jd.txt --resume resume.md --phrases keywords.txt --json`
2. Take the top 5 matched keywords by relevance
3. For each, find the matching resume bullet
4. Use them as evidence sentences in the cover letter

**Expected Output:** 3-5 evidence sentences for the cover letter.

**Time Estimate:** 10 minutes.

---

## Tools

### exact_phrase_matcher.py

Reads a JD text file, a resume file and a phrases file (one exact JD phrase per line), and returns, per phrase, the count in the JD and in the resume, flags phrases not in the JD, and flags phrases missing from the resume. Matching is exact, case-insensitive and whole-word. `--suggest N` lists frequent exact 1-3 word phrases from the JD to help pick phrases.

```bash
python .claude/skills/resume-tailor/scripts/exact_phrase_matcher.py --jd jd.txt --resume resume.md --phrases keywords.txt
python .claude/skills/resume-tailor/scripts/exact_phrase_matcher.py --jd jd.txt --resume resume.md --phrases keywords.txt --json
python .claude/skills/resume-tailor/scripts/exact_phrase_matcher.py --jd jd.txt --suggest 30
```

---

## Reference Guides

- **`references/bullet_rewrite_patterns.md`** — CAR pattern, action-verb library, quantification examples, weak-phrase blacklist
- **`references/ats_optimization_guide.md`** — How ATS parses resumes, formatting do's and don'ts, keyword density bounds

---

## Templates

- **`assets/tailored_resume_template.md`** — A bare resume skeleton with section ordering, length guidance, and keyword-placement notes. Fill in your content.

---

## Best Practices

- **Tailor every time.** A generic resume sent to ten roles performs worse than ten tailored versions.
- **Honesty over keyword stuffing.** Add only skills you actually have. Hiring managers can tell.
- **Keep one master resume.** Tailor variants from a single source of truth.
- **Two pages max.** Even for senior roles, two pages is the ceiling outside academia.
- **Plain text, single-column.** ATS systems still mishandle tables, graphics, and multi-column layouts.

---

## Integration Points

- Pairs with `personal-productivity/lead-researcher/` for prepping informational interviews
- Pairs with `marketing/copywriting/` for cover letter prose quality
- Used by `agents/personas/` workflows when authoring sample profiles
