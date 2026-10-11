#!/usr/bin/env bash
set -euo pipefail
# kineticos-plus: install the custom fastfetch config. User copy by default,
# --system also sets it as the machine default (needs root).
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)/../files/fastfetch-config.jsonc"
mkdir -p ~/.config/fastfetch
cp "$SRC" ~/.config/fastfetch/config.jsonc
chmod 644 ~/.config/fastfetch/config.jsonc
echo "installed ~/.config/fastfetch/config.jsonc"
# auto-run fastfetch in interactive bash terminals (kitty/konsole/alacritty all read ~/.bashrc)
if grep -q 'kineticos-plus fastfetch' ~/.bashrc 2>/dev/null; then
  echo "terminal auto-run already enabled in ~/.bashrc"
else
  cat >> ~/.bashrc <<'EOF'

# kineticos-plus fastfetch: run once per interactive terminal
if [ -z "${KINETICOS_PLUS_FASTFETCH_SHOWN:-}" ]; then
  export KINETICOS_PLUS_FASTFETCH_SHOWN=1
  case $- in *i*) [ -t 1 ] && command -v fastfetch >/dev/null 2>&1 && fastfetch;; esac
fi
EOF
  echo "enabled fastfetch auto-run in ~/.bashrc"
fi
if [ "${1:-}" = "--system" ]; then
  sudo mkdir -p /etc/fastfetch
  sudo cp "$SRC" /etc/fastfetch/config.jsonc
  echo "installed /etc/fastfetch/config.jsonc (system default)"
fi
