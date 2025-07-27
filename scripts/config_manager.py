#!/usr/bin/env python3
"""
Configuration Management Script
Helps synchronize configuration between backend and raspi
"""

import toml
import argparse
from pathlib import Path


def get_project_root():
    """Get the project root directory"""
    current_dir = Path(__file__).parent.absolute()
    # Go up until we find the main project directory
    while current_dir.parent != current_dir:
        if (current_dir / "src").exists():
            return current_dir
        current_dir = current_dir.parent
    return Path(__file__).parent.absolute()


def load_config(config_path):
    """Load configuration from TOML file"""
    try:
        with open(config_path, "r") as f:
            return toml.load(f)
    except Exception as e:
        print(f"Error loading config from {config_path}: {e}")
        return None


def save_config(config, config_path):
    """Save configuration to TOML file"""
    try:
        with open(config_path, "w") as f:
            toml.dump(config, f)
        return True
    except Exception as e:
        print(f"Error saving config to {config_path}: {e}")
        return False


def sync_configs():
    """Synchronize configuration files"""
    project_root = get_project_root()
    backend_config_path = project_root / "src" / "backend" / "config.toml"
    raspi_config_path = project_root / "src" / "raspi" / "config.toml"

    print(f"Project root: {project_root}")
    print(f"Backend config: {backend_config_path}")
    print(f"Raspi config: {raspi_config_path}")

    # Load both configs
    backend_config = load_config(backend_config_path)
    raspi_config = load_config(raspi_config_path)

    if not backend_config or not raspi_config:
        print("Failed to load one or both configuration files")
        return False

    # The backend config should be the master
    # Copy main settings from backend to raspi but preserve raspi-specific UI settings
    raspi_config["main"] = backend_config["main"]
    raspi_config["api"] = backend_config["api"]
    raspi_config["logging"] = backend_config["logging"]

    # Save updated raspi config
    if save_config(raspi_config, raspi_config_path):
        print("✓ Configuration synchronized successfully")
        return True
    else:
        print("❌ Failed to save synchronized configuration")
        return False


def show_config(config_type="both"):
    """Show current configuration"""
    project_root = get_project_root()

    if config_type in ["both", "backend"]:
        backend_config_path = project_root / "src" / "backend" / "config.toml"
        backend_config = load_config(backend_config_path)
        if backend_config:
            print("\n=== Backend Configuration ===")
            print(toml.dumps(backend_config))

    if config_type in ["both", "raspi"]:
        raspi_config_path = project_root / "src" / "raspi" / "config.toml"
        raspi_config = load_config(raspi_config_path)
        if raspi_config:
            print("\n=== Raspi Configuration ===")
            print(toml.dumps(raspi_config))


def update_address(new_address):
    """Update the address in both configuration files"""
    project_root = get_project_root()
    backend_config_path = project_root / "src" / "backend" / "config.toml"
    raspi_config_path = project_root / "src" / "raspi" / "config.toml"

    # Update backend config
    backend_config = load_config(backend_config_path)
    if backend_config:
        backend_config.setdefault("main", {})["address"] = new_address
        save_config(backend_config, backend_config_path)

    # Update raspi config
    raspi_config = load_config(raspi_config_path)
    if raspi_config:
        raspi_config.setdefault("main", {})["address"] = new_address
        save_config(raspi_config, raspi_config_path)

    print(f"✓ Address updated to: {new_address}")


def main():
    parser = argparse.ArgumentParser(
        description="Flight Tracker Configuration Management"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Sync command
    subparsers.add_parser("sync", help="Synchronize configuration files")

    # Show command
    show_parser = subparsers.add_parser("show", help="Show configuration")
    show_parser.add_argument(
        "--type",
        choices=["backend", "raspi", "both"],
        default="both",
        help="Which config to show",
    )

    # Update address command
    update_parser = subparsers.add_parser(
        "update-address", help="Update tracking address"
    )
    update_parser.add_argument("address", help="New address to track")

    args = parser.parse_args()

    if args.command == "sync":
        sync_configs()
    elif args.command == "show":
        show_config(args.type)
    elif args.command == "update-address":
        update_address(args.address)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
