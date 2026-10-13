#!/usr/bin/env python3
"""Import an owner-supplied interview handoff packet into the knowledge base.

Usage: python scripts/import_interview_packet.py <packet.md> [--claims kb/_views/claims.md]
                                                  [--dest-root kb/interviews]

Validates the packet contract (front matter `slug` and `created`; exactly the sections Job
description, Submitted resume, Claims used, Role research, Known gaps, in that order, none empty;
claim IDs listed as `- A-...`; a source URL or "No external sources." under Role research), checks
every claim ID against the claims view, then stores the packet unchanged at
<dest-root>/<slug>/packet.md. Nothing is stored if any check fails, and an existing import is never
overwritten. The packet's contents are never sent anywhere.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_application as ca  # noqa: E402

SECTIONS = ["Job description", "Submitted resume", "Claims used", "Role research", "Known gaps"]
SLUG_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_[a-z0-9][a-z0-9-]*_[a-z0-9][a-z0-9-]*$")
CLAIM_ID_RE = re.compile(r"^- (A-[a-z0-9]+(?:-[a-z0-9]+)*-\d+)\s*$")
URL_RE = re.compile(r"https?://\S+")


def parse(text):
    meta, sections, order, cur = {}, {}, [], None
    for line in text.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
            order.append(cur)
            sections[cur] = []
        elif cur is None:
            m = re.match(r"(\w+): (.*)$", line)
            if m:
                meta[m.group(1)] = m.group(2).strip()
        else:
            sections[cur].append(line)
    return meta, {k: "\n".join(v).strip() for k, v in sections.items()}, order


def validate(text, known_claims):
    errs = []
    meta, sections, order = parse(text)
    slug = meta.get("slug", "")
    if not SLUG_RE.match(slug):
        errs.append(f"slug {slug!r} must look like YYYY-MM-DD_org_role (lowercase letters, digits, hyphens)")
    if not meta.get("created"):
        errs.append("missing front matter key: created")
    for name in order:
        if name not in SECTIONS:
            errs.append(f"unknown section: {name}")
    for name in SECTIONS:
        if name not in sections:
            errs.append(f"missing section: {name}")
        elif not sections[name]:
            errs.append(f"empty section: {name}")
    if not errs and order != SECTIONS:
        errs.append("sections out of order")
    ids = [m.group(1) for m in (CLAIM_ID_RE.match(l) for l in sections.get("Claims used", "").splitlines()) if m]
    if "Claims used" in sections:
        if not ids:
            errs.append("Claims used has no claim IDs (lines like '- A-...')")
        if len(ids) != len(set(ids)):
            errs.append("duplicate claim ID in Claims used")
        for cid in ids:
            if cid not in known_claims:
                errs.append(f"unknown claim ID {cid}")
    research = sections.get("Role research", "")
    if research and not URL_RE.search(research) and "No external sources." not in research:
        errs.append("Role research needs a source URL or the line 'No external sources.'")
    return slug, errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("packet")
    ap.add_argument("--claims", default=str(ROOT / "kb" / "_views" / "claims.md"))
    ap.add_argument("--dest-root", default=str(ROOT / "kb" / "interviews"))
    args = ap.parse_args()
    src = Path(args.packet)
    if not src.exists():
        print(f"error: {src} not found")
        return 1
    text = src.read_text(encoding="utf-8")
    _, claims = ca.load_claims(Path(args.claims))
    slug, errs = validate(text, claims)
    if not errs:
        dest = Path(args.dest_root) / slug / "packet.md"
        if dest.exists():
            errs.append(f"{dest} already exists; remove it deliberately to re-import")
    for e in errs:
        print(f"error: {e}")
    if errs:
        print(f"{len(errs)} error(s); nothing imported")
        return 1
    dest.parent.mkdir(parents=True)
    with open(dest, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"imported {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
