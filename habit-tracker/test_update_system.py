#!/usr/bin/env python3
"""Test script to diagnose update system issues."""

import subprocess
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config


def run_command(cmd, description):
    """Run a command and show results."""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"Working dir: {Config.BASE_DIR}")
    print('-'*60)

    try:
        result = subprocess.run(
            cmd,
            cwd=Config.BASE_DIR,
            capture_output=True,
            text=True,
            timeout=10
        )

        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")

        return result
    except subprocess.TimeoutExpired:
        print("ERROR: Command timed out")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def main():
    print("="*60)
    print("UPDATE SYSTEM DIAGNOSTIC TEST")
    print("="*60)

    # Test 1: Check git is available
    result = run_command(["git", "--version"], "Check git is installed")
    if not result or result.returncode != 0:
        print("\n❌ FAIL: Git is not available!")
        return

    # Test 2: Check we're in a git repo
    result = run_command(["git", "rev-parse", "--git-dir"], "Check if in git repo")
    if not result or result.returncode != 0:
        print(f"\n❌ FAIL: Not in a git repo! BASE_DIR={Config.BASE_DIR}")
        return

    # Test 3: Check current branch
    result = run_command(["git", "branch", "--show-current"], "Check current branch")
    if result and result.returncode == 0:
        branch = result.stdout.strip()
        print(f"Current branch: {branch}")
        if branch != "main":
            print(f"⚠️  WARNING: Not on 'main' branch!")

    # Test 4: Check remote URL
    result = run_command(["git", "remote", "get-url", "origin"], "Check remote URL")
    if result and result.returncode == 0:
        remote = result.stdout.strip()
        print(f"Remote URL: {remote}")

    # Test 5: Check current commit
    result = run_command(["git", "rev-parse", "HEAD"], "Get current commit hash")
    if result and result.returncode == 0:
        local_hash = result.stdout.strip()[:8]
        print(f"Local commit: {local_hash}")

    # Test 6: Fetch from remote
    result = run_command(["git", "fetch", "origin", "main"], "Fetch from remote")
    if not result or result.returncode != 0:
        print("\n❌ FAIL: Could not fetch from remote!")
        print("Check WiFi connection and remote URL")
        return

    # Test 7: Check remote commit
    result = run_command(["git", "rev-parse", "origin/main"], "Get remote commit hash")
    if result and result.returncode == 0:
        remote_hash = result.stdout.strip()[:8]
        print(f"Remote commit: {remote_hash}")

    # Test 8: Count commits behind
    result = run_command(
        ["git", "rev-list", "--count", "HEAD..origin/main"],
        "Count commits behind remote"
    )
    if not result or result.returncode != 0:
        print("\n❌ FAIL: Could not count commits!")
        return

    commits_behind = int(result.stdout.strip())
    print(f"\n{'='*60}")
    print(f"RESULT: {commits_behind} commit(s) behind remote")
    print(f"{'='*60}")

    if commits_behind == 0:
        print("✅ Already up to date!")
    else:
        print(f"✅ Update available ({commits_behind} commit(s))")

        # Show what commits are new
        result = run_command(
            ["git", "log", "--oneline", "HEAD..origin/main"],
            "Show new commits"
        )

    # Test 9: Check for uncommitted changes
    result = run_command(["git", "status", "--porcelain"], "Check for uncommitted changes")
    if result and result.stdout.strip():
        print("\n⚠️  WARNING: You have uncommitted changes:")
        print(result.stdout)

    print("\n" + "="*60)
    print("DIAGNOSTIC COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
