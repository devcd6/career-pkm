#!/usr/bin/env python3
"""Verify an application-facts packet against the current career knowledge sources."""
import argparse
import re
import sys
from pathlib import Path

from build_claim_packet import (
    CERTIFICATE_FIELDS,
    CLAIMS_VIEW,
    EDUCATION_FIELDS,
    EDUCATION,
    PACKET_DIR,
    PUBLICATION_FIELDS,
    ROLE_FIELDS,
    SKILLS,
    SUMMARIES,
    DECISIONS,
    parse_claims,
    parse_education,
    parse_skills,
    parse_summaries,
    validate_output_path,
)


def single_heading_section(text, heading):
    match = re.search(rf"^# {re.escape(heading)}\s*$", text, re.MULTILINE)
    if not match:
        return None
    next_heading = re.search(r"^# (?!#)", text[match.end():], re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(text)
    return text[match.end():end]


def entry_blocks(section, pattern):
    if section is None:
        return {}
    headings = list(re.finditer(pattern, section, re.MULTILINE))
    entries = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(section)
        fields = {}
        for line in section[heading.end():end].splitlines():
            key, separator, value = line.partition(": ")
            if separator:
                fields[key] = value
        entries[heading.group(1)] = {"title": heading.group(2) if heading.lastindex > 1 else "", **fields}
    return entries


def list_entries(section):
    if section is None:
        return []
    return [line[2:].split(" | source:", 1)[0] for line in section.splitlines() if line.startswith("- ")]


def validate(packet_path, source_path=CLAIMS_VIEW):
    packet_text = packet_path.read_text(encoding="utf-8")
    source_text = source_path.read_text(encoding="utf-8")
    packet_roles, packet_claims, packet_order = parse_claims(packet_text)
    source_roles, source_claims, _ = parse_claims(source_text)
    errors = []

    if not packet_text.startswith("# Application facts packet\n"):
        errors.append("missing '# Application facts packet' heading")
    if not packet_order:
        errors.append("packet contains no claims")
    if len(packet_order) != len(set(packet_order)):
        errors.append("packet contains duplicate claim IDs")
    if len(re.findall(r"^## ", packet_text, re.MULTILINE)) != len(packet_roles):
        errors.append("packet contains malformed or duplicate role headings")
    if len(re.findall(r"^### A-", packet_text, re.MULTILINE)) != len(packet_order):
        errors.append("packet contains a malformed claim heading")

    for claim_id in packet_order:
        if claim_id not in source_claims:
            errors.append(f"unknown claim ID: {claim_id}")
            continue
        packet_claim = packet_claims[claim_id]
        source_claim = source_claims[claim_id]
        for field in ("tier", "canonical", "metrics"):
            if field not in packet_claim:
                errors.append(f"claim {claim_id} is missing {field}")
            elif packet_claim[field] != source_claim.get(field):
                errors.append(f"claim {claim_id} {field} mismatch")

    selected_roles = {packet_claims[claim_id]["role"] for claim_id in packet_order}
    if set(packet_roles) != selected_roles:
        errors.append("role headers do not match the selected claims")
    for role_id, packet_role in packet_roles.items():
        source_role = source_roles.get(role_id)
        if source_role is None:
            errors.append(f"unknown role ID: {role_id}")
            continue
        if not packet_role.get("claims"):
            errors.append(f"role {role_id} has no selected claims")
        for field in ROLE_FIELDS:
            if packet_role.get(field) != source_role.get(field):
                errors.append(f"role {role_id} {field} mismatch")

    packet_summaries = entry_blocks(
        single_heading_section(packet_text, "Selected summaries"),
        r"^### (S-\d{2})\s*$",
    )
    source_summaries = parse_summaries(SUMMARIES)
    if len(re.findall(r"^### S-", packet_text, re.MULTILINE)) != len(packet_summaries):
        errors.append("packet contains malformed or duplicate summary headings")
    for summary_id, entry in packet_summaries.items():
        if summary_id not in source_summaries:
            errors.append(f"unknown summary ID: {summary_id}")
        elif entry.get("summary") != source_summaries[summary_id]:
            errors.append(f"summary {summary_id} summary mismatch")
        if entry.get("source") != f"kb/summaries.md#{summary_id}":
            errors.append(f"summary {summary_id} source mismatch")

    packet_education = entry_blocks(
        single_heading_section(packet_text, "Selected education and credentials"),
        r"^### ((?:EDU|CERT|PUB)-\d+) (.+)$",
    )
    source_education = parse_education(EDUCATION)
    if len(re.findall(r"^### (?:EDU|CERT|PUB)-", packet_text, re.MULTILINE)) != len(packet_education):
        errors.append("packet contains malformed or duplicate education headings")
    for entry_id, entry in packet_education.items():
        source = source_education.get(entry_id)
        if source is None:
            errors.append(f"unknown education ID: {entry_id}")
            continue
        if entry.get("title") != source["title"]:
            errors.append(f"education {entry_id} title mismatch")
        fields = (EDUCATION_FIELDS if entry_id.startswith("EDU-") else
                  CERTIFICATE_FIELDS if entry_id.startswith("CERT-") else PUBLICATION_FIELDS)
        for field in fields:
            if field in entry and entry[field] != source.get(field):
                errors.append(f"education {entry_id} {field} mismatch")
        if entry.get("source") != f"kb/education.md#{entry_id}":
            errors.append(f"education {entry_id} source mismatch")

    known_skills = set(parse_skills(SKILLS))
    for skill in list_entries(single_heading_section(packet_text, "Selected skills")):
        if skill not in known_skills:
            errors.append(f"unknown skill: {skill}")

    decisions = DECISIONS.read_text(encoding="utf-8")
    for ruling in list_entries(single_heading_section(packet_text, "Selected owner rulings")):
        if ruling not in decisions:
            errors.append(f"unknown ruling: {ruling}")

    try:
        validate_output_path(packet_path)
    except ValueError as error:
        errors.append(str(error))

    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--claims", type=Path, default=CLAIMS_VIEW, help="source claims view")
    args = parser.parse_args(argv)

    try:
        errors = validate(args.packet, args.claims)
    except OSError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    for error in errors:
        print(f"ERROR {error}")
    print(f"application-facts packet check: {'FAILED' if errors else 'ok'} ({len(errors)} error(s))")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
