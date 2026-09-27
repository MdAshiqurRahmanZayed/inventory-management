#!/usr/bin/env bash
# Fetches third-party (OCA) Odoo addons into extra-addons/.
# extra-addons/ is gitignored - this script is how a fresh clone gets them back.
#
# To add a module, add one line to MODULES below: "repo_url|branch|module_name".
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

MODULES=(
  "https://github.com/OCA/web.git|19.0|web_responsive"
)

fetch_module() {
  local repo_url="$1" branch="$2" module="$3"
  local dest="extra-addons/${module}"

  if [ -d "$dest" ]; then
    echo "Skipping ${module}: extra-addons/${module} already exists."
    return
  fi

  echo "Fetching ${module} (${repo_url}@${branch})..."
  local tmp
  tmp="$(mktemp -d)"
  git clone --depth 1 --branch "$branch" --filter=blob:none --sparse "$repo_url" "$tmp" >/dev/null
  git -C "$tmp" sparse-checkout set "$module" >/dev/null
  mkdir -p extra-addons
  cp -R "$tmp/$module" "$dest"
  rm -rf "$tmp" "$dest/.git"
  find "$dest" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
  echo "-> extra-addons/${module}"
}

for entry in "${MODULES[@]}"; do
  IFS='|' read -r repo_url branch module <<<"$entry"
  fetch_module "$repo_url" "$branch" "$module"
done
