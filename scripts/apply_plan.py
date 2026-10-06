#!/usr/bin/env python3
"""Execute an APPROVED rename/organize plan safely.

Plan file: CSV with columns  old_path,new_path,action,reason
  action = copy | move | skip
  Default behavior is DRY RUN. Nothing changes without --apply.
  Every applied operation is logged with a content hash so it can be undone.

Safety rules enforced:
  - old_path must exist; new_path must not exist; no duplicate new_path
  - paths must stay inside the project root (no ../ escapes)
  - nothing may be written into _raw/, and nothing may be moved out of _raw/
    (originals stay untouched; use action=copy)

Usage:
    python apply_plan.py _work/plan.csv              # validate + dry run
    python apply_plan.py _work/plan.csv --apply      # execute
    python apply_plan.py --undo                      # reverse last applied run
"""
import argparse
import csv
import hashlib
import shutil
import sys
from datetime import datetime
from pathlib import Path

LOG = Path("_work/apply_log.csv")
ACTIONS = {"copy", "move", "skip"}
RAW = "_raw"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def inside_root(p: Path, root: Path) -> bool:
    try:
        p.resolve().relative_to(root)
        return True
    except ValueError:
        return False


def in_raw(p: Path, root: Path) -> bool:
    try:
        return p.resolve().relative_to(root).parts[0] == RAW
    except (ValueError, IndexError):
        return False


def load_plan(plan_path: Path, root: Path):
    rows, errors, seen = [], [], set()
    with open(plan_path, newline="") as f:
        reader = csv.DictReader(f)
        need = {"old_path", "new_path", "action"}
        if not need.issubset(reader.fieldnames or []):
            sys.exit(f"error: plan must have columns {sorted(need)} (+ optional reason)")
        for n, r in enumerate(reader, start=2):
            action = (r["action"] or "").strip().lower()
            old, new = Path(r["old_path"].strip()), Path(r["new_path"].strip())
            if action not in ACTIONS:
                errors.append(f"line {n}: bad action {action!r}")
                continue
            if action == "skip":
                rows.append((old, new, action))
                continue
            if not old.exists():
                errors.append(f"line {n}: missing source {old}")
            if new.exists():
                errors.append(f"line {n}: destination already exists {new}")
            if str(new) in seen:
                errors.append(f"line {n}: duplicate destination {new}")
            seen.add(str(new))
            if not inside_root(old, root) or not inside_root(new, root):
                errors.append(f"line {n}: path escapes project root")
            if in_raw(new, root):
                errors.append(f"line {n}: may not write into {RAW}/ ({new})")
            if action == "move" and in_raw(old, root):
                errors.append(f"line {n}: may not move out of {RAW}/, use copy ({old})")
            rows.append((old, new, action))
    return rows, errors


def apply(rows):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    new_log = not LOG.exists()
    ts = datetime.now().isoformat(timespec="seconds")
    with open(LOG, "a", newline="") as f:
        w = csv.writer(f)
        if new_log:
            w.writerow(["timestamp", "action", "old_path", "new_path", "sha256"])
        for old, new, action in rows:
            if action == "skip":
                continue
            new.parent.mkdir(parents=True, exist_ok=True)
            digest = sha(old)
            if action == "copy":
                shutil.copy2(old, new)
            else:
                shutil.move(str(old), str(new))
            w.writerow([ts, action, str(old), str(new), digest])
            print(f"{action:4} {old} -> {new}")


def undo():
    """Reverse only the most recent applied run (entries sharing the last timestamp)."""
    if not LOG.exists():
        sys.exit("nothing to undo: no apply log found")
    with open(LOG, newline="") as f:
        entries = list(csv.DictReader(f))
    if not entries:
        sys.exit("nothing to undo: apply log is empty")
    last_ts = entries[-1]["timestamp"]
    run = [e for e in entries if e["timestamp"] == last_ts]
    rest = [e for e in entries if e["timestamp"] != last_ts]
    problems = 0
    for e in reversed(run):
        old, new = Path(e["old_path"]), Path(e["new_path"])
        if not new.exists():
            print(f"skip (already gone): {new}")
            continue
        if sha(new) != e["sha256"]:
            print(f"KEPT (edited since apply, not reverting): {new}")
            problems += 1
            continue
        if e["action"] == "copy":
            new.unlink()
        else:
            old.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(new), str(old))
        print(f"undone {e['action']}: {new}")
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    cols = ["timestamp", "action", "old_path", "new_path", "sha256"]
    with open(LOG.with_name(f"apply_log.undone-{stamp}.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(run)
    if rest:
        with open(LOG, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rest)
    else:
        LOG.unlink()
    if problems:
        print(f"{problems} file(s) were edited after apply and were left in place.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("plan", nargs="?")
    ap.add_argument("--apply", action="store_true", help="execute (default is dry run)")
    ap.add_argument("--undo", action="store_true", help="reverse the last applied run")
    args = ap.parse_args()
    root = Path.cwd().resolve()

    if args.undo:
        undo()
        return 0
    if not args.plan:
        ap.error("plan file required (or use --undo)")

    rows, errors = load_plan(Path(args.plan), root)
    if errors:
        print("PLAN REJECTED:")
        for e in errors:
            print("  -", e)
        return 1
    ops = [r for r in rows if r[2] != "skip"]
    if not args.apply:
        print(f"DRY RUN: {len(ops)} operation(s), {len(rows) - len(ops)} skipped. Plan is valid.")
        for old, new, action in ops:
            print(f"  {action:4} {old} -> {new}")
        print("Re-run with --apply to execute.")
        return 0
    apply(rows)
    print(f"done: {len(ops)} operation(s). Log: {LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
