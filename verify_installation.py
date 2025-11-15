#!/usr/bin/env python3
"""Verify that travelTools is properly installed and configured."""

import sys
from pathlib import Path


def check_file(path: str, description: str) -> bool:
    """Check if a file exists."""
    if Path(path).exists():
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} (missing: {path})")
        return False


def check_import(module: str, description: str) -> bool:
    """Check if a Python module can be imported."""
    try:
        __import__(module)
        print(f"✓ {description}")
        return True
    except ImportError as e:
        print(f"✗ {description} ({e})")
        return False


def main():
    """Run verification checks."""
    print("🌴 Travel Tools Installation Verification")
    print("=" * 50)
    print()

    checks = []

    # Check directory structure
    print("Checking directory structure...")
    checks.append(check_file("src/travel_tools", "Source directory"))
    checks.append(check_file("tests", "Tests directory"))
    checks.append(check_file("data", "Data directory"))
    checks.append(check_file("outputs", "Outputs directory"))
    checks.append(check_file("config", "Config directory"))
    checks.append(check_file("web_client", "Web client (Vue) directory"))
    print()

    # Check core files
    print("Checking core files...")
    checks.append(check_file("pyproject.toml", "Project configuration"))
    checks.append(check_file("requirements.txt", "Requirements file"))
    checks.append(check_file("README.md", "README"))
    checks.append(check_file("QUICKSTART.md", "Quick start guide"))
    print()

    # Check Python modules
    print("Checking Python modules...")
    checks.append(check_file("src/travel_tools/step1_filter.py", "Step 1: Filter"))
    checks.append(check_file("src/travel_tools/step2_scrape.py", "Step 2: Scrape"))
    checks.append(check_file("src/travel_tools/step3_merge.py", "Step 3: Merge"))
    checks.append(
        check_file("src/travel_tools/step4_generate_web.py", "Step 4: Generate web")
    )
    checks.append(check_file("src/travel_tools/launcher.py", "Launcher"))
    checks.append(check_file("src/travel_tools/types.py", "Type definitions"))
    print()

    # Check utilities
    print("Checking utilities...")
    checks.append(check_file("src/travel_tools/utils/logger.py", "Logger utility"))
    checks.append(check_file("src/travel_tools/utils/file_ops.py", "File ops utility"))
    checks.append(
        check_file("src/travel_tools/utils/validators.py", "Validators utility")
    )
    print()

    # Check tests
    print("Checking tests...")
    checks.append(check_file("tests/conftest.py", "Test configuration"))
    checks.append(check_file("tests/unit/test_filter.py", "Filter tests"))
    checks.append(check_file("tests/unit/test_scrape.py", "Scrape tests"))
    checks.append(check_file("tests/unit/test_merge.py", "Merge tests"))
    checks.append(check_file("tests/unit/test_generate_web.py", "Web generation tests"))
    print()

    # Check config
    print("Checking configuration...")
    checks.append(check_file("config/settings.json", "Settings"))
    checks.append(check_file("config/destinations.json", "Destinations"))
    print()

    # Check web client assets
    print("Checking web client...")
    checks.append(check_file("web_client/package.json", "Vue client package.json"))
    checks.append(check_file("web_client/src/App.vue", "Vue client entry component"))
    print()

    # Try imports (if in virtual environment)
    print("Checking Python imports...")
    checks.append(check_import("travel_tools", "travel_tools package"))
    checks.append(check_import("travel_tools.types", "Type definitions"))
    checks.append(check_import("travel_tools.launcher", "Launcher"))
    checks.append(check_import("pydantic", "Pydantic (dependency)"))
    checks.append(check_import("click", "Click (dependency)"))
    checks.append(check_import("rich", "Rich (dependency)"))
    print()

    # Summary
    print("=" * 50)
    passed = sum(checks)
    total = len(checks)
    percentage = (passed / total) * 100 if total > 0 else 0

    if passed == total:
        print(f"✅ All checks passed ({passed}/{total})")
        print()
        print("Installation is complete and ready to use!")
        print()
        print("Next steps:")
        print("  1. Add package data: mkdir -p data/cancun/transat/raw")
        print("  2. Run pipeline: python -m travel_tools.launcher")
        return 0
    else:
        print(f"⚠️  Some checks failed ({passed}/{total} passed, {percentage:.1f}%)")
        print()
        print("Please fix the missing items above.")
        print("Run: ./setup.sh to install dependencies")
        return 1


if __name__ == "__main__":
    sys.exit(main())
