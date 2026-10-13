#!/usr/bin/env python3
"""Advisory claim ranking for one application. Writes no facts and no bullets.

Usage:
    python scripts/rank_claims.py applications/<slug> [--top 12] [--out rank.md]

Reads <slug>/keywords.txt ("Category | phrase" lines, see exact_phrase_matcher.py) and
<slug>/jd.md, then scores every claim in kb/_views/claims.md by exact, whole-word,
case-insensitive phrase hits in its canonical wording (bracket alternatives all count).

Weights by category: Forced 4, Title Keyword 3, Hard Skill 3, Business Context 2,
Domain Keyword 2, Action Keyword 1, Uncategorized 1, Hard Filter 0 (eligibility, not matchable).
Label per phrase: "stated" (appears in jd.md, weighted) or "not-in-jd" (weight 0, listed so the
owner sees it). The score ranks claims for the owner and agent to choose from; it is not a fit
percentage. Per role the report shows tier, matched phrases and near-duplicate clusters
(word overlap >= 0.70). It also lists phrases that no claim in the KB contains: real gaps.
Selection stays with the owner; bullets are built from spec.json by build_application.py.
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--claims", default=str(ROOT / "kb" / "_views" / "claims.md"))
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--out", help="save the report as this file name inside the application folder")
    a = ap.parse_args()
    folder = Path(a.folder)
    kws = ca.read_keywords(folder / "keywords.txt")
    if not kws:
        print("no keywords.txt found or it is empty")
        return 2
    jd_path = folder / "jd.md"
    jd = ca.norm(jd_path.read_text(encoding="utf-8")) if jd_path.exists() else ""
    roles, claims = ca.load_claims(Path(a.claims))
    labelled = [(c, p, "stated" if (not jd or ca.has_phrase(jd, p)) else "not-in-jd") for c, p in kws]

    scored = {}
    for cid, cl in claims.items():
        text = re.sub(r"[\[\]|]", " ", cl.get("canonical", ""))
        hits = [(c, p, l) for c, p, l in labelled if ca.has_phrase(text, p)]
        score = sum(WEIGHT.get(c, 1) for c, p, l in hits if l == "stated")
        scored[cid] = (score, hits)

    out = [f"# Claim ranking: {folder.name}", "",
           "Advisory. Not a fit score. Owner chooses; bullets come from spec.json.", ""]
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

    corpus = ca.norm(" ".join(re.sub(r"[\[\]|]", " ", c.get("canonical", "")) for c in claims.values()))
    gap = [(c, p) for c, p in kws if c != "Hard Filter" and not ca.has_phrase(corpus, p)]
    out.append("## Phrases no claim contains (real gaps unless the JD wording differs)")
    out += [f"- {p} [{c}]" for c, p in gap] or ["- none"]
    out.append("")
    cov = {}
    for c, p, l in labelled:
        if c == "Hard Filter":
            continue
        d = cov.setdefault(c, [0, 0])
        d[1] += 1
        d[0] += any(ca.has_phrase(re.sub(r"[\[\]|]", " ", cl.get("canonical", "")), p) for cl in claims.values())
    out.append("## KB support by category (phrases found in at least one claim)")
    out += [f"- {c}: {h}/{t}" for c, (h, t) in cov.items()]
    text = "\n".join(out)
    print(text)
    if a.out:
        (folder / Path(a.out).name).write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
