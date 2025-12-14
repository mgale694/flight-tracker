# 🔧 Display Fix - Multiple Issues

## The Problems

### Issue 1: Virtual Environment Mismatch

✅ **Diagnostic passes** - `./scripts/diagnose-display.sh` shows all modules available  
❌ **Display fails** - Flight tracker shows "No module named 'spidev'"

**Why?** System Python (used by diagnostic) ≠ Virtual Environment Python (used by flight tracker)

### Issue 2: Missing lgpio Module

❌ **Error:** `Failed to add edge detection`  
❌ **Warning:** `Falling back from lgpio: No module named 'lgpio'`

**Why?** gpiozero needs lgpio library for GPIO pin control on modern Raspberry Pi OS

## Quick Fix

```bash
cd ~/flight-tracker

# 1. Install ALL required packages (including lgpio)
./scripts/fix-venv-hardware.sh

# 2. Test display hardware works
./scripts/test-display.sh

# 3. Run full system (now uses venv Python consistently)
./scripts/start-raspi-all.sh
```

**Note:** The start script was updated to use `python` (venv) instead of `python3` (system) so packages are found correctly.

## Test Display First!

Before running the full system, test just the display:

```bash
./scripts/test-display.sh
```

This will:

- Check Python modules in the current environment
- Initialize the display hardware
- Render a test pattern
- Confirm everything works

**Takes 10 seconds, no backend/frontend needed!**

## Expected Output

### Good ✅

```
✅ spidev module available
✅ gpiozero module available
✅ RPi.GPIO module available
✅ Display initialized successfully!
✅ Image rendered to display successfully!
🎉 Check your e-ink display - you should see the test pattern!
```

### Bad ❌

```
❌ spidev - SPI communication - ERROR: No module named 'spidev'
```

Fix with: `./scripts/fix-venv-hardware.sh`

## Manual Fix

If the automated script doesn't work:

```bash
# Option 1: Install in backend venv
cd ~/flight-tracker/src/backend
source venv/bin/activate
pip install spidev gpiozero RPi.GPIO
deactivate

# Option 2: Install system-wide
pip3 install spidev gpiozero RPi.GPIO --break-system-packages

# Option 3: Use system packages
sudo apt-get install python3-spidev python3-gpiozero python3-rpi.gpio
```

## Scripts Overview

| Script                 | What It Does        | Time | Needs Display |
| ---------------------- | ------------------- | ---- | ------------- |
| `diagnose-display.sh`  | Check system Python | 5s   | No            |
| `fix-venv-hardware.sh` | Install in venv     | 30s  | No            |
| `test-display.sh`      | **Test hardware**   | 10s  | **Yes**       |
| `start-raspi-all.sh`   | Run full system     | ∞    | Yes           |

## Still Not Working?

Try with sudo:

```bash
sudo ./scripts/test-display.sh
```

If it works with sudo, add yourself to gpio/spi groups:

```bash
sudo usermod -a -G spi,gpio $USER
# Then logout/login or reboot
```
