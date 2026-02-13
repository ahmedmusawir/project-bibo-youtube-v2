#!/usr/bin/env python3
"""
Utility to check summary/script word/token counts for a project.
Usage: python src/utils/check_script.py
"""
import os
from pathlib import Path


def get_project_root():
    """Find the project root directory."""
    # Start from this script's directory and go up to find the root
    current = Path(__file__).resolve().parent
    while current != current.parent:
        # Check for markers that indicate project root
        if (current / "main.py").exists() or (current / ".git").exists():
            return current
        current = current.parent
    return Path.cwd()  # Fallback to current directory


def list_projects():
    """List all project folders."""
    root = get_project_root()
    projects_dir = root / "projects"
    if not projects_dir.exists():
        print("❌ projects/ directory not found!")
        return []

    projects = [p.name for p in projects_dir.iterdir() if p.is_dir()]
    return sorted(projects)


def check_script(project_name):
    """Check summary/script stats for a project."""
    root = get_project_root()
    script_path = root / "projects" / project_name / "1_summary.txt"

    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return

    # Read content
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Calculate stats
    words = len(content.split())
    chars = len(content)
    lines = len(content.splitlines())

    # Estimate tokens (rough: 1 token ≈ 0.75 words or 1 token ≈ 4 chars)
    tokens_estimate = int(words / 0.75)

    # Check if complete
    ends_correctly = content.strip().endswith("Thanks for watching")
    completeness = "✅ Complete" if ends_correctly else "⚠️  May be incomplete"

    # Display
    print("\n" + "="*60)
    print(f"SCRIPT/SUMMARY STATS: {project_name}")
    print("="*60)
    print(f"📄 File: {script_path}")
    print(f"📊 Words: {words:,}")
    print(f"📊 Characters: {chars:,}")
    print(f"📊 Lines: {lines:,}")
    print(f"🔢 Estimated Tokens: ~{tokens_estimate:,} (at 0.75 word/token ratio)")
    print(f"✓  Status: {completeness}")
    print("="*60)

    # Target range check
    if 900 <= words <= 950:
        print("✅ Word count is in target range (900-950)")
    elif words < 900:
        print(f"⚠️  Below target (got {words}, target 900-950)")
    else:
        print(f"⚠️  Above target (got {words}, target 900-950)")

    # Show last 200 chars
    print(f"\n📝 Last 200 characters:")
    print("-"*60)
    print(content[-200:])
    print("-"*60)


def main():
    print("\n" + "="*60)
    print("SCRIPT/SUMMARY CHECKER")
    print("="*60)

    projects = list_projects()

    if not projects:
        print("❌ No projects found in projects/ directory")
        return

    print("\nAvailable projects:")
    root = get_project_root()
    for i, project in enumerate(projects, 1):
        # Check if script exists
        script_exists = (root / "projects" / project / "1_summary.txt").exists()
        status = "✅" if script_exists else "❌"
        print(f"  {i}. {project:<30} {status}")

    print("\nEnter project number (or 'q' to quit): ", end="")
    choice = input().strip()

    if choice.lower() == 'q':
        print("👋 Bye!")
        return

    try:
        index = int(choice) - 1
        if 0 <= index < len(projects):
            check_script(projects[index])
        else:
            print("❌ Invalid project number!")
    except ValueError:
        print("❌ Please enter a number!")


if __name__ == "__main__":
    main()