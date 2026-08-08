#!/bin/bash
# One-time Raspberry Pi provisioning used by `make setup`.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v raspi-config >/dev/null; then
    echo "This setup target must be run on Raspberry Pi OS."
    exit 1
fi

echo "Provisioning Raspberry Pi system packages..."
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    git \
    make \
    nodejs \
    npm \
    python3 \
    python3-dev \
    python3-gpiozero \
    python3-lgpio \
    python3-pil \
    python3-rpi-lgpio \
    python3-spidev \
    python3-venv

echo "Enabling SPI..."
sudo raspi-config nonint do_spi 0

SKIP_SYSTEM_PACKAGES=1 "$SCRIPT_DIR/install-waveshare.sh"

if [ ! -e /dev/spidev0.0 ]; then
    echo
    echo "SPI is enabled in the boot configuration, but /dev/spidev0.0 is not ready."
    echo "Reboot once before running make pi."
fi
