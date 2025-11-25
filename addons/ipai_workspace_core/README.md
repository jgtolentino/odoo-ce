# IPAI Workspace Core

Notion-style workspaces for Odoo CE 18.0 — the foundation of the IPAI Productivity Suite.

## Features

### Core Functionality
- **Workspaces**: Collaborative containers with privacy controls (private/shared/public)
- **Pages**: Hierarchical documents with unlimited nesting depth
- **Blocks**: Modular content units (text, headings, todos, callouts, code, embeds)
- **Templates**: Reusable page structures for quick creation
- **Backlinks**: Automatic bi-directional page references via `[[Page Name]]` syntax

### Security Model
- Three-tier access groups: User, Manager, Administrator
- Workspace-level privacy: Private, Shared, Public
- Record rules enforce access based on membership
- Owner-only deletion controls

### API Endpoints
REST API for external integrations and custom frontends:
- `GET /workspace/api/page/<id>` - Fetch page with blocks
- `POST /workspace/api/page/<id>/save` - Save page content
- `POST /workspace/api/block/create` - Create new block
- `POST /workspace/api/block/<id>` - Update block
- `GET /workspace/api/workspace/<id>/pages` - Get page tree
- `GET /workspace/api/search` - Full-text search

## Installation

```bash
# From Odoo addons directory
cd /opt/odoo/custom-addons

# Clone or copy module
cp -r ipai_workspace_core .

# Update Odoo module list
./odoo-bin -d your_db -u base --stop-after-init

# Install the module
./odoo-bin -d your_db -i ipai_workspace_core --stop-after-init
```

Or via the Apps menu in Odoo:
1. Update Apps List
2. Search for "IPAI Workspace"
3. Click Install

## Configuration

### Security Groups
After installation, assign users to workspace groups:
- **Workspace User**: Can view/edit workspaces they're members of
- **Workspace Manager**: Can create workspaces and manage templates
- **Workspace Administrator**: Full access to all workspaces

### Templates
Global templates are included by default:
- Meeting Notes
- Project Brief
- Weekly Planning
- Documentation Page
- Blank Page

Create workspace-specific templates via Configuration → Page Templates.

## Usage

### Creating a Workspace
1. Go to Workspace → Workspaces
2. Click Create
3. Set name, icon, and privacy level
4. Add members (for shared workspaces)

### Creating Pages
1. Open a workspace
2. Click "Create Page" or use the + button
3. Start typing content
4. Use `[[Page Name]]` to create links to other pages

### Using Templates
1. Create a new page
2. In the form, select "Created From Template"
3. Choose a template to pre-populate content

### Block Types (Slash Commands)
When using the advanced editor (Sprint 3):
- `/text` - Paragraph
- `/h1`, `/h2`, `/h3` - Headings
- `/todo` - Checkbox item
- `/bullet` - Bulleted list
- `/number` - Numbered list
- `/quote` - Block quote
- `/callout` - Highlighted callout box
- `/code` - Code block
- `/divider` - Horizontal rule

## Dependencies

- `base` - Odoo base module
- `mail` - Messaging and activity tracking
- `web` - Web assets

## Roadmap

This module is part of a multi-sprint development:

| Sprint | Focus | Status |
|--------|-------|--------|
| 1 | Core models, basic views, record rules | ✅ Complete |
| 2 | Database views, templates, backlinks | 🔄 Next |
| 3 | TipTap block editor, slash menu | Planned |
| 4 | Automations, n8n integration | Planned |
| 5 | AI/RAG layer, search improvements | Planned |

## Related Modules

- `ipai_workspace_db` - Database views and linked records (Sprint 2)
- `ipai_workspace_automations` - Workflow automation (Sprint 4)
- `ipai_workspace_integrations` - GitHub, Mattermost, BI embeds (Sprint 4)
- `ipai_workspace_ai` - RAG search and summarization (Sprint 5)

## License

AGPL-3.0 - See LICENSE file for details.

## Author

**InsightPulseAI**
Website: https://insightpulseai.net

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Submit a pull request

## Support

For issues and feature requests, please use the GitHub issue tracker.
