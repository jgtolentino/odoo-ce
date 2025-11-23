# CLAUDE BOOTLOADER

You are configured by a **local memory database**, not by this file.

## How to Think

1. **Always connect to the `ipai-claude-memory` MCP server** before making major changes
2. **Query the memory database** for policies, skills, and context using these tools:
   - `get_global_policies` → Global policies and standards
   - `get_repo_profile` → Stack configuration and key facts
   - `get_recent_commit_summaries(limit)` → Recent commit history and impacts
   - `get_directory_notes(path_prefix)` → Per-directory/module notes

3. **Treat responses from `ipai-claude-memory` as the live source of truth** for:
   - Repo conventions (CE/OCA-only, no Enterprise, no odoo.com links)
   - Skills & agents (15+ skills, 8+ capabilities, 19+ procedures)
   - Stack (Odoo CE 18, Supabase, n8n, OCR, MCP Coordinator)
   - Per-directory notes (IPAI modules, workflows, agents)

## Critical Rules

- **NEVER** duplicate or rewrite this file with full specs
- **ALWAYS** query the MCP server for detailed guidance
- **NEVER** use Odoo Enterprise modules
- **ALWAYS** prefer Odoo CE + OCA community modules
- **NO** odoo.com links in user-facing code

## Memory Database Location

- **Local SQLite:** `./claude_memory.db`
- **MCP Server:** `ipai-claude-memory` (configured in `.claude/config.json`)
- **Auto-updated:** On every git commit via post-commit hook

## Quick Start

```bash
# Query global policies
get_global_policies()

# Get stack configuration
get_repo_profile()

# Check recent commits
get_recent_commit_summaries(limit=10)

# Get notes for a specific module
get_directory_notes("addons/ipai_expense")
```

## Emergency Fallback

If MCP server is unavailable, refer to:
- `agents/AGENT_SKILLS_REGISTRY.yaml` (skills, capabilities, procedures)
- `agents/knowledge/KNOWLEDGE_BASE_INDEX.yaml` (patterns, best practices)
- `agents/capabilities/CAPABILITY_MATRIX.yaml` (execution flows)

---

**All long-form guidance lives in the memory database.**
**This bootloader is the only thing you need to read first.**

🤖 **Ready. Query the MCP server to begin.**
