#!/usr/bin/env python3
"""
Utility to check transcript word/token counts for a project.
Usage: python src/utils/check_transcript.py
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


def check_transcript(project_name):
    """Check transcript stats for a project."""
    root = get_project_root()
    transcript_path = root / "projects" / project_name / "0_transcript.txt"

    if not transcript_path.exists():
        print(f"❌ Transcript not found: {transcript_path}")
        return

    # Read content
    with open(transcript_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Calculate stats
    words = len(content.split())
    chars = len(content)
    lines = len(content.splitlines())

    # Estimate tokens (rough: 1 token ≈ 0.75 words or 1 token ≈ 4 chars)
    tokens_estimate = int(words / 0.75)

    # Display
    print("\n" + "="*60)
    print(f"TRANSCRIPT STATS: {project_name}")
    print("="*60)
    print(f"📄 File: {transcript_path}")
    print(f"📊 Words: {words:,}")
    print(f"📊 Characters: {chars:,}")
    print(f"📊 Lines: {lines:,}")
    print(f"🔢 Estimated Tokens: ~{tokens_estimate:,} (at 0.75 word/token ratio)")
    print("="*60)

    # Show first 200 chars
    print(f"\n📝 First 200 characters:")
    print("-"*60)
    print(content[:200])
    print("-"*60)


def main():
    print("\n" + "="*60)
    print("TRANSCRIPT CHECKER")
    print("="*60)

    projects = list_projects()

    if not projects:
        print("❌ No projects found in projects/ directory")
        return

    print("\nAvailable projects:")
    root = get_project_root()
    for i, project in enumerate(projects, 1):
        # Check if transcript exists
        transcript_exists = (root / "projects" / project / "0_transcript.txt").exists()
        status = "✅" if transcript_exists else "❌"
        print(f"  {i}. {project:<30} {status}")

    print("\nEnter project number (or 'q' to quit): ", end="")
    choice = input().strip()

    if choice.lower() == 'q':
        print("👋 Bye!")
        return

    try:
        index = int(choice) - 1
        if 0 <= index < len(projects):
            check_transcript(projects[index])
        else:
            print("❌ Invalid project number!")
    except ValueError:
        print("❌ Please enter a number!")


if __name__ == "__main__":
    main()