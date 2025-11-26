# InsightPulse Finance PPM

**PMBOK-compliant Finance task matrix with WBS, dependencies, and ECharts dashboards**

## Features

### Core Functionality
- **Logical Framework (Logframe)** - 6-level hierarchy (Goal → Outcome → IM1/IM2 → Outputs → Activities)
- **BIR Filing Schedule** - Automated tracking of Philippine tax forms with internal deadlines
- **Task Auto-Creation** - Daily cron creates 3 tasks per BIR form (prep → review → approval)
- **ECharts Dashboard** - Interactive visualizations at `/ipai/finance/ppm`
- **Critical Path Analysis** - PMBOK-compliant dependency management

### Dashboard Visualizations
1. **BIR Deadline Timeline** - Bar chart with color-coded status (green=filed, orange=in_progress, red=late)
2. **Completion Tracking** - Percentage bar chart with dynamic thresholds (≥80% green, 50-79% orange, <50% red)
3. **Status Distribution** - Pie chart of form statuses
4. **Logframe Overview** - Task count by logframe level
5. **KPI Cards** - Total forms, on-time filings, compliance rate, at-risk, late filings

## Installation

### Requirements
- Odoo CE 18.0
- Python 3.11+
- PostgreSQL 15+

### Steps

```bash
# 1. Copy module to addons
cp -r ipai_finance_ppm /path/to/odoo/addons/

# 2. Update module list
odoo-bin -d production -u all --stop-after-init

# 3. Install module
odoo-bin -d production -i ipai_finance_ppm --stop-after-init
```

## Configuration

### 1. Create Finance PPM Project

Navigate to: **Project → Configuration → Projects → Create**

- Name: `Finance PPM`
- This project will hold all auto-generated BIR tasks

### 2. Configure Responsible Persons

Navigate to: **Finance PPM → BIR Schedule → Open any form**

Set default responsible users:
- **Preparation**: Finance Supervisor (e.g., RIM)
- **Review**: Senior Finance Manager (e.g., BOM)
- **Approval**: Finance Director (e.g., JPAL)

### 3. Enable Daily Cron Job

Navigate to: **Settings → Technical → Scheduled Actions**

Find: `Finance PPM: Sync BIR Tasks`
- **Active**: ✅ True
- **Execute Every**: 1 day
- **Next Execution Date**: Today at 8:00 AM

## Usage

### Access Dashboard

Navigate to: **Finance PPM → Dashboard**

Or visit directly: `https://your-odoo-domain.com/ipai/finance/ppm`

### Create BIR Form Manually

Navigate to: **Finance PPM → BIR Schedule → Create**

Fields:
- **BIR Form**: Select form code (1601-C, 2550Q, etc.)
- **Period**: Enter tax period (e.g., "December 2025")
- **BIR Filing Deadline**: Select official deadline

Click **Create Tasks** button to generate 3 tasks immediately.

### View Finance PPM Tasks

Navigate to: **Finance PPM → Finance Tasks**

Filter shows only tasks linked to logframe or BIR schedule (`is_finance_ppm = True`).

### Logframe Management

Navigate to: **Finance PPM → Logframe**

- View/edit hierarchical objectives
- Click **Task Count** button to see linked tasks
- Add custom objectives at any level

## API Endpoints

### Dashboard
- **URL**: `/ipai/finance/ppm`
- **Method**: GET
- **Auth**: User login required
- **Response**: HTML dashboard with ECharts

### BIR Data API
- **URL**: `/ipai/finance/ppm/api/bir`
- **Method**: POST (JSON-RPC)
- **Auth**: User login required
- **Response**: JSON array of BIR schedule data

### Logframe Data API
- **URL**: `/ipai/finance/ppm/api/logframe`
- **Method**: POST (JSON-RPC)
- **Auth**: User login required
- **Response**: JSON array of logframe data

## Seed Data

Module ships with:

### Logframe (12 objectives)
- 1 Goal: "100% compliant and timely month-end closing and tax filing"
- 1 Outcome: "Zero-penalty compliance with timely financial reporting"
- 2 Immediate Objectives:
  - **IM1**: Month-end closing (within 5 days)
  - **IM2**: BIR tax filing (100% on-time)
- 3 Outputs: Reconciliations, Journal Entries, BIR Forms
- 4 Activities: Bank Recon, GL Recon, WHT Computation, VAT Computation

### BIR Schedule (8 forms)
- 3× 1601-C (Dec 2025, Jan 2026, Feb 2026)
- 2× 0619-E (Dec 2025, Jan 2026)
- 1× 2550Q (Q4 2025)
- 1× 1702-RT (Annual 2025)
- 1× 1601-EQ (Q4 2025)

## Integration Points

### Odoo Knowledge
Auto-generate Knowledge articles from BIR analysis:
```python
article = request.env['knowledge.article'].create({
    'name': 'October 2025 Month-End Closing Guide',
    'body': generate_closing_guide(tasks)
})
```

### Odoo Spreadsheet
Export BIR data to spreadsheet with pivot tables:
```python
spreadsheet = request.env['documents.document'].create({
    'name': 'BIR Compliance Report',
    'spreadsheet_data': generate_spreadsheet_json(bir_schedules)
})
```

### n8n Workflows
- **BIR Deadline Alert**: Schedule → Query upcoming deadlines → Mattermost notify
- **Task Escalation**: Schedule → Query overdue tasks → Alert supervisors
- **Monthly Summary**: End of month → Query stats → Generate report

### Tableau LangChain
Natural language queries via CrewAI agents:
```python
from langchain_tableau import TableauToolkit
agent = create_agent(tableau_toolkit)
response = agent.invoke("Show me late BIR filings for Q4 2025")
```

## Troubleshooting

### Dashboard Not Loading
1. Check controller route: `odoo-bin shell -d production`
   ```python
   env['ir.http']._match('/ipai/finance/ppm')
   ```
2. Verify ECharts CDN accessible: `curl -I https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js`

### Tasks Not Auto-Creating
1. Check cron job active: **Settings → Technical → Scheduled Actions**
2. Manual run: `odoo-bin shell -d production`
   ```python
   env['ipai.finance.bir_schedule']._cron_sync_bir_tasks()
   ```
3. Check logs: `grep "BIR" /var/log/odoo/odoo.log`

### Missing Logframe Objectives
1. Check seed data loaded: `psql production -c "SELECT COUNT(*) FROM ipai_finance_logframe;"`
2. Expected: 12 records
3. If missing, reinstall module: `odoo-bin -d production -i ipai_finance_ppm --stop-after-init`

## Technical Details

### Models
- **ipai.finance.logframe** - Logical framework tracking
- **ipai.finance.bir_schedule** - BIR filing schedule
- **project.task** (extended) - Finance PPM task fields

### Views
- Tree, Form views for logframe and BIR schedule
- Extended project task form with Finance PPM tab
- ECharts dashboard QWeb template

### Controllers
- `/ipai/finance/ppm` - Dashboard endpoint
- `/ipai/finance/ppm/api/bir` - BIR data JSON API
- `/ipai/finance/ppm/api/logframe` - Logframe data JSON API

### Scheduled Actions
- **_cron_sync_bir_tasks()** - Daily at 8:00 AM, creates tasks for upcoming BIR forms

## License

AGPL-3 (Affero General Public License)

## Author

InsightPulse AI
https://insightpulseai.net

## Support

For issues or questions:
- GitHub: https://github.com/jgtolentino/odoo-ce/issues
- Email: support@insightpulseai.net
