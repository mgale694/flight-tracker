#!/bin/bash
# Compatibility helper for older setup instructions.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Hardware modules are installed as Raspberry Pi OS packages."
echo "The .venv-pi environment can see them through --system-site-packages."

if [ "$EUID" -eq 0 ]; then
    exec "$SCRIPT_DIR/install-gpio-packages.sh"
fi

exec sudo "$SCRIPT_DIR/install-gpio-packages.sh"
