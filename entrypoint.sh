#!/usr/bin/env bash
# Custom Docker entrypoint: auto-upgrades this project's own module against
# the configured dev db on every container start, then hands off to the
# official odoo:19.0 image's own /entrypoint.sh to actually start the server.
#
# Why: without this, picking up a code change (new field, new model, a view
# edit) requires a manual Apps > Upgrade click after every `docker compose up`.
# This runs that upgrade automatically, quietly skipping it on the very first
# run (db doesn't exist / module not installed yet) since the README's manual
# "Apps > Install" step still has to happen once.
set -euo pipefail

apps_to_upgrade=("inventory_management")

db_name="${DB_NAME:-}"
if [ -z "$db_name" ] && [ -f /etc/odoo/odoo.conf ]; then
  db_name="$(grep -E '^\s*db_name\s*=' /etc/odoo/odoo.conf | head -1 | cut -d'=' -f2 | xargs || true)"
fi

join_by_comma() {
  local IFS=,
  echo "$*"
}

if [ -n "$db_name" ] && [ ${#apps_to_upgrade[@]} -gt 0 ]; then
  echo "Upgrading modules: ${apps_to_upgrade[*]} (db: $db_name)"
  if odoo -d "$db_name" -u "$(join_by_comma "${apps_to_upgrade[@]}")" --no-http --stop-after-init; then
    echo "Upgrading modules: done"
  else
    echo "Upgrading modules: skipped (db '$db_name' not installed yet - fine on first run, use Apps > Install once)"
  fi
else
  echo "Upgrading modules: skipped (no db_name configured in odoo.conf)"
fi

exec /entrypoint.sh "$@"
