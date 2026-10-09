#!/usr/bin/env python3
"""Build resume.md and claims-used.md for an application from kb/_views/claims.md.

Usage:
    python scripts/build_application.py applications/<slug>            # reads <slug>/spec.json
    python scripts/build_application.py applications/<slug> --check    # report only, write nothing

The spec holds the choices (which claims, which bracket options, which verb); this script
copies the claim wording verbatim so a bullet cannot drift from the KB. Review the spec,
then run scripts/check_application.py on the folder.

spec.json:
  title      heading for claims-used.md
  summary    the summary paragraph (ends with a "Committed to" or "Dedicated to" sentence)
  skills     list of "**Group:** text" lines for the skills block (KB wording)
  roles      {role id: [{"claims": [n, ...], "pick": {"0": 1}, "verb": "Served"}, ...]}
             claims: claim numbers within the role; the first supplies the bullet text, any
             others are mapped so their metrics cover numbers the first claim lacks.
             pick: which option to take for the Nth "[A | B]" group (default 0; -1 drops the group,
             as for a count alternative after a plain noun).
             Value brackets such as "6+ [six]" and groups after a number are dropped.
             verb: the starting verb; must match the first word of the bullet.
Header, publication, education and certification lines are fixed KB text below.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ROLE_META = {  # role id -> (employer heading, title, location and dates line, claim id prefix)
    "ncmw-project-coordinator": ("NATIONAL COUNCIL FOR MENTAL WELLBEING", "Project Coordinator",
                                 "Remote, DC  Oct 2025 - May 2026", "A-ncmw-project-coordinator-"),
    "ucsb-research-assistant": ("UC SANTA BARBARA", "Research Assistant",
                                "Goleta, CA  Jun 2021 - Jan 2025", "A-ucsb-research-assistant-"),
    "sanctuary-centers-housing-coordinator": ("SANCTUARY CENTERS (via United Way)",
                                              "Housing & Basic Needs Services Coordinator",
                                              "Santa Barbara, CA  Sept 2022 - Nov 2023",
                                              "A-sanctuary-centers-housing-coordinator-"),
    "asei-marketing-specialist": ("AMERICAN SOCIETY OF ENGINEERS OF INDIAN ORIGIN (ASEI)", "Marketing Specialist",
                                  "Remote, TX  Jan 2021 - Sept 2022", "A-asei-marketing-specialist-"),
    "casa-serena-program-assistant": ("CASA SERENA TREATMENT CENTERS", "Behavioral Health Program Assistant",
                                      "Santa Barbara, CA  Sept 2021 - Aug 2022", "A-casa-serena-program-assistant-"),
}

HEADER = """## **DEVIKA C. DIXIT**

Dallas, TX | (925) 719-8412 | devikadixit25@gmail.com | LinkedIn: linkedin.com/in/devikadixittexas

## **SUMMARY**

{summary}

## **WORK EXPERIENCE**
"""

TAIL = """## **PUBLICATIONS**

Plante, A., & Dixit, D. C. (2026, April 22). *Chasing the High: Why Gambling Disorder Belongs in the Addiction Conversation*. National Council for Mental Wellbeing. https://www.thenationalcouncil.org/gambling-disorder-and-addiction/

## **EDUCATION**

**University of California, Santa Barbara**
Bachelor of Arts in Communications
Goleta, CA  2025

**Santa Barbara City College**
Associates in Political Science & Communications
Santa Barbara, CA  2022

## **CERTIFICATIONS & SKILLS**

**Certifications & Training:** Google Project Management Certificate, Google Data Analytics Certificate, Adult Mental Health First Aid, CDC Federal Grants Training Certification, Motivational Interviewing (OARS)
{skills}
"""


def load_claims():
    view = (ROOT / "kb/_views/claims.md").read_text()
    return {m.group(1): {"tier": m.group(2), "canon": m.group(3)}
            for m in re.finditer(r"### (A-[\w-]+) \| (\S+)\ncanonical: (.*)\n", view)}


def resolve(canon, pick):
    """Resolve bracket groups: verb options are chosen, value alternatives are dropped."""
    out, last, gi = [], 0, 0
    for m in re.finditer(r"\[([^\]]*)\]", canon):
        out.append(canon[last:m.start()])
        body = m.group(1)
        if "|" in body:
            opts = [o.strip() for o in body.split("|")]
            choice = int(pick.get(str(gi), 0))
            gi += 1
            before = canon[:m.start()].rstrip()
            if choice != -1 and not (before and before[-1] in "+0123456789"):
                out.append(opts[choice])
        last = m.end()
    out.append(canon[last:])
    return re.sub(r"\s+,", ",", re.sub(r"\s{2,}", " ", "".join(out))).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--check", action="store_true", help="validate the spec, write nothing")
    args = ap.parse_args()
    folder = Path(args.folder)
    spec = json.loads((folder / "spec.json").read_text())
    claims = load_claims()

    resume = [HEADER.format(summary=spec["summary"])]
    used = [f"# {spec['title']}\n",
            "Format: bullet | claim ID | tier | verb. Tier from kb/_views/claims.md. Verb options resolved as "
            "set in spec.json; value brackets dropped so the canonical value stands.\n"]
    problems = []
    for role, bullets in spec["roles"].items():
        employer, title, line, prefix = ROLE_META[role]
        resume.append(f"## **{employer}**\n\n{title}\n{line}\n")
        used.append(f"\n## {employer}")
        for b in bullets:
            ids = [f"{prefix}{n:02d}" for n in b["claims"]]
            missing = [i for i in ids if i not in claims]
            if missing:
                problems.append(f"unknown claim {missing}")
                continue
            text = resolve(claims[ids[0]]["canon"], b.get("pick", {}))
            if not text.startswith(b["verb"]):
                problems.append(f"{ids[0]}: bullet starts '{text.split()[0]}', spec verb is '{b['verb']}'")
            resume.append(f"- {text}")
            used.append(f"- {text} | {', '.join(ids)} | {claims[ids[0]]['tier']} | {b['verb']}")
        resume.append("")
    resume.append(TAIL.format(skills="\n".join(spec["skills"])))

    for p in problems:
        print("ERROR", p)
    if problems:
        return 1
    if args.check:
        print("spec ok")
        return 0
    (folder / "resume.md").write_text("\n".join(resume))
    (folder / "claims-used.md").write_text("\n".join(used) + "\n")
    print(f"wrote {folder}/resume.md and claims-used.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
