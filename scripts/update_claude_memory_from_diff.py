#!/usr/bin/env python3
"""
Update claude_memory.db from git commit diff
Called by post-commit hook to keep memory database in sync
"""
import sys
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime

# Get repo root
repo_root = Path(__file__).parent.parent
db_file = repo_root / "claude_memory.db"


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Update claude_memory.db from git diff")
    parser.add_argument("--sha", required=True, help="Git commit SHA")
    parser.add_argument("--author", required=True, help="Commit author")
    parser.add_argument("--date", required=True, help="Commit date (ISO format)")
    parser.add_argument("--title", required=True, help="Commit title/message")
    return parser.parse_args()


def generate_summary(title, diff):
    """
    Generate a machine-readable summary from commit title and diff
    In a full implementation, this would call Claude Code once to generate a smart summary
    For now, we'll use a simple heuristic
    """
    # Extract changed file types
    lines = diff.split('\n')
    changed_files = []

    for line in lines:
        if line.startswith('+++') or line.startswith('---'):
            # Extract file path
            parts = line.split(' ')
            if len(parts) >= 2:
                path = parts[1]
                if path != '/dev/null' and not path.startswith('a/') and not path.startswith('b/'):
                    continue
                # Remove a/ or b/ prefix
                if path.startswith('a/') or path.startswith('b/'):
                    path = path[2:]
                    if path and path not in changed_files:
                        changed_files.append(path)

    # Determine impact based on title keywords and changed files
    impact = []

    title_lower = title.lower()

    if any(kw in title_lower for kw in ['feat', 'feature', 'add']):
        impact.append('new_feature')
    if any(kw in title_lower for kw in ['fix', 'bug', 'resolve']):
        impact.append('bug_fix')
    if any(kw in title_lower for kw in ['refactor', 'cleanup', 'improve']):
        impact.append('refactoring')
    if any(kw in title_lower for kw in ['test', 'spec']):
        impact.append('testing')
    if any(kw in title_lower for kw in ['docs', 'doc', 'documentation']):
        impact.append('documentation')

    # Check for module/domain impacts
    if any('ipai_' in f for f in changed_files):
        impact.append('ipai_module')
    if any('odoo' in f.lower() for f in changed_files):
        impact.append('odoo')
    if any('schema' in f.lower() or 'sql' in f.lower() for f in changed_files):
        impact.append('database_schema')
    if any('mcp' in f.lower() for f in changed_files):
        impact.append('mcp_server')
    if any('n8n' in f.lower() or 'workflow' in f.lower() for f in changed_files):
        impact.append('automation')

    summary = f"{len(changed_files)} file(s) changed"
    if changed_files:
        # Show first 3 files
        summary += f": {', '.join(changed_files[:3])}"
        if len(changed_files) > 3:
            summary += f" +{len(changed_files) - 3} more"

    return summary, ','.join(impact) if impact else 'general'


def update_file_notes(cursor, diff, commit_sha):
    """Update file_notes table based on changed files in diff"""
    lines = diff.split('\n')
    changed_files = set()

    for line in lines:
        if line.startswith('+++') or line.startswith('---'):
            parts = line.split(' ')
            if len(parts) >= 2:
                path = parts[1]
                # Remove a/ or b/ prefix
                if path.startswith('a/') or path.startswith('b/'):
                    path = path[2:]
                    if path and path != '/dev/null':
                        changed_files.add(path)

    # Update last_commit for all changed files
    for file_path in changed_files:
        # Check if file note exists
        cursor.execute("SELECT path FROM file_notes WHERE path = ?", (file_path,))
        if cursor.fetchone():
            # Update existing note
            cursor.execute("""
                UPDATE file_notes
                SET last_commit = ?,
                    updated_at = datetime('now')
                WHERE path = ?
            """, (commit_sha, file_path))
        else:
            # Create new note for files without existing notes
            # (but only for key directories)
            if any(file_path.startswith(prefix) for prefix in ['addons/', 'mcp/', 'agents/', 'scripts/', 'docs/']):
                cursor.execute("""
                    INSERT INTO file_notes (path, summary, last_commit)
                    VALUES (?, ?, ?)
                """, (file_path, f"Modified in commit {commit_sha[:8]}", commit_sha))


def main():
    """Main function"""
    args = parse_args()

    # Read diff from stdin
    diff = sys.stdin.read()

    # Generate summary and impact
    summary, impact = generate_summary(args.title, diff)

    # Connect to database
    if not db_file.exists():
        print(f"⚠️  Database not found: {db_file}")
        print("   Skipping memory update (database will be created on first use)")
        return 0

    try:
        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()

        # Insert/update commit record
        cursor.execute("""
            INSERT OR REPLACE INTO commits (sha, author, date, title, summary, impact)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (args.sha, args.author, args.date, args.title, summary, impact))

        # Update file notes
        update_file_notes(cursor, diff, args.sha)

        # Commit changes
        conn.commit()

        print(f"✅ Memory updated: {args.sha[:8]} - {args.title}")
        print(f"   Summary: {summary}")
        print(f"   Impact: {impact}")

        conn.close()
        return 0

    except Exception as e:
        print(f"❌ Error updating memory: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
