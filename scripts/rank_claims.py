#!/usr/bin/env python3
"""Advisory claim ranking for one application. Writes no facts and no bullets.

Usage:
    python scripts/rank_claims.py --jd jd.md --keywords keywords.txt [--top 12] --out rank.md

Reads the keyword file ("Category | phrase" lines) and the JD, then scores every claim in kb/_views/claims.md by exact, whole-word,
case-insensitive phrase hits in its canonical wording (bracket alternatives all count).

Weights by category: Forced 4, Title Keyword 3, Hard Skill 3, Business Context 2,
Domain Keyword 2, Action Keyword 1, Uncategorized 1, Hard Filter 0 (eligibility, not matchable).
Label per phrase: "stated" (appears in the JD, weighted) or "not-in-jd" (weight 0, listed so the
owner sees it). The score ranks claims for the owner and agent to choose from; it is not a fit
percentage. Per role the report shows tier, matched phrases and near-duplicate clusters
(word overlap >= 0.70). It also lists phrases that no claim in the KB contains: real gaps.
Selection stays with the owner, who passes the chosen IDs to build_claim_packet.py.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_application as ca  # noqa: E402

ROOT = ca.ROOT
WEIGHT = {"Forced": 4, "Title Keyword": 3, "Hard Skill": 3, "Business Context": 2,
          "Domain Keyword": 2, "Action Keyword": 1, "Uncategorized": 1, "Hard Filter": 0}


def kb_reference_lines():
    """(file, line number, label, text) for skills, summaries and education lines, so tool and skill phrases are not reported as gaps."""
    rows = []
    for rel in ("kb/skills.md", "kb/summaries.md", "kb/education.md"):
        f = ROOT / rel
        if not f.exists():
            continue
        heading = ""
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if line.startswith("## ") or line.startswith("### "):
                heading = line.lstrip("# ").split()[0] if line.lstrip("# ") else ""
            if rel == "kb/skills.md":
                fields = [x.strip() for x in line.split(" | ")]
                if len(fields) < 5 or not re.match(r"\d{4}-\d{2}_", fields[1]):
                    continue
                rows.append((rel, n, fields[0][:60], fields[0]))
            elif line.strip() and not line.startswith(("#", "sources:", "count:")):
                rows.append((rel, n, heading, line))
    return rows


def hard_filter_block(filters):
    out = ["## Hard filters (owner decides; advisory lookup only)"]
    if not filters:
        return out + ["- none", ""]
    education = (ROOT / "kb" / "education.md").read_text(encoding="utf-8") if (ROOT / "kb" / "education.md").exists() else ""
    decisions = (ROOT / "kb" / "_user_decisions.md").read_text(encoding="utf-8").splitlines() if (ROOT / "kb" / "_user_decisions.md").exists() else []
    for _, phrase in filters:
        low = phrase.lower()
        notes = []
        degree = re.search(r"associate|bachelor|master|doctor|degree|diploma", low)
        if degree:
            word = degree.group(0) if degree.group(0) not in ("degree", "diploma") else "(?:associate|bachelor|master)"
            notes += [f"kb/education.md {m.group(1)}" for m in re.finditer(rf"^### (EDU-\d+[^\n]*{word}[^\n]*)", education, re.I | re.M)]
            if not notes:
                notes.append("no matching EDU heading; check kb/education.md")
        if re.search(r"\byears?\b", low):
            notes += [f"kb/_user_decisions.md:{n} (years ruling)" for n, l in enumerate(decisions, 1) if re.search(r"\d\+?\s*years|years of experience", l, re.I)][:2]
            notes.append("compare the role dates in the packet; owner decides")
        if re.search(r"background|clearance|public trust|citizen|authoriz|eligib|visa|sponsor|license|certif", low) and not notes:
            notes.append("eligibility: no KB source, owner answers")
        out.append(f"- {phrase} | " + ("; ".join(notes) if notes else "owner decides"))
    out.append("")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jd", required=True, help="job description file")
    ap.add_argument("--keywords", required=True, help="exact keyword list")
    ap.add_argument("--claims", default=str(ROOT / "kb" / "_views" / "claims.md"))
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--out", help="save the report to this path")
    a = ap.parse_args()

    keywords_path = Path(a.keywords)
    jd_path = Path(a.jd)
    out_path = Path(a.out) if a.out else None

    kws = ca.read_keywords(keywords_path)
    ca_unknown = ca.unknown_category_lines(keywords_path)
    if not kws:
        print(f"no keywords found or file is empty: {keywords_path}")
        return 2
    if not jd_path.exists():
        print(f"job description not found: {jd_path}")
        return 2
    jd = ca.norm(jd_path.read_text(encoding="utf-8"))
    roles, claims = ca.load_claims(Path(a.claims))
    labelled = [(c, p, "stated" if (not jd or ca.has_phrase(jd, p)) else "not-in-jd") for c, p in kws]

    scored = {}
    for cid, cl in claims.items():
        text = re.sub(r"[\[\]|]", " ", cl.get("canonical", ""))
        hits = [(c, p, l) for c, p, l in labelled if ca.has_phrase(text, p)]
        score = sum(WEIGHT.get(c, 1) for c, p, l in hits if l == "stated")
        scored[cid] = (score, hits)

    out = [f"# Claim ranking: {jd_path.stem}", "",
           "Advisory. Not a fit score. Owner chooses; the owner selects claim IDs for the packet.", ""]
    for rid, role in roles.items():
        ids = [c for c, cl in claims.items() if cl["role"] == rid]
        ranked = sorted(ids, key=lambda c: (-scored[c][0], c))
        out.append(f"## {rid}  ({role.get('title', '').split('|')[0].strip()}; {len(ids)} claims)")
        shown = [c for c in ranked if scored[c][0] > 0][: a.top]
        if not shown:
            out += ["No claim in this role matches a stated phrase.", ""]
            continue
        for c in shown:
            s, hits = scored[c]
            ph = "; ".join(f"{p} [{cat}]" if l == "stated" else f"{p} [{cat}, not-in-jd]" for cat, p, l in hits)
            out.append(f"- {c} | {claims[c]['tier']} | score {s} | {ph}")
        clusters, seen = [], set()
        for i, c1 in enumerate(shown):
            if c1 in seen:
                continue
            w1 = ca.wordset(claims[c1].get("canonical", ""))
            grp = [c1]
            for c2 in ranked:
                if c2 != c1 and c2 not in seen:
                    w2 = ca.wordset(claims[c2].get("canonical", ""))
                    if len(w1 & w2) / max(1, len(w1 | w2)) >= 0.70:
                        grp.append(c2)
            if len(grp) > 1:
                clusters.append(grp)
                seen.update(grp)
        for g in clusters:
            out.append(f"  near-duplicates, pick one: {', '.join(g)}")
        out.append("")

    claim_text = {cid: re.sub(r"[\[\]|]", " ", cl.get("canonical", "")) for cid, cl in claims.items()}
    corpus = " ".join(claim_text.values())
    gap = [(c, p) for c, p in kws if c != "Hard Filter" and not ca.has_phrase(corpus, p)]
    kb_lines = kb_reference_lines()
    out.append("## No exact match in any claim (check the notes before treating these as gaps)")
    for c, p in gap:
        notes = []
        near = [cid for cid, t in claim_text.items() if ca.variant_phrase(t, p)]
        if near:
            notes.append("inflected or hyphenated form in " + ", ".join(near[:3]) + (f" (+{len(near) - 3})" if len(near) > 3 else ""))
        found = [f"{rel}:{n} {label}" for rel, n, label, t in kb_lines if ca.has_phrase(t, p) or ca.variant_phrase(t, p)]
        if found:
            notes.append("in " + "; ".join(found[:3]) + " (skill or summary wording, not a claim)")
        out.append(f"- {p} [{c}]" + (" | " + " | ".join(notes) if notes else " | no match found"))
    if not gap:
        out.append("- none")
    out.append("")
    out += hard_filter_block([(c, p) for c, p in kws if c == "Hard Filter"])
    cov = {}
    for c, p, l in labelled:
        if c == "Hard Filter":
            continue
        d = cov.setdefault(c, [0, 0])
        d[1] += 1
        d[0] += any(ca.has_phrase(t, p) for t in claim_text.values())
    out.append("## KB support by category (phrases found in at least one claim)")
    out += [f"- {c}: {h}/{t}" for c, (h, t) in cov.items()]
    for line in ca_unknown:
        out.append(f"WARNING: unknown keyword category, treated as Uncategorized: {line}")
    text = "\n".join(out)
    print(text)
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
