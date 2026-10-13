#!/usr/bin/env python3
"""Export an owner-selected subset of the generated claims view."""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLAIMS_VIEW = ROOT / "kb" / "_views" / "claims.md"
ROLE_FIELDS = ("employer", "title", "dates", "location")


def parse_claims(text):
    roles, claims, claim_order = {}, {}, []
    current_role = None
    current_claim = None

    for line in text.splitlines():
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


def build_packet(selected_ids, source_path=CLAIMS_VIEW):
    if not selected_ids or any(not claim_id for claim_id in selected_ids):
        raise ValueError("at least one claim ID is required")
    if len(selected_ids) != len(set(selected_ids)):
        raise ValueError("duplicate claim ID in selection")

    roles, claims, _ = parse_claims(source_path.read_text(encoding="utf-8"))
    unknown = [claim_id for claim_id in selected_ids if claim_id not in claims]
    if unknown:
        raise ValueError("unknown claim ID(s): " + ", ".join(unknown))

    role_order = list(dict.fromkeys(claims[claim_id]["role"] for claim_id in selected_ids))
    lines = [
        "# Claims packet",
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

    return "\n".join(lines).rstrip() + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claims", required=True, help="comma-separated claim IDs selected by the owner")
    parser.add_argument("--out", required=True, type=Path, help="output Markdown packet")
    args = parser.parse_args(argv)

    try:
        selected_ids = [claim_id.strip() for claim_id in args.claims.split(",")]
        packet = build_packet(selected_ids)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(packet, encoding="utf-8")
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(f"wrote claims packet: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())