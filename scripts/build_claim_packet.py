#!/usr/bin/env python3
"""Build a selected, source-traceable application-facts packet."""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLAIMS_VIEW = ROOT / "kb" / "_views" / "claims.md"
SUMMARIES = ROOT / "kb" / "summaries.md"
SKILLS = ROOT / "kb" / "skills.md"
EDUCATION = ROOT / "kb" / "education.md"
DECISIONS = ROOT / "kb" / "_user_decisions.md"
PACKET_DIR = ROOT / "_work" / "application-packets"
ROLE_FIELDS = ("employer", "title", "dates", "location")
EDUCATION_FIELDS = ("degree", "institution", "location", "end", "honors", "tier")
CERTIFICATE_FIELDS = ("accepted names", "user decision", "status as written", "date", "tier")
PUBLICATION_FIELDS = ("authors", "date", "title", "publisher", "url", "tier")


def parse_claims(text):
    roles, claims, claim_order = {}, {}, []
    current_role = None
    current_claim = None

    for line in text.splitlines():
        if line.startswith("# "):
            current_role = None
            current_claim = None
            continue

        if line.startswith("## "):
            current_role = line[3:].strip()
            roles[current_role] = {"id": current_role, "claims": []}
            current_claim = None
            continue

        if current_role is None:
            continue

        if line.startswith("### "):
            match = re.fullmatch(r"### (A-\S+) \| (\S+)", line)
            if not match:
                current_claim = None
                continue
            current_claim = match.group(1)
            claims[current_claim] = {
                "role": current_role,
                "tier": match.group(2),
            }
            roles[current_role]["claims"].append(current_claim)
            claim_order.append(current_claim)
            continue

        if line.startswith(("employer: ", "title: ", "dates: ", "location: ")) and current_claim is None:
            field, _, value = line.partition(": ")
            roles[current_role][field] = value
        elif current_claim is not None:
            match = re.match(r"^(canonical|metrics): ?(.*)$", line)
            if match:
                claims[current_claim][match.group(1)] = match.group(2)

    return roles, claims, claim_order


def parse_summaries(path=SUMMARIES):
    text = path.read_text(encoding="utf-8")
    headings = list(re.finditer(r"^## (S-\d{2})\s*$", text, re.MULTILINE))
    summaries = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        body = text[heading.end():end]
        summary_lines = [line[2:] for line in body.splitlines() if line.startswith("> ")]
        if summary_lines:
            summaries[heading.group(1)] = " ".join(summary_lines)
    return summaries


def parse_education(path=EDUCATION):
    text = path.read_text(encoding="utf-8")
    headings = list(re.finditer(r"^### ((?:EDU|CERT|PUB)-\d+) (.+)$", text, re.MULTILINE))
    entries = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        body = text[heading.end():end]
        fields = {}
        for line in body.splitlines():
            if line == "variants:" or line.startswith("variants ("):
                break
            match = re.match(r"^([a-z][a-z _-]*):\s*(.*)$", line)
            if match and match.group(1) != "sources":
                fields[match.group(1)] = match.group(2)
        entries[heading.group(1)] = {"title": heading.group(2), **fields}
    return entries


def parse_skills(path=SKILLS):
    names = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if " | " not in line or line.startswith(("#", "|")):
            continue
        name = line.split(" | ", 1)[0].strip()
        if name:
            names.append(name)
    return names


def validate_output_path(path):
    try:
        path.resolve().relative_to(PACKET_DIR.resolve())
    except ValueError as error:
        raise ValueError(f"output must be under {PACKET_DIR.relative_to(ROOT)}") from error


def build_packet(selected_ids, summaries=(), education=(), skills=(), rulings=(), source_path=CLAIMS_VIEW):
    if not selected_ids or any(not claim_id for claim_id in selected_ids):
        raise ValueError("at least one claim ID is required")
    if len(selected_ids) != len(set(selected_ids)):
        raise ValueError("duplicate claim ID in selection")

    roles, claims, _ = parse_claims(source_path.read_text(encoding="utf-8"))
    unknown = [claim_id for claim_id in selected_ids if claim_id not in claims]
    if unknown:
        raise ValueError("unknown claim ID(s): " + ", ".join(unknown))

    available_summaries = parse_summaries()
    unknown_summaries = [summary_id for summary_id in summaries if summary_id not in available_summaries]
    if unknown_summaries:
        raise ValueError("unknown summary ID(s): " + ", ".join(unknown_summaries))
    if len(summaries) != len(set(summaries)):
        raise ValueError("duplicate summary ID in selection")

    available_education = parse_education()
    unknown_education = [entry_id for entry_id in education if entry_id not in available_education]
    if unknown_education:
        raise ValueError("unknown education ID(s): " + ", ".join(unknown_education))
    if len(education) != len(set(education)):
        raise ValueError("duplicate education ID in selection")

    available_skills = parse_skills()
    unknown_skills = [skill for skill in skills if skill not in available_skills]
    if unknown_skills:
        raise ValueError("unknown skill(s): " + "; ".join(unknown_skills))
    if len(skills) != len(set(skills)):
        raise ValueError("duplicate skill in selection")

    decision_log = DECISIONS.read_text(encoding="utf-8")
    log_lines = [re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", line).strip() for line in decision_log.splitlines()]
    unknown_rulings = [
        ruling for ruling in rulings
        if not ruling.strip() or (f'"{ruling}"' not in decision_log and ruling.strip() not in log_lines)
    ]
    if unknown_rulings:
        raise ValueError("unknown ruling(s): " + "; ".join(unknown_rulings))
    if len(rulings) != len(set(rulings)):
        raise ValueError("duplicate ruling in selection")

    role_order = list(dict.fromkeys(claims[claim_id]["role"] for claim_id in selected_ids))
    lines = [
        "# Application facts packet",
        "",
        "Generated from the knowledge repository claims view. Only listed claims are included.",
        "",
    ]

    for role_id in role_order:
        role = roles[role_id]
        lines.append(f"## {role_id}")
        for field in ROLE_FIELDS:
            lines.append(f"{field}: {role.get(field, '')}")
        lines.append("")

        for claim_id in selected_ids:
            claim = claims[claim_id]
            if claim["role"] != role_id:
                continue
            if "canonical" not in claim or "metrics" not in claim:
                raise ValueError(f"claim {claim_id} is missing canonical wording or metrics")
            lines.extend([
                f"### {claim_id} | {claim['tier']}",
                f"canonical: {claim['canonical']}",
                f"metrics: {claim['metrics']}",
                "",
            ])

    if summaries:
        lines.extend(["# Selected summaries", ""])
        for summary_id in summaries:
            lines.extend([
                f"### {summary_id}",
                f"summary: {available_summaries[summary_id]}",
                f"source: kb/summaries.md#{summary_id}",
                "",
            ])

    if education:
        lines.extend(["# Selected education and credentials", ""])
        for entry_id in education:
            entry = available_education[entry_id]
            lines.append(f"### {entry_id} {entry['title']}")
            fields = (EDUCATION_FIELDS if entry_id.startswith("EDU-") else
                      CERTIFICATE_FIELDS if entry_id.startswith("CERT-") else PUBLICATION_FIELDS)
            for field in fields:
                if entry.get(field):
                    lines.append(f"{field}: {entry[field]}")
            lines.extend([f"source: kb/education.md#{entry_id}", ""])

    if skills:
        lines.extend(["# Selected skills", ""])
        lines.extend(f"- {skill} | source: kb/skills.md" for skill in skills)
        lines.append("")

    if rulings:
        lines.extend(["# Selected owner rulings", ""])
        lines.extend(f"- {ruling} | source: kb/_user_decisions.md" for ruling in rulings)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claims", required=True, help="comma-separated claim IDs selected by the owner")
    parser.add_argument("--summary", action="append", default=[], help="selected summary ID; repeat as needed")
    parser.add_argument("--education", help="comma-separated EDU-, CERT-, or PUB- IDs selected by the owner")
    parser.add_argument("--skill", action="append", default=[], help="exact selected skill wording; repeat as needed")
    parser.add_argument("--ruling", action="append", default=[], help="exact owner-ruling text; repeat as needed")
    parser.add_argument("--out", required=True, type=Path, help="output Markdown packet")
    args = parser.parse_args(argv)

    try:
        selected_ids = [claim_id.strip() for claim_id in args.claims.split(",")]
        summaries = args.summary
        education = [entry_id.strip() for entry_id in (args.education or "").split(",") if entry_id.strip()]
        validate_output_path(args.out)
        packet = build_packet(selected_ids, summaries, education, args.skill, args.ruling)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w", encoding="utf-8", newline="") as handle:
            handle.write(packet)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(f"wrote application-facts packet: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
