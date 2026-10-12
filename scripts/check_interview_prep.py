#!/usr/bin/env python3
"""Check an interview-prep.md against the knowledge base.

Usage:
    python scripts/check_interview_prep.py applications/<slug>
    python scripts/check_interview_prep.py applications/<slug> --claims kb/_views/claims.md

Reads <slug>/interview-prep.md. Errors (exit 1):
  provenance   a number not found in any claim's metrics (years, dates, claim and story IDs,
               URLs and list numbers are ignored; "4+" is an owner ruling and allowed)
  ids          a claim ID (A-...) not in the claims view, or a story ID (S###) not in kb/stories.md
  questions    a predicted-question line ("Q: ...") without exactly one tag:
               [inferred from JD] | [inferred] | [reported: <url> <url> ...] (two or more distinct
               URLs) | [one report: <url>]
  cheatsheet   no "Cheat sheet" heading
  dashes       em dash in the text
Numbers are compared as literal tokens, using the same rules as check_application.py. This
script does not change that checker.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_application as ca  # noqa: E402

URL_RE = re.compile(r"https?://[^\s)\]]+")
CLAIM_ID_RE = re.compile(r"\bA-[a-z0-9]+(?:-[a-z0-9]+)*-\d+\b")
STORY_ID_RE = re.compile(r"\bS\d{3}\b")
ISO_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
MONTH_DAY_RE = re.compile(rf"\b{ca.MON}\s+\d{{1,2}}\b")
LIST_NUM_RE = re.compile(r"^\s*\d+[.)]\s+", re.M)
Q_RE = re.compile(r"^\s*(?:[-*]\s+|\d+[.)]\s+)?Q:\s*(.*)$")
TAG_RE = re.compile(r"\[(inferred from JD|inferred|reported:[^\]]*|one report:[^\]]*)\]")


def strip_non_numeric(text):
    for rx in (URL_RE, CLAIM_ID_RE, STORY_ID_RE, ISO_RE, MONTH_DAY_RE):
        text = rx.sub(" ", text)
    return LIST_NUM_RE.sub("", text)


def story_ids(path):
    return set(re.findall(r"^### (S\d{3})\b", path.read_text(encoding="utf-8"), re.M))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--claims", default=str(ROOT / "kb" / "_views" / "claims.md"))
    ap.add_argument("--stories", default=str(ROOT / "kb" / "stories.md"))
    args = ap.parse_args()
    folder = Path(args.folder)
    f = folder / "interview-prep.md"
    if not f.exists():
        print(f"error: {f} not found")
        return 1
    text = f.read_text(encoding="utf-8")
    _, claims = ca.load_claims(Path(args.claims))
    stories = story_ids(Path(args.stories))
    errs = []

    allowed = set(ca.RULING_NUMBERS)
    for c in claims.values():
        allowed |= ca.metric_tokens(c)
    for tok in sorted(set(ca.numbers_in(strip_non_numeric(text)))):
        if tok not in allowed:
            errs.append(("provenance", f"number {tok!r} is not in any claim's metrics"))

    for cid in sorted(set(CLAIM_ID_RE.findall(text))):
        if cid not in claims:
            errs.append(("ids", f"unknown claim ID {cid}"))
    for sid in sorted(set(STORY_ID_RE.findall(text))):
        if sid not in stories:
            errs.append(("ids", f"unknown story ID {sid}"))

    n_q = 0
    for i, line in enumerate(text.splitlines(), 1):
        m = Q_RE.match(line)
        if not m:
            continue
        n_q += 1
        tags = TAG_RE.findall(line)
        if len(tags) != 1:
            errs.append(("questions", f"line {i}: needs exactly one tag, found {len(tags)}"))
            continue
        tag = tags[0]
        urls = set(URL_RE.findall(tag))
        if tag.startswith("reported:") and len(urls) < 2:
            errs.append(("questions", f"line {i}: [reported] needs two or more distinct URLs (use [one report: url] for one)"))
        if tag.startswith("one report:") and len(urls) != 1:
            errs.append(("questions", f"line {i}: [one report] needs exactly one URL"))

    if not re.search(r"^#{1,4}\s*cheat sheet", text, re.I | re.M):
        errs.append(("cheatsheet", "no 'Cheat sheet' heading"))
    if "\u2014" in text:
        errs.append(("dashes", "em dash in text"))

    for kind, msg in errs:
        print(f"error [{kind}]: {msg}")
    print(f"{n_q} predicted questions checked; {len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
