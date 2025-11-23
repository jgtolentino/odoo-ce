#!/usr/bin/env python3
"""
ipai-claude-memory MCP Server
Exposes claude_memory.db SQLite database to Claude Code via MCP protocol
"""
import os
import sys
import json
import sqlite3
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# MCP imports (using stdio protocol)
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Get database path from environment or default
DB_PATH = os.getenv("CLAUDE_MEMORY_DB", "./claude_memory.db")

# Initialize server
app = Server("ipai-claude-memory")


def get_db_connection():
    """Get SQLite database connection"""
    db_file = Path(DB_PATH)
    if not db_file.exists():
        raise FileNotFoundError(f"Database not found: {db_file}")

    return sqlite3.connect(str(db_file))


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available MCP tools"""
    return [
        types.Tool(
            name="get_global_policies",
            description="Get global policies and standards for the repository",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get_repo_profile",
            description="Get repository profile including stack configuration and key facts",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get_recent_commit_summaries",
            description="Get recent commit summaries with impact analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Number of commits to retrieve (default: 10)",
                        "default": 10
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="get_directory_notes",
            description="Get notes for a specific directory or file path",
            inputSchema={
                "type": "object",
                "properties": {
                    "path_prefix": {
                        "type": "string",
                        "description": "Directory or file path prefix (e.g., 'addons/ipai_expense')"
                    }
                },
                "required": ["path_prefix"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if name == "get_global_policies":
            cursor.execute("""
                SELECT markdown FROM sections
                WHERE key = 'global_policies'
            """)
            result = cursor.fetchone()

            if result:
                return [types.TextContent(
                    type="text",
                    text=result[0]
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text="No global policies found in database"
                )]

        elif name == "get_repo_profile":
            # Get stack configuration
            cursor.execute("""
                SELECT markdown FROM sections
                WHERE key = 'odoo_ce_18_stack'
            """)
            stack_result = cursor.fetchone()

            # Get all facts
            cursor.execute("""
                SELECT namespace, key, value FROM facts
                ORDER BY namespace, key
            """)
            facts_results = cursor.fetchall()

            # Format response
            profile = ""

            if stack_result:
                profile += stack_result[0] + "\n\n"

            if facts_results:
                profile += "## Key Facts\n\n"
                current_namespace = None
                for namespace, key, value in facts_results:
                    if namespace != current_namespace:
                        profile += f"\n### {namespace.upper()}\n"
                        current_namespace = namespace
                    profile += f"- **{key}:** {value}\n"

            return [types.TextContent(
                type="text",
                text=profile if profile else "No repository profile found"
            )]

        elif name == "get_recent_commit_summaries":
            limit = arguments.get("limit", 10)

            cursor.execute("""
                SELECT sha, author, date, title, summary, impact
                FROM commits
                ORDER BY date DESC
                LIMIT ?
            """, (limit,))
            commit_results = cursor.fetchall()

            if commit_results:
                commits_md = f"# Recent Commits (last {limit})\n\n"
                for sha, author, date, title, summary, impact in commit_results:
                    commits_md += f"## {title}\n\n"
                    commits_md += f"- **SHA:** `{sha[:8]}`\n"
                    commits_md += f"- **Author:** {author}\n"
                    commits_md += f"- **Date:** {date}\n"
                    if summary:
                        commits_md += f"- **Summary:** {summary}\n"
                    if impact:
                        commits_md += f"- **Impact:** {impact}\n"
                    commits_md += "\n---\n\n"

                return [types.TextContent(
                    type="text",
                    text=commits_md
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text="No commits found in database. The database is auto-updated on each commit via post-commit hook."
                )]

        elif name == "get_directory_notes":
            path_prefix = arguments.get("path_prefix", "")

            cursor.execute("""
                SELECT path, summary, tags, last_commit, updated_at
                FROM file_notes
                WHERE path LIKE ?
                ORDER BY path
            """, (f"{path_prefix}%",))
            notes_results = cursor.fetchall()

            if notes_results:
                notes_md = f"# Directory Notes: {path_prefix}\n\n"
                for path, summary, tags, last_commit, updated_at in notes_results:
                    notes_md += f"## {path}\n\n"
                    if summary:
                        notes_md += f"{summary}\n\n"
                    if tags:
                        notes_md += f"**Tags:** {tags}\n\n"
                    if last_commit:
                        notes_md += f"**Last Commit:** {last_commit[:8]}\n\n"
                    if updated_at:
                        notes_md += f"**Updated:** {updated_at}\n\n"
                    notes_md += "---\n\n"

                return [types.TextContent(
                    type="text",
                    text=notes_md
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"No notes found for path: {path_prefix}"
                )]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error executing tool {name}: {str(e)}"
        )]
    finally:
        if 'conn' in locals():
            conn.close()


async def main():
    """Run MCP server using stdio transport"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
