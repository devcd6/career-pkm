#!/usr/bin/env python3
"""Shared claims-view loader and keyword helpers.

The application checks that used to live here moved to career-applications. What remains is
imported by rank_claims.py, import_interview_packet.py and check_interview_prep.py:
load_claims, norm, has_phrase, variant_phrase, read_keywords, unknown_category_lines,
numbers_in, metric_tokens, wordset and the MON / RULING_NUMBERS constants.

Numbers are compared as literal tokens ("6,000+" must appear as "6,000+" in a claim's metrics),
except that a count written as a word in metrics ("four", two through twelve) also allows its
digit ("4"). "4+" (years of experience) is an owner ruling in kb/_user_decisions.md.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULING_NUMBERS = {"4+"}
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


def numbers_in(text):
    """Numeric tokens in text, ignoring dates, years and regulation/product identifiers."""
    text = IDENT_RE.sub(" ", DATE_RE.sub(" ", text))
    return [t for t in NUM_RE.findall(text) if not re.fullmatch(r"(19|20)\d\d", t)]


def metric_tokens(claim):
    m = claim.get("metrics", "")
    words = {w for w in re.findall(r"[a-z]+", m.lower()) if w in WORDNUM}
    return set(NUM_RE.findall(m)) | words | {WORD_DIGITS[w] for w in words if w in WORD_DIGITS}


def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


def load_claims(path):
    roles, claims, cur = {}, {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            cur = None
            continue
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


CATEGORIES = ["title keyword", "hard skill", "action keyword", "business context", "domain keyword", "hard filter", "forced"]


def read_keywords(path):
    """keywords.txt lines: 'phrase' or 'Category | phrase'. Returns [(category, phrase)]."""
    out = []
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        cat, _, rest = line.partition("|")
        if rest and cat.strip().lower() in CATEGORIES:
            out.append((cat.strip().title(), rest.strip()))
        else:
            out.append(("Uncategorized", line))
    return out


def has_phrase(text, phrase):
    return re.search(r"(?<!\w)" + re.escape(norm(phrase)) + r"(?!\w)", norm(text), re.I) is not None


def _stem(word):
    for suffix in ("ance", "ence", "ing", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            word = word[: -len(suffix)]
            break
    return word[:-1] if word.endswith("e") and len(word) > 4 else word


def _stems(text):
    return [_stem(w) for w in re.findall(r"[a-z0-9']+", norm(text).replace("-", " "))]


def variant_phrase(text, phrase):
    """True when phrase appears with simple inflection or hyphenation differences
    ("report" for "reports", "troubleshooting" for "trouble-shoot"). Advisory only; never a provenance check."""
    want = _stems(phrase)
    if not want:
        return False
    have = _stems(text)
    n = len(want)
    if any(have[i:i + n] == want for i in range(len(have) - n + 1)):
        return True
    if "-" in phrase:  # "trouble-shoot" vs "troubleshooting"
        joined = re.sub(r"[^a-z0-9]", "", norm(phrase))
        return any(tok.startswith(joined) for tok in re.findall(r"[a-z0-9']+", norm(text)))
    return False


def unknown_category_lines(path):
    """keywords.txt lines that contain '|' but whose category is not one of CATEGORIES (read_keywords keeps them as Uncategorized)."""
    bad = []
    if not path.exists():
        return bad
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "|" in line and line.partition("|")[0].strip().lower() not in CATEGORIES:
            bad.append(line)
    return bad


def wordset(b):
    return set(re.findall(r"[a-z0-9']+", b.lower()))


