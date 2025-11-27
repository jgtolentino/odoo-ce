# Finance Workflow RACI Architecture

**Module**: `ipai_finance_workflow`
**Version**: 18.0.1.0.0
**Status**: ✅ Phase 1 Complete (Instance-Based) | ⏳ Phase 2 Planned (Template-Instance)

## Current Implementation (Phase 1: Instance-Based)

### Core Models

**ipai.finance.stage** - Workflow stages for Finance operations
- Separates Month-End vs BIR vs other workstreams
- Stage types: prep, review, approve, file/pay, reconcile, report, close
- Auto-sets task status when moved between stages
- 8 seeded stages (4 Month-End + 4 BIR)

**ipai.finance.task** - RACI-aware Finance tasks (current period instances)
- **RACI**: All roles via `ipai.person` (R, A, C, I)
- **Workstreams**: month_end, tax_filing, reporting, treasury, audit, project
- **Task Types**: recurring, bir_filing, project, one_off
- **WBS Support**: parent_id, wbs_code, hierarchical levels
- **Dates**: period_start/end, planned_start/end, actual_start/end, due_date
- **Status**: draft → in_progress → waiting_review → completed/blocked/cancelled
- **Health**: on_track, at_risk, off_track
- **Dependencies**: predecessors tracking via many2many

**ipai.task.checklist** - Detailed step-by-step items per task
- Sequences each bullet/step in Excel "Detailed Task" column
- **Role**: prep, review, approve (mapped to RACI activity types)
- **Assignment**: person_id (ipai.person), user_id (res.users), employee_code
- **Tracking**: planned_date, done, done_date
- Auto-sets done_date on completion

### Smart Delta Approach

✅ **OCA Checklist NOT Available** (Odoo 18.0) → Built minimal custom checklist
✅ **Reuses ipai.person** for RACI (no duplicate People models)
✅ **Extends project.task** (optional integration point for future OCA compatibility)

### Seed Data

Month-End Stages (category: month_end):
1. **Preparation** (ME_PREP) - default, status: in_progress
2. **Review** (ME_REVIEW) - status: waiting_review
3. **Approval** (ME_APPROVE) - status: waiting_review
4. **Period Close** (ME_CLOSE) - status: completed, folded

BIR Tax Filing Stages (category: tax_filing):
1. **Preparation** (BIR_PREP) - default, status: in_progress
2. **Review** (BIR_REVIEW) - status: waiting_review
3. **Approval** (BIR_APPROVE) - status: waiting_review
4. **File & Pay** (BIR_FILE) - status: completed, folded

### UI/UX

**Kanban View** - Clarity PPM-style board
- Group by stage (drag-and-drop between workflow stages)
- Traffic light health indicators (on_track/at_risk/off_track)
- Progress bars per task
- RACI avatars (Responsible person visible)
- Due date + overdue warnings

**Tree View** - Traditional list with filters
- Group by workstream, stage, health
- Sort by due_date, progress, priority

**Form View** - Detailed task management
- **RACI Tab**: R/A (single), C/I (multi-select tags)
- **Checklist Tab**: Editable tree with sequence handles, done checkboxes, role assignment
- **Details Tab**: Description, evidences (links to BIR portal, Google Drive)
- Chatter: mail.thread integration for discussions

---

## Future Evolution (Phase 2: Template-Instance Pattern)

**Design Decision**: Current implementation is **instance-only** (October 2025 tasks created manually).
**Future Goal**: Normalize to **template → instance** pattern per canonical schema.

### Planned Models (Phase 2)

**closing_task_template** - Reusable month-end task definitions
- Maps to Excel "Detailed Monthly Tasks" bold headers
- Default frequency, RACI defaults, offset days
- One record per recurring task type (e.g., "Payroll Processing & Tax Provision")

**closing_task_step_template** - Reusable checklist step definitions
- Maps to Excel bullet points under each task
- One record per sentence in "Detailed Task" column
- Default role, offset days, sequence

**closing_period** - Time periods with BIR form mapping
- Maps to Excel "Period Covered" + BIR schedule
- One record per month/quarter (e.g., "2025-10", "2025-Q1")
- Links to BIR form codes (1601-C, 2550Q)

**closing_task_instance** (extends ipai.finance.task)
- Current tasks generated FROM templates FOR specific periods
- Allows per-period RACI overrides (e.g., someone on leave)
- Links: period_id, task_template_id, project_task_id

**closing_task_step_instance** (extends ipai.task.checklist)
- Checklist items generated FROM step templates FOR specific task instances
- Allows per-instance modifications while preserving template source

### Migration Path

1. ✅ **Phase 1 (Current)**: Manual task/checklist creation (MVP)
2. ⏳ **Phase 1.5**: Excel import wizard (bulk load Oct 2025 month-end tasks)
3. ⏳ **Phase 2**: Add template models + period model
4. ⏳ **Phase 2.5**: Automated task generation from templates on period open
5. ⏳ **Phase 3**: Template library UI (clone, modify, version templates)

### Compatibility Strategy

**Current code is forward-compatible**:
- `ipai.finance.task` will become base for `closing_task_instance`
- `ipai.task.checklist` will become base for `closing_task_step_instance`
- Add template_id fields without breaking existing instances
- Migration script will populate template_id retroactively (mark as "converted_from_manual")

---

## Integration Points

### With ipai.person (Canonical People Model)
- All RACI roles reference ipai.person (not res.users)
- Supports multi-employee Finance SSC (8 employees: RIM, CKVC, LAS, etc.)
- employee_code stored in checklist for Excel compatibility

### With ipai.workspace_core
- Optional workspace_id on tasks (multi-client/agency support)
- Future: workspace dashboards aggregate Finance task metrics

### With project.task (Optional)
- project_task.finance_checklist_ids field created (future OCA checklist compatibility)
- Can bind Finance tasks to Projects for PPM integration

### With Odoo HR (Future)
- ipai.person ↔ hr.employee via employee_code matching
- Leave management → auto-adjust RACI assignments during absence

---

## Excel Mapping (Current vs Future)

| Excel Column | Phase 1 (Current) | Phase 2 (Template-Instance) |
|--------------|-------------------|------------------------------|
| Task Category | Manual grouping in name | closing_task_template.category_id |
| Detailed Monthly Tasks (bold) | ipai.finance.task.name | closing_task_template.title |
| Bullet list under task | ipai.task.checklist.name (manual) | closing_task_step_template (auto-generated) |
| Reviewed by / Approved by | ipai.finance.task RACI fields | closing_task_template_raci (defaults) |
| Preparation/Review/Approval days | Checklist planned_date (manual calc) | closing_task_step_template.default_offset_days |
| Period Covered | ipai.finance.task.period_start/end | closing_period (normalized) |
| BIR Form | ipai.finance.task.bir_form | closing_period.bir_form_code |

---

## Deployment Checklist

✅ Module created: `/opt/odoo-ce/ipai_addons/ipai_finance_workflow`
✅ Dependencies: base, mail, project, ipai_person, ipai_workspace_core
✅ Security: CSV with user/manager access levels
✅ Seed Data: 8 workflow stages (Month-End + BIR)
✅ Views: Kanban, Tree, Form for stages and tasks
⏳ Installation: Pending Odoo restart + module install
⏳ Testing: Create sample October 2025 month-end task with checklist
⏳ Excel Import Wizard: Bulk load from Monthly Closing Tasks.xlsx
⏳ Documentation: User guide for Finance team (RACI assignment, checklist usage)

---

## Next Steps

**Immediate (Phase 1 Completion)**:
1. Restart Odoo to detect new module
2. Install `ipai_finance_workflow` via Apps menu
3. Verify 8 stages created (Month-End + BIR)
4. Create test task "October 2025 Payroll Processing"
5. Add 3 checklist items (Prep, Review, Approval)
6. Assign RACI roles to Finance team members
7. Test Kanban drag-and-drop between stages

**Short-Term (Phase 1.5 - Excel Import)**:
1. Create wizard: `ipai.finance.import_wizard`
2. Parse Monthly Closing Tasks.xlsx
3. Bulk create tasks + checklists for current period
4. Map Excel columns → Odoo fields
5. Handle RACI assignment from "Reviewed by" cells

**Medium-Term (Phase 2 - Template System)**:
1. Add 5 template models (task_template, step_template, period, template_raci)
2. Migrate existing tasks to template-instance pattern
3. Build period opening workflow (auto-generate Oct tasks from Sep template)
4. Template library UI (clone, modify, version)
5. Historical template changes tracking (audit which template version was used)

**Long-Term (Phase 3 - Full PPM Integration)**:
1. Gantt view with critical path (dependency chains)
2. Resource allocation dashboard (who's overloaded?)
3. BIR auto-filing integration (generate PDFs from templates)
4. Mattermost notifications (deadline alerts, approval requests)
5. Analytics: on-time completion %, average cycle time per task type
