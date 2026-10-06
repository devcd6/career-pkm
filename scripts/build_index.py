#!/usr/bin/env python3
"""Generate INDEX.md from the knowledge base and lint it.

Reads:
    resumes/**/*.md        frontmatter on each organized resume version
                           (optional key duplicate_of: <path> exempts exact duplicates
                           from the "must be cited by a role" check)
    kb/roles/*.md          one file per role; achievements are '### A-...' blocks
    kb/_conflicts.md       '## C-...' blocks with a 'status:' line

Writes:
    INDEX.md               tables of resume versions, roles, open conflicts

Usage:
    python build_index.py            # regenerate INDEX.md
    python build_index.py --check    # lint only, exit 1 if problems found

Frontmatter must be flat 'key: value' lines; lists use inline [a, b] form.
"""
import argparse
import re
import sys
from datetime import date
from pathlib import Path

FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
RESUME_KEYS = ["id", "role_target", "company_target", "date", "version_group",
               "version_no", "status", "source_original"]
ROLE_KEYS = ["id", "employer", "title", "start", "end", "sources"]
ACH_KEYS = ["canonical", "tier", "sources"]
TIERS = {"verified", "consistent", "single-source", "conflicting"}
STATUSES = {"active", "archived"}


def parse_fm(text: str) -> dict:
    m = FM_RE.match(text)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        k, v = line.split(":", 1)
        v = v.strip().strip("'\"")
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
        out[k.strip()] = v
    return out


def body(text: str) -> str:
    return FM_RE.sub("", text, count=1)


def achievement_blocks(text: str):
    """Yield (id, {key: value}) for each '### A-...' block."""
    parts = re.split(r"(?m)^###\s+(A-[\w.-]+)\s*$", body(text))
    for i in range(1, len(parts), 2):
        block = {}
        for line in parts[i + 1].splitlines():
            m = re.match(r"^([a-z_]+):\s*(.*)$", line.strip())
            if m:
                block[m.group(1)] = m.group(2).strip()
        yield parts[i], block


def conflict_blocks(text: str):
    parts = re.split(r"(?m)^##\s+(C-[\w.-]+)\s*$", text)
    for i in range(1, len(parts), 2):
        block = {"id": parts[i], "raw": parts[i + 1]}
        for line in parts[i + 1].splitlines():
            m = re.match(r"^(status|role|field|resolution):\s*(.*)$", line.strip())
            if m:
                block[m.group(1)] = m.group(2).strip()
        yield block


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="lint only")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = Path(args.root)

    problems = []
    resumes, roles = [], []

    # Resume versions
    for p in sorted((root / "resumes").rglob("*.md")) if (root / "resumes").is_dir() else []:
        fm = parse_fm(p.read_text(encoding="utf-8", errors="replace"))
        rel = p.relative_to(root).as_posix()
        missing = [k for k in RESUME_KEYS if not fm.get(k)]
        if missing:
            problems.append(f"{rel}: missing frontmatter {missing}")
        if fm.get("status") and fm["status"] not in STATUSES:
            problems.append(f"{rel}: status must be one of {sorted(STATUSES)}")
        resumes.append((rel, fm))

    # Roles and achievements
    open_by_role = {}
    cpath = root / "kb" / "_conflicts.md"
    conflicts = []
    if cpath.exists():
        conflicts = list(conflict_blocks(cpath.read_text(encoding="utf-8")))
        for c in conflicts:
            st = c.get("status", "")
            if st not in {"open", "resolved"}:
                problems.append(f"kb/_conflicts.md {c['id']}: status must be open or resolved")
            if st == "resolved" and not c.get("resolution"):
                problems.append(f"kb/_conflicts.md {c['id']}: resolved but no resolution text")
            if st == "open":
                open_by_role[c.get("role", "?")] = open_by_role.get(c.get("role", "?"), 0) + 1

    rdir = root / "kb" / "roles"
    known_sources = {r[0] for r in resumes}
    for p in sorted(rdir.glob("*.md")) if rdir.is_dir() else []:
        text = p.read_text(encoding="utf-8", errors="replace")
        fm = parse_fm(text)
        rel = p.relative_to(root).as_posix()
        missing = [k for k in ROLE_KEYS if not fm.get(k)]
        if missing:
            problems.append(f"{rel}: missing frontmatter {missing}")
        n_ach = 0
        for aid, blk in achievement_blocks(text):
            n_ach += 1
            for k in ACH_KEYS:
                if not blk.get(k):
                    problems.append(f"{rel} {aid}: missing '{k}:'")
            if blk.get("tier") and blk["tier"] not in TIERS:
                problems.append(f"{rel} {aid}: tier must be one of {sorted(TIERS)}")
            srcs = re.findall(r"resumes/[^\s,\]]+\.md", blk.get("sources", ""))
            for s in srcs:
                if known_sources and s not in known_sources:
                    problems.append(f"{rel} {aid}: source not found in resumes/: {s}")
        roles.append((rel, fm, n_ach))

    # Coverage: every organized resume should be cited by at least one role
    cited = set()
    for p in sorted(rdir.glob("*.md")) if rdir.is_dir() else []:
        cited.update(re.findall(r"resumes/[^\s,\]]+\.md", p.read_text(encoding="utf-8")))
    for rel, fm in resumes:
        if fm.get("duplicate_of"):
            continue  # exact duplicates are exempt from the citation check
        if roles and rel not in cited:
            problems.append(f"{rel}: not cited by any kb/roles file (not yet ingested?)")

    if args.check:
        if problems:
            print(f"{len(problems)} problem(s):")
            for pr in problems:
                print("  -", pr)
            return 1
        print(f"OK: {len(resumes)} resume versions, {len(roles)} roles, "
              f"{sum(1 for c in conflicts if c.get('status') == 'open')} open conflicts")
        return 0

    lines = [f"# Career knowledge base index", "",
             f"Generated {date.today().isoformat()} by scripts/build_index.py. Do not edit by hand.", ""]

    lines += ["## Resume versions", "",
              "| raw | file | target role | date | keywords / unique angle | status |",
              "|-----|------|-------------|------|-------------------------|--------|"]
    for rel, fm in sorted(resumes, key=lambda r: (r[1].get("status", "") == "archived", r[1].get("version_group", ""), str(r[1].get("version_no", "")))):
        raw = fm.get("source_original", "").replace("_raw/", "")
        kw = fm.get("keywords", "") + (f" ({fm['archive_reason']})" if fm.get("archive_reason") else "")
        lines.append(f"| {raw} | [{Path(rel).name}]({rel}) | {fm.get('role_target', '')} | "
                     f"{fm.get('date', '')} | {kw} | {fm.get('status', '')} |")
    lines.append("")

    lines += ["## Roles", "",
              "| role | employer | dates | achievements | open conflicts |",
              "|------|----------|-------|--------------|----------------|"]
    for rel, fm, n_ach in sorted(roles, key=lambda r: str(r[1].get("start", "")), reverse=True):
        rid = fm.get("id", "")
        lines.append(f"| [{fm.get('title', Path(rel).stem)}]({rel}) | {fm.get('employer', '')} | "
                     f"{fm.get('start', '')} to {fm.get('end', '')} | {n_ach} | {open_by_role.get(rid, 0)} |")
    lines.append("")

    n_open = sum(1 for c in conflicts if c.get("status") == "open")
    lines += ["## Status", "",
              f"- Resume versions organized: {len(resumes)}",
              f"- Roles in KB: {len(roles)}",
              f"- Achievements: {sum(r[2] for r in roles)}",
              f"- Open conflicts: {n_open} (see [kb/_conflicts.md](kb/_conflicts.md))",
              f"- Lint problems: {len(problems)}", ""]
    if problems:
        lines += ["### Lint problems", ""] + [f"- {p}" for p in problems] + [""]

    (root / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote INDEX.md: {len(resumes)} versions, {len(roles)} roles, "
          f"{n_open} open conflicts, {len(problems)} lint problems")
    return 0


if __name__ == "__main__":
    sys.exit(main())
