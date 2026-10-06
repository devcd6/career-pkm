#!/usr/bin/env python3
"""Read-only inventory of markdown resume files.

Computes hashes and stats, finds exact duplicates, and groups files into
version clusters by CONTENT similarity (word 3-shingle Jaccard), not by name.
Standard library only. Never modifies the input folder.

Usage:
    python inventory.py [ROOT] [--out _work] [--threshold 0.35]

Outputs (in --out):
    manifest.json   machine-readable, one record per file
    manifest.csv    same data, spreadsheet-friendly
    clusters.md     human-readable version clusters for review
"""
import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

SECTION_WORDS = {
    "experience", "education", "skills", "summary", "projects",
    "certifications", "work history", "employment", "profile", "objective",
    "publications", "awards", "professional experience", "technical skills",
}
YEAR_RE = re.compile(r"\b(19[89]\d|20[0-4]\d)\b")
CURRENT_RE = re.compile(r"\b(present|current|ongoing|now)\b", re.I)
FRONTMATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.S)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1)


def normalize(text: str) -> list:
    text = strip_frontmatter(text).lower()
    text = re.sub(r"[#*_`>\[\]()|~-]", " ", text)
    text = re.sub(r"[^a-z0-9%$+. ]", " ", text)
    return text.split()


def shingles(words: list, k: int = 3) -> set:
    if len(words) < k:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i:i + k]) for i in range(len(words) - k + 1)}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def headings(text: str) -> list:
    out = []
    for line in strip_frontmatter(text).splitlines():
        s = line.strip()
        if s.startswith("#"):
            out.append(s.lstrip("#").strip().lower())
        elif s and len(s) < 40 and s.isupper() and any(c.isalpha() for c in s):
            out.append(s.lower())
    return out


def looks_like_resume(text: str, heads: list, words: int) -> bool:
    head200 = text.strip()[:200].lower()
    if head200.startswith("dear ") or "\ndear " in head200:
        return False
    hits = sum(1 for h in heads if any(w in h for w in SECTION_WORDS))
    return hits >= 2 and words >= 60


class UnionFind:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("root", nargs="?", default="_raw")
    ap.add_argument("--out", default="_work")
    ap.add_argument("--threshold", type=float, default=0.35,
                    help="Jaccard similarity for same-lineage (default 0.35)")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 1
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    files = sorted(p for p in root.rglob("*") if p.is_file())
    md_files = [p for p in files if p.suffix.lower() in {".md", ".markdown"}]
    skipped = [p for p in files if p not in md_files and not p.name.startswith(".")]

    records = []
    shingle_sets = []
    for p in md_files:
        text = read_text(p)
        words = normalize(text)
        heads = headings(text)
        years = sorted({int(y) for y in YEAR_RE.findall(text)})
        # "Present" means the resume was current when written: rank it as this year
        if CURRENT_RE.search(strip_frontmatter(text)):
            years.append(datetime.now().year)
        rec = {
            "path": str(p),
            "size": p.stat().st_size,
            "modified": datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d"),
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "norm_sha": hashlib.sha256(" ".join(words).encode()).hexdigest(),
            "words": len(words),
            "headings": heads[:25],
            "max_year": max(years) if years else None,
            "has_frontmatter": bool(FRONTMATTER_RE.match(text)),
            "likely_resume": looks_like_resume(text, heads, len(words)),
            "first_line": next((l.strip() for l in text.splitlines() if l.strip()), "")[:100],
        }
        records.append(rec)
        shingle_sets.append(shingles(words))

    n = len(records)

    # Exact duplicates (content identical after normalization)
    by_norm = {}
    for i, r in enumerate(records):
        by_norm.setdefault(r["norm_sha"], []).append(i)
    for idxs in by_norm.values():
        first = idxs[0]
        for j in idxs:
            records[j]["exact_dup_of"] = None if j == first else records[first]["path"]

    # Similarity clustering (single linkage). Skip exact dups when linking.
    uf = UnionFind(n)
    best = {}
    for i in range(n):
        for j in range(i + 1, n):
            s = jaccard(shingle_sets[i], shingle_sets[j])
            if s >= args.threshold:
                uf.union(i, j)
            if s > best.get(i, (0, None))[0]:
                best[i] = (s, j)
            if s > best.get(j, (0, None))[0]:
                best[j] = (s, i)

    groups = {}
    for i in range(n):
        groups.setdefault(uf.find(i), []).append(i)
    clusters = sorted(groups.values(), key=lambda g: (-len(g), g[0]))
    cid = 0
    for g in clusters:
        if len(g) > 1:
            cid += 1
            for i in g:
                records[i]["cluster"] = f"C{cid:02d}"
        else:
            records[g[0]]["cluster"] = None

    # Outputs
    (out / "manifest.json").write_text(json.dumps(records, indent=2))
    cols = ["path", "modified", "words", "max_year", "cluster", "exact_dup_of",
            "likely_resume", "has_frontmatter", "first_line"]
    with open(out / "manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(records)

    lines = [
        "# Version clusters",
        "",
        f"Source: `{root}`  |  files: {n}  |  threshold: {args.threshold}",
        "",
        "Clusters are grouped by CONTENT similarity, not filename. The order hint "
        "uses the latest year mentioned in the text, then modified date. "
        "Modified dates are unreliable (copies, syncs), so confirm order by reading.",
        "",
    ]
    cid = 0
    for g in clusters:
        if len(g) < 2:
            continue
        cid += 1
        g_sorted = sorted(g, key=lambda i: (records[i]["max_year"] or 0, records[i]["modified"]))
        lines += [f"## Cluster C{cid:02d} ({len(g)} files)", "",
                  "| # | file | modified | words | max year | sim to previous | exact dup of |",
                  "|---|------|----------|-------|----------|-----------------|--------------|"]
        prev = None
        for k, i in enumerate(g_sorted, 1):
            r = records[i]
            sim = "" if prev is None else f"{jaccard(shingle_sets[prev], shingle_sets[i]):.2f}"
            lines.append(f"| {k} | `{r['path']}` | {r['modified']} | {r['words']} | "
                         f"{r['max_year'] or ''} | {sim} | {r['exact_dup_of'] or ''} |")
            prev = i
        lines.append("")

    singles = [records[g[0]] for g in clusters if len(g) == 1]
    if singles:
        lines += ["## Unclustered files (no similar sibling found)", ""]
        for r in singles:
            lines.append(f"- `{r['path']}` ({r['words']} words, likely resume: {r['likely_resume']})")
        lines.append("")

    non_resume = [r for r in records if not r["likely_resume"]]
    if non_resume:
        lines += ["## Possibly not resumes (cover letters, notes, fragments)", ""]
        for r in non_resume:
            lines.append(f"- `{r['path']}`: {r['first_line']!r}")
        lines.append("")

    if skipped:
        lines += ["## Skipped (not markdown)", ""]
        for p in skipped:
            lines.append(f"- `{p}`")
        lines.append("")

    (out / "clusters.md").write_text("\n".join(lines))
    print(f"files: {n}  clusters: {cid}  singletons: {len(singles)}  "
          f"exact-dup files: {sum(1 for r in records if r.get('exact_dup_of'))}  "
          f"skipped non-md: {len(skipped)}")
    print(f"wrote {out}/manifest.json, manifest.csv, clusters.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
