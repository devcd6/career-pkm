#!/bin/bash
# SessionStart hook (web sessions only): print the last handoff for the current application branch.
# On an application branch (its diff against origin/main touches applications/) print the newest
# applications/*/handoff.md changed on it. On main or any other branch print a one-line list of
# applications that have a handoff. Output is added to the session as context. Read-only.
set -uo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ] && [ "${HANDOFF_HOOK_FORCE:-}" != "1" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}" || exit 0
git rev-parse --git-dir >/dev/null 2>&1 || exit 0

branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
base=origin/main
git rev-parse --verify -q "$base" >/dev/null 2>&1 || base=main

shopt -s nullglob
all=(applications/*/handoff.md)
[ ${#all[@]} -eq 0 ] && exit 0

# Newest handoff by last commit time among the given files.
newest() {
  local best="" bt=0 t f
  for f in "$@"; do
    t=$(git log -1 --format=%ct -- "$f" 2>/dev/null || echo 0)
    [ -z "$t" ] && t=0
    if [ -z "$best" ] || [ "$t" -gt "$bt" ]; then best=$f; bt=$t; fi
  done
  printf '%s' "$best"
}

on_app_branch=0
case "$branch" in
  main|master|HEAD|"") ;;
  *)
    if git diff --name-only "$base"...HEAD 2>/dev/null | grep -q '^applications/'; then
      on_app_branch=1
    fi ;;
esac

if [ "$on_app_branch" = 1 ]; then
  changed=()
  for f in "${all[@]}"; do
    git diff --name-only "$base"...HEAD 2>/dev/null | grep -qx "$f" && changed+=("$f")
  done
  [ ${#changed[@]} -eq 0 ] && changed=("${all[@]}")
  pick=$(newest "${changed[@]}")
  echo "== Handoff from the last session on this application branch ($pick) =="
  echo "Read it before doing anything else, then follow CLAUDE.md. It is a summary, not a source of facts."
  echo
  head -n 200 "$pick"
else
  echo "== Application handoffs available (read one before continuing that application) =="
  for f in "${all[@]}"; do echo "- $f"; done
fi
exit 0
