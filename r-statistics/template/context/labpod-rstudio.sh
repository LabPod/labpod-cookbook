#!/usr/bin/env bash
# Rootless single-user rserver launcher. LabPod runs the container as the
# workspace owner with --cap-drop=ALL / no-new-privileges / --userns=keep-id,
# so RStudio Server's default root+PAM multi-user model cannot start. Run
# rserver as the current user with no PAM and every writable path under a
# per-run runtime dir; LabPod's reverse proxy (JWT + owner check) is the
# access boundary.
set -euo pipefail

runtime_dir="${XDG_RUNTIME_DIR:-/tmp}/labpod-rstudio-$(id -u)"
mkdir -p "$runtime_dir/run" "$runtime_dir/db"
chmod 700 "$runtime_dir"

db_conf="$runtime_dir/database.conf"
printf 'provider=sqlite\ndirectory=%s/db\n' "$runtime_dir" > "$db_conf"

cookie_key="$runtime_dir/secure-cookie-key"
if [ ! -f "$cookie_key" ]; then
  openssl rand -hex 32 > "$cookie_key"
  chmod 600 "$cookie_key"
fi

# Open sessions in /work, mirroring the Jupyter launcher's
# --ServerApp.root_dir: /work persists across workspace stop/start and is
# shared by the owner's concurrent workspaces, while $HOME is per-workspace.
# rserver takes no command-line flag for this — it is an rsession setting,
# and the image's /etc/rstudio/rsession.conf holds nothing else.
session_conf="$runtime_dir/rsession.conf"
printf 'session-default-working-dir=/work\n' > "$session_conf"

exec /usr/lib/rstudio-server/bin/rserver \
  --rsession-config-file="$session_conf" \
  --server-user="$(id -un)" \
  --server-daemonize=0 \
  --server-data-dir="$runtime_dir/run" \
  --server-pid-file="$runtime_dir/rstudio-server.pid" \
  --auth-none=1 \
  --www-address=0.0.0.0 \
  --secure-cookie-key-file="$cookie_key" \
  --database-config-file="$db_conf" \
  --rsession-which-r="$(command -v R)" \
  "$@"
