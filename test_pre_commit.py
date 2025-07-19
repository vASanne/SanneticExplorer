#!/usr/bin/env python3
"""
Test script to verify pre-commit setup

This script can be used to test that pre-commit hooks are working correctly.
"""

import subprocess
import sys
from pathlib import Path


def test_pre_commit_installation() -> bool:
    """Test if pre-commit is installed and working"""
    try:
        result = subprocess.run(
            ["pre-commit", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        print(f"✅ Pre-commit version: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Pre-commit not found. Install with: pip install pre-commit")
        return False


def test_pre_commit_hooks() -> bool:
    """Test if pre-commit hooks are installed"""
    try:
        result = subprocess.run(
            ["pre-commit", "run", "--all-files"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            print("✅ Pre-commit hooks passed")
            return True
        else:
            print("❌ Pre-commit hooks failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running pre-commit hooks: {e}")
        return False


def test_individual_tools() -> bool:
    """Test individual code quality tools"""
    tools = [
        ("black", ["black", "--version"]),
        ("ruff", ["ruff", "--version"]),
        ("mypy", ["mypy", "--version"]),
        ("isort", ["isort", "--version"]),
    ]
    
    all_passed = True
    for tool_name, cmd in tools:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ {tool_name}: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ {tool_name} not found")
            all_passed = False
    
    return all_passed


def main() -> None:
    """Main test function"""
    print("🧪 Testing Pre-commit Setup")
    print("=" * 40)
    
    # Test pre-commit installation
    if not test_pre_commit_installation():
        sys.exit(1)
    
    # Test individual tools
    if not test_individual_tools():
        print("\n💡 Install missing tools with: pip install black ruff mypy isort")
        sys.exit(1)
    
    # Test pre-commit hooks
    print("\n🔍 Running pre-commit hooks...")
    if not test_pre_commit_hooks():
        print("\n💡 Fix issues above or run: make format")
        sys.exit(1)
    
    print("\n🎉 All pre-commit tests passed!")


if __name__ == "__main__":
    main() 