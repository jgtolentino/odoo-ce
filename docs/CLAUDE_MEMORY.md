# Claude Memory System

**Status:** ✅ Active
**Version:** 1.0.0
**Last Updated:** 2025-11-23

---

## Overview

The Claude Memory System replaces the traditional giant `CLAUDE.md` file with a **structured SQLite database** that stays automatically in sync with git commits. Instead of maintaining a massive documentation file, Claude Code now queries a local MCP server backed by `claude_memory.db`.

### Architecture

```
┌──────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  CLAUDE.md   │─────▶│ MCP Server      │─────▶│ claude_memory   │
│ (bootloader) │      │ ipai-claude-    │      │ .db (SQLite)    │
│   (~80 lines)│      │ memory          │      │                 │
└──────────────┘      └─────────────────┘      │ - sections      │
                                                 │ - facts         │
                      ┌─────────────────┐      │ - file_notes    │
                      │ Git Hook        │─────▶│ - commits       │
                      │ (post-commit)   │      └─────────────────┘
                      └─────────────────┘
```

---

## Components

### 1. **claude_memory.db (SQLite Database)**

**Location:** `./claude_memory.db`

**Tables:**

#### `sections`
Stores large markdown sections like policies, skills, capabilities.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| key | TEXT | Unique section key (e.g., 'global_policies') |
| title | TEXT | Section title |
| markdown | TEXT | Full markdown content |
| updated_at | TEXT | Last update timestamp |

**Current sections:**
- `global_policies` - Global policies and standards
- `odoo_ce_18_stack` - Stack configuration
- `agent_skills` - 15+ atomic skills
- `agent_capabilities` - 8+ composite capabilities
- `execution_procedures` - 19+ execution playbooks
- `capability_matrix` - Execution flows and validation
- `knowledge_base_index` - Documentation, patterns, best practices

#### `facts`
Key/value pairs for quick lookups.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| namespace | TEXT | Fact namespace (odoo, supabase, n8n, etc.) |
| key | TEXT | Fact key |
| value | TEXT | Fact value |
| updated_at | TEXT | Last update timestamp |

#### `file_notes`
Per-directory/file memory.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| path | TEXT | File/directory path |
| summary | TEXT | 1-2 paragraph description |
| tags | TEXT | Comma-separated tags |
| last_commit | TEXT | Last commit SHA that touched this path |
| updated_at | TEXT | Last update timestamp |

#### `commits`
Commit-level summaries.

| Column | Type | Description |
|--------|------|-------------|
| sha | TEXT | Git commit SHA (primary key) |
| author | TEXT | Commit author |
| date | TEXT | Commit date (ISO format) |
| title | TEXT | Commit message title |
| summary | TEXT | Machine-readable summary |
| impact | TEXT | Impact classification (comma-separated) |
| created_at | TEXT | Record creation timestamp |

---

### 2. **MCP Server (ipai-claude-memory)**

**Location:** `mcp/claude_memory_server.py`

**Transport:** stdio (standard input/output)

**Tools Exposed:**

#### `get_global_policies()`
Returns global policies and standards.

**Input:** None
**Output:** Markdown with policies

#### `get_repo_profile()`
Returns stack configuration + key facts.

**Input:** None
**Output:** Markdown with stack details and facts grouped by namespace

#### `get_recent_commit_summaries(limit=10)`
Returns recent commit summaries.

**Input:**
- `limit` (number, optional): Number of commits to retrieve

**Output:** Markdown list of commits with summaries and impacts

#### `get_directory_notes(path_prefix)`
Returns notes for a specific directory/file.

**Input:**
- `path_prefix` (string): Directory path (e.g., "addons/ipai_expense")

**Output:** Markdown with file notes, tags, and last commit

---

### 3. **Git Post-Commit Hook**

**Location:** `.git/hooks/post-commit`

**Triggers:** Automatically after every `git commit`

**Actions:**
1. Captures commit SHA, author, date, title, and diff
2. Calls `scripts/update_claude_memory_from_diff.py`
3. Updates `commits` table with new commit
4. Updates `file_notes` table for all changed files

---

### 4. **CLAUDE.md Bootloader**

**Location:** `./CLAUDE.md`

**Size:** ~80 lines (down from 800+)

**Purpose:**
- Minimal file that tells Claude Code to query the MCP server
- No duplication of policies or skills
- All long-form guidance lives in the database

---

## Usage

### For Claude Code

When Claude Code starts, it reads `CLAUDE.md` which instructs it to:

1. Connect to the `ipai-claude-memory` MCP server
2. Query for policies before making changes:
   ```
   get_global_policies()
   get_repo_profile()
   ```
3. Query for recent context:
   ```
   get_recent_commit_summaries(limit=10)
   ```
4. Query for module-specific notes:
   ```
   get_directory_notes("addons/ipai_expense")
   ```

### For Developers

#### Query the database directly

```bash
sqlite3 claude_memory.db

# List all sections
SELECT key, title FROM sections;

# Get global policies
SELECT markdown FROM sections WHERE key = 'global_policies';

# Get all facts
SELECT namespace, key, value FROM facts ORDER BY namespace;

# Get recent commits
SELECT sha, title, summary FROM commits ORDER BY date DESC LIMIT 10;

# Get notes for a directory
SELECT * FROM file_notes WHERE path LIKE 'addons/ipai_%';
```

#### Manually update the database

```bash
# Re-migrate from YAML files
python3 scripts/migrate_yaml_to_sqlite.py

# Manually trigger memory update for a commit
python3 scripts/update_claude_memory_from_diff.py \
  --sha $(git rev-parse HEAD) \
  --author "$(git log -1 --pretty=%an)" \
  --date "$(git log -1 --pretty=%cI)" \
  --title "$(git log -1 --pretty=%s)" \
  <<< "$(git show --stat --patch --pretty=format:)"
```

---

## Configuration

### Enable MCP Server

The MCP server is configured in `.mcp.json`:

```json
{
  "mcpServers": {
    "ipai-claude-memory": {
      "command": "python3",
      "args": ["mcp/claude_memory_server.py"],
      "env": {
        "CLAUDE_MEMORY_DB": "./claude_memory.db"
      }
    }
  }
}
```

And enabled in `.claude/settings.local.json`:

```json
{
  "enableAllProjectMcpServers": true
}
```

### Install MCP Dependencies

```bash
pip install -r mcp/requirements.txt
```

---

## Maintenance

### Adding New Sections

To add a new section to the database:

```python
import sqlite3

conn = sqlite3.connect('claude_memory.db')
cursor = conn.cursor()

cursor.execute("""
    INSERT OR REPLACE INTO sections (key, title, markdown)
    VALUES (?, ?, ?)
""", ('my_new_section', 'My New Section Title', '# Content here...'))

conn.commit()
conn.close()
```

### Adding New Facts

```python
cursor.execute("""
    INSERT OR REPLACE INTO facts (namespace, key, value)
    VALUES (?, ?, ?)
""", ('my_namespace', 'my_key', 'my_value'))
```

### Backup and Restore

```bash
# Backup
sqlite3 claude_memory.db ".backup claude_memory_backup.db"

# Restore
sqlite3 claude_memory.db ".restore claude_memory_backup.db"

# Export to SQL
sqlite3 claude_memory.db .dump > claude_memory_dump.sql

# Import from SQL
sqlite3 claude_memory_new.db < claude_memory_dump.sql
```

---

## Migration from Old System

### Before (Giant CLAUDE.md)

- ❌ Single 800+ line markdown file
- ❌ Manual updates required
- ❌ No auto-sync with commits
- ❌ Difficult to query specific sections
- ❌ Copy-paste between sessions

### After (SQLite Memory)

- ✅ Tiny 80-line bootloader
- ✅ Queryable SQLite database
- ✅ Auto-updates on every commit
- ✅ Structured sections, facts, file notes
- ✅ MCP server for programmatic access

---

## Troubleshooting

### MCP Server Not Starting

**Check:**
1. MCP dependencies installed: `pip install -r mcp/requirements.txt`
2. Database exists: `ls -lh claude_memory.db`
3. MCP server permissions: `chmod +x mcp/claude_memory_server.py`

**Test manually:**
```bash
CLAUDE_MEMORY_DB=./claude_memory.db python3 mcp/claude_memory_server.py
```

### Database Not Updating After Commits

**Check:**
1. Post-commit hook is executable: `ls -lh .git/hooks/post-commit`
2. Update script is executable: `ls -lh scripts/update_claude_memory_from_diff.py`
3. Check git hook logs: `git commit` (should show memory update message)

**Fix permissions:**
```bash
chmod +x .git/hooks/post-commit
chmod +x scripts/update_claude_memory_from_diff.py
```

### Database Corrupted

**Rebuild from scratch:**
```bash
# Remove old database
rm claude_memory.db

# Re-initialize
python3 scripts/init_claude_memory_db.py

# Re-migrate from YAML
python3 scripts/migrate_yaml_to_sqlite.py
```

---

## Future Enhancements

Potential improvements:

1. **RAG Integration:** Embed sections for semantic search
2. **Supabase Sync:** Replicate to Supabase for team access
3. **Web Interface:** Browse memory database via web UI
4. **Smart Summaries:** Use Claude to generate better commit summaries
5. **Dependency Tracking:** Track module dependencies in database
6. **Performance Metrics:** Store build times, test results

---

## See Also

- [AGENT_SKILLS_REGISTRY.yaml](../agents/AGENT_SKILLS_REGISTRY.yaml) - Source YAML for skills
- [KNOWLEDGE_BASE_INDEX.yaml](../agents/knowledge/KNOWLEDGE_BASE_INDEX.yaml) - Source YAML for knowledge
- [CAPABILITY_MATRIX.yaml](../agents/capabilities/CAPABILITY_MATRIX.yaml) - Source YAML for capabilities
- [MCP Protocol](https://modelcontextprotocol.io/) - Model Context Protocol docs

---

**Status:** Production-ready ✅
**Maintained By:** InsightPulseAI Platform Team
