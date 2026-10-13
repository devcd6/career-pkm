#!/usr/bin/env python3
"""Verify a claims packet against the current generated claims view."""
import argparse
import re
import sys
from pathlib import Path

from build_claim_packet import CLAIMS_VIEW, ROLE_FIELDS, parse_claims


def validate(packet_path, source_path=CLAIMS_VIEW):
    packet_text = packet_path.read_text(encoding="utf-8")
    source_text = source_path.read_text(encoding="utf-8")
    packet_roles, packet_claims, packet_order = parse_claims(packet_text)
    source_roles, source_claims, _ = parse_claims(source_text)
    errors = []

    if not packet_text.startswith("# Claims packet\n"):
        errors.append("missing '# Claims packet' heading")
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
    print(f"claims packet check: {'FAILED' if errors else 'ok'} ({len(errors)} error(s))")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())