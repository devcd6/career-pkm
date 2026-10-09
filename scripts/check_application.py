#!/usr/bin/env python3
"""Check an application folder against the knowledge base.

Usage:
    python scripts/check_application.py applications/<slug>
    python scripts/check_application.py applications/<slug> --claims kb/_views/claims.md

Errors (exit 1):
  provenance   a number in resume.md or cover-letter.md not in any claim's metrics; for resume bullets, not in the metrics of the claim(s) the bullet maps to
  titles       role title not one of the KB title variants (NCMW must be "Project Coordinator")
  dates        role dates differ from the KB role header
  counts       bullets per role outside the owner's ranges
  verbs        a role repeats a starting verb
  dashes       em dash in narrative text
  spacing      blank line between bullets or skill lines, or two blank lines in a row
  summary      summary does not end with a "Committed to" / "Dedicated to" sentence
  claims-used  a resume bullet missing from claims-used.md, or mapped to an unknown claim ID
Warnings: starting verb not among the claim's canonical wording; use of allowed_numbers.txt.

Provenance borrows the idea (not the code) of career-ops. Numbers are compared as
literal tokens ("6,000+" must appear as "6,000+" in a claim's metrics), except that a count
written as a word in metrics ("four", two through twelve) also allows its digit ("4"). Years and
dates are checked by the dates check instead. "4+" (years of experience) is an
owner ruling in kb/_user_decisions.md and is always allowed. A reviewed list of extra
numbers may go in <slug>/allowed_numbers.txt (one per line); the check reports its use.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RANGES = {  # role id (claims view '## <id>') -> (min, max); owner preferences
    "ncmw-project-coordinator": (9, 14),
    "ucsb-research-assistant": (5, 8),
    "sanctuary-centers-housing-coordinator": (8, 11),
    "asei-marketing-specialist": (4, 7),
    "casa-serena-program-assistant": (4, 6),
}
RULING_NUMBERS = {"4+"}
MONTHS = "jan feb mar apr may jun jul aug sep oct nov dec".split()
MON = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"
DATE_RE = re.compile(rf"({MON})\s+(\d{{4}})\s*[-–—]+\s*(?:({MON})\s+(\d{{4}})|(Present|present|Current))")
NUM_RE = re.compile(r"(?<![\w.])\$?\d[\d,]*(?:\.\d+)?[+%]?")
WORDNUM = "two three four five six seven eight nine ten eleven twelve fifteen twenty thirty forty fifty hundred thousand dozen".split()
# A count written as a word in a claim's metrics also allows its digit form in a bullet (owner approved 2026-10-09).
# Limited to two through twelve; "one" is left out because it is also a pronoun.
WORD_DIGITS = dict(zip("two three four five six seven eight nine ten eleven twelve".split(), map(str, range(2, 13))))
IDENT_RE = re.compile(
    r"\bCFR\s*Part\s*\d+|\b\d+\s*CFR\b(?:\s*Part\s*\d+)?|\bPart\s*\d+|\bSection\s*\d+[\w/]*|\bWCAG\s*\d+(?:\.\d+)*"
    r"|\bM-\d+-\d+|\bSF-\d+\w*|\bRMF\s*\d+(?:\.\d+)*|\bISO\s*\d+|\bNCT\d+|\bRise\s*\d+|\bOffice\s*365|\b[A-Z]{2,}-\d+\w*")
SKIP_SECTIONS = ("education", "certification", "skill", "header", "publication")


def numbers_in(text):
    """Numeric tokens in text, ignoring dates, years and regulation/product identifiers."""
    text = IDENT_RE.sub(" ", DATE_RE.sub(" ", text))
    return [t for t in NUM_RE.findall(text) if not re.fullmatch(r"(19|20)\d\d", t)]


def metric_tokens(claim):
    m = claim.get("metrics", "")
    words = {w for w in re.findall(r"[a-z]+", m.lower()) if w in WORDNUM}
    return set(NUM_RE.findall(m)) | words | {WORD_DIGITS[w] for w in words if w in WORD_DIGITS}


def norm(s):
    return re.sub(r"\s+", " ", s.replace("’", "'")).strip().lower()


def load_claims(path):
    roles, claims, cur = {}, {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            cur = {"id": line[3:].strip()}
            roles[cur["id"]] = cur
        elif cur is not None and re.match(r"(employer|title|dates|location): ", line):
            k, _, v = line.partition(": ")
            cur[k] = v.strip()
        m = re.match(r"### (A-\S+) \| (\S+)", line)
        if m:
            claims[m.group(1)] = {"tier": m.group(2), "role": cur["id"] if cur else ""}
        elif claims and line.startswith("canonical: "):
            claims[list(claims)[-1]]["canonical"] = line[11:]
        elif claims and line.startswith("metrics: "):
            claims[list(claims)[-1]]["metrics"] = line[9:]
    return roles, claims


def ym(mon, year):
    return f"{int(year):04d}-{MONTHS.index(mon[:3].lower()) + 1:02d}"


def parse_resume(text):
    """Split into sections {name: [lines]} and role blocks."""
    sections, order, name = {"header": []}, ["header"], "header"
    for line in text.splitlines():
        m = re.match(r"#{1,3}\s*\**(.+?)\**\s*$", line)
        if m and not line.startswith("# "):
            name = m.group(1).strip()
            sections[name] = []
            order.append(name)
        else:
            sections[name].append(line)
    return sections, order


def role_for(name, roles):
    n = norm(name)
    for rid, r in roles.items():
        emp = r.get("employer", "")
        acro = re.search(r"\(([^)]+)\)", emp)
        full = norm(re.sub(r"\s*\([^)]*\)", "", emp))
        if full and full in n or (acro and norm(acro.group(1)) == n):
            return rid
    return None


def bullets_of(lines):
    return [re.sub(r"^\s*[-*•]\s+", "", l).strip() for l in lines if re.match(r"\s*[-*•]\s+", l)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--claims", default=str(ROOT / "kb" / "_views" / "claims.md"))
    a = ap.parse_args()
    folder = Path(a.folder)
    errors, warns = [], []
    err = lambda k, m: errors.append(f"[{k}] {m}")
    roles, claims = load_claims(Path(a.claims))
    if not claims:
        print("no claims loaded; run scripts/build_claims_view.py")
        return 2
    base = set(RULING_NUMBERS)
    allowed = set(base)
    for c in claims.values():
        allowed |= metric_tokens(c)
    extra = folder / "allowed_numbers.txt"
    if extra.exists():
        ex = {l.strip() for l in extra.read_text(encoding="utf-8").splitlines() if l.strip()}
        allowed |= ex
        base |= ex
        warns.append(f"allowed_numbers.txt in use ({', '.join(sorted(ex)) or 'empty'}); owner must review")

    docs = {n: (folder / n) for n in ("resume.md", "cover-letter.md")}
    for n, p in docs.items():
        if not p.exists():
            warns.append(f"{n} not found; skipped")
    texts = {n: p.read_text(encoding="utf-8") for n, p in docs.items() if p.exists()}

    # dashes
    for n, t in texts.items():
        for i, l in enumerate(t.splitlines(), 1):
            if "—" in l:
                err("dashes", f"{n}:{i} em dash")

    resume = texts.get("resume.md")
    all_bullets = []
    if resume:
        sections, order = parse_resume(resume)
        # provenance (resume)
        for sname in order:
            if any(s in sname.lower() for s in SKIP_SECTIONS):
                continue
            body = "\n".join(l for l in sections[sname]
                             if "@" not in l and not re.match(r"\s*[-*\u2022]\s", l))
            for tok in sorted(set(numbers_in(body))):
                if tok in allowed:
                    continue
                err("provenance", f"resume.md [{sname}] number {tok!r} not in any claim's metrics")
        # roles
        for sname in order:
            rid = role_for(sname, roles)
            if not rid:
                continue
            lines = sections[sname]
            block = "\n".join(lines)
            bl = bullets_of(lines)
            all_bullets += [(rid, b) for b in bl]
            lo, hi = RANGES.get(rid, (0, 999))
            if not lo <= len(bl) <= hi:
                err("counts", f"{rid}: {len(bl)} bullets, range {lo}-{hi}")
            verbs = [re.match(r"[\w'-]+", b).group(0).lower() for b in bl if re.match(r"[\w'-]+", b)]
            for v in sorted({v for v in verbs if verbs.count(v) > 1}):
                err("verbs", f"{rid}: starting verb {v!r} used {verbs.count(v)} times")
            head = block.split("\n- ")[0]
            variants = [v.strip() for v in roles[rid].get("title", "").split("|")]
            if rid.startswith("ncmw"):
                variants = ["Project Coordinator"]
                if re.search(r"junior", head, re.I):
                    err("titles", f"{rid}: title must be 'Project Coordinator' (found 'Junior')")
            if not any(norm(v) in norm(head) for v in variants):
                err("titles", f"{rid}: none of {variants} found in role heading")
            kb_dates = roles[rid].get("dates", "")
            m = DATE_RE.search(head)
            if not m:
                err("dates", f"{rid}: no date range found in role heading")
            else:
                start = ym(m.group(1), m.group(2))
                end = ym(m.group(3), m.group(4)) if m.group(3) else "present"
                if f"{start} to {end}" != kb_dates:
                    err("dates", f"{rid}: resume {start} to {end}, KB {kb_dates}")
            # spacing
            for i in range(1, len(lines) - 1):
                if not lines[i].strip() and re.match(r"\s*[-*•]\s", lines[i - 1]) and re.match(r"\s*[-*•]\s", lines[i + 1]):
                    err("spacing", f"{rid}: blank line between bullets")
                    break
        for sname in order:
            if "skill" in sname.lower():
                ls = sections[sname]
                for i in range(1, len(ls) - 1):
                    if not ls[i].strip() and ls[i - 1].strip() and ls[i + 1].strip():
                        err("spacing", f"[{sname}] blank line between skill lines")
                        break
        if re.search(r"\n[ \t]*\n[ \t]*\n", resume):
            err("spacing", "resume.md has two blank lines in a row")
        # summary
        key = next((s for s in order if "summary" in s.lower()), None)
        if not key:
            err("summary", "no SUMMARY section")
        else:
            text = " ".join(l.strip() for l in sections[key] if l.strip())
            sents = re.split(r"(?<=[.!?])\s+", text)
            if not sents or not re.match(r"(Committed|Dedicated) to\b", sents[-1]):
                err("summary", "summary must end with a 'Committed to...' or 'Dedicated to...' sentence")

    cover = texts.get("cover-letter.md")
    if cover:
        body = "\n".join(l for l in cover.splitlines() if "@" not in l)
        for tok in sorted(set(numbers_in(body))):
            if tok not in allowed:
                err("provenance", f"cover-letter.md number {tok!r} not in any claim's metrics")

    # claims-used
    cu = folder / "claims-used.md"
    if resume and not cu.exists():
        err("claims-used", "claims-used.md missing")
    elif resume:
        lines = cu.read_text(encoding="utf-8").splitlines()
        nlines = [norm(l) for l in lines]
        for l in lines:
            for cid in re.findall(r"A-[\w-]+", l):
                if cid not in claims:
                    err("claims-used", f"unknown claim ID {cid}")
        for rid, b in all_bullets:
            nb = norm(b)
            hit = next((l for l, n in zip(lines, nlines) if nb in n), None)
            ids = re.findall(r"A-[\w-]+", hit or "")
            if not hit:
                err("claims-used", f"bullet not in claims-used.md: {b[:70]}...")
            elif not any(i in claims for i in ids):
                err("claims-used", f"no valid claim ID for bullet: {b[:70]}...")
            else:
                ok = set().union(*(metric_tokens(claims[i]) for i in ids if i in claims)) | base
                for tok in sorted(set(numbers_in(b))):
                    if tok not in ok:
                        err("provenance", f"bullet number {tok!r} not in metrics of {', '.join(ids)}: {b[:60]}...")
                verb = re.match(r"[\w'-]+", b).group(0).lower()
                canon = " ".join(claims[next(i for i in ids if i in claims)].get("canonical", "").split()[:14]).lower()
                if verb not in re.findall(r"[\w'-]+", canon):
                    warns.append(f"verb {verb!r} not in claim wording start: {b[:60]}...")

    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"{len(errors)} error(s), {len(warns)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
