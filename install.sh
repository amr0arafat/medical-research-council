#!/usr/bin/env bash
# Install the medical-research-council skill for Claude Code, Codex, and/or Gemini CLI.
#
#   bash install.sh [--claude] [--codex] [--gemini] [--all] [--link] [--uninstall]
#
# --claude  -> ~/.claude/skills/medical-research-council
# --codex   -> ~/.agents/skills/medical-research-council  (shared with Gemini CLI)
# --gemini  -> ~/.agents/skills/medical-research-council  (shared with Codex)
# --link    symlink instead of copy, so edits in this repo apply immediately
# No target flag means --all.
set -euo pipefail

NAME="medical-research-council"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills/$NAME"
LINK=0
UNINSTALL=0
TARGETS=()

for arg in "$@"; do
  case "$arg" in
    --claude) TARGETS+=("$HOME/.claude/skills") ;;
    --codex|--gemini) TARGETS+=("$HOME/.agents/skills") ;;
    --all) TARGETS+=("$HOME/.claude/skills" "$HOME/.agents/skills") ;;
    --link) LINK=1 ;;
    --uninstall) UNINSTALL=1 ;;
    -h|--help) sed -n '2,11p' "$0"; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; exit 1 ;;
  esac
done
[ ${#TARGETS[@]} -eq 0 ] && TARGETS=("$HOME/.claude/skills" "$HOME/.agents/skills")

if [ ! -f "$SRC/SKILL.md" ]; then
  echo "Cannot find $SRC/SKILL.md. Run this script from the repository." >&2
  exit 1
fi

# De-duplicate (--codex and --gemini share a folder).
UNIQUE=$(printf '%s\n' "${TARGETS[@]}" | awk '!seen[$0]++')

while IFS= read -r dir; do
  dest="$dir/$NAME"
  if [ "$UNINSTALL" -eq 1 ]; then
    if [ -e "$dest" ] || [ -L "$dest" ]; then rm -rf "$dest"; echo "Removed $dest"; fi
    continue
  fi
  mkdir -p "$dir"
  if [ -e "$dest" ] || [ -L "$dest" ]; then rm -rf "$dest"; fi
  if [ "$LINK" -eq 1 ]; then
    ln -s "$SRC" "$dest"; echo "Linked  $dest -> $SRC"
  else
    cp -R "$SRC" "$dest"; echo "Copied  $dest"
  fi
done <<< "$UNIQUE"

[ "$UNINSTALL" -eq 1 ] || echo "Done. Restart your agent, then say: run the medical research council on <your idea>."
