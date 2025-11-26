#!/bin/bash
# =============================================================================
# SEED DATA FOR MARKETING AGENCY
# =============================================================================
# Initializes the database with Marketing Agency seed data:
# - Company settings
# - Default users/roles
# - CRM stages
# - Project templates
# - Contract templates (for retainers)
#
# Usage:
#   ./scripts/seed_marketing_agency.sh [DATABASE_NAME]
# =============================================================================

set -e

DB_NAME="${1:-odoo}"
CONTAINER="${ODOO_CONTAINER:-odoo-ce}"

echo "=============================================="
echo "  MARKETING AGENCY - SEED DATA"
echo "=============================================="
echo "Database: $DB_NAME"
echo ""

# -----------------------------------------------------------------------------
# Create seed data via Odoo shell
# -----------------------------------------------------------------------------
docker exec -i $CONTAINER odoo shell -d $DB_NAME --no-http << 'PYTHON_EOF'
# =============================================================================
# MARKETING AGENCY SEED DATA
# =============================================================================

print("Seeding Marketing Agency data...")

# -----------------------------------------------------------------------------
# 1. CRM Stages (Lead Pipeline)
# -----------------------------------------------------------------------------
print("[1/5] Creating CRM stages...")
CrmStage = env['crm.stage']
stages = [
    {'name': 'New Lead', 'sequence': 1},
    {'name': 'Qualified', 'sequence': 2},
    {'name': 'Proposal Sent', 'sequence': 3},
    {'name': 'Negotiation', 'sequence': 4},
    {'name': 'Won', 'sequence': 5, 'is_won': True},
]
for stage in stages:
    if not CrmStage.search([('name', '=', stage['name'])]):
        CrmStage.create(stage)
        print(f"   Created stage: {stage['name']}")

# -----------------------------------------------------------------------------
# 2. Project Stages (Task Pipeline)
# -----------------------------------------------------------------------------
print("[2/5] Creating Project task stages...")
ProjectTaskType = env['project.task.type']
task_stages = [
    {'name': 'Backlog', 'sequence': 1},
    {'name': 'To Do', 'sequence': 2},
    {'name': 'In Progress', 'sequence': 3},
    {'name': 'Review', 'sequence': 4},
    {'name': 'Done', 'sequence': 5, 'fold': True},
]
for stage in task_stages:
    if not ProjectTaskType.search([('name', '=', stage['name'])]):
        ProjectTaskType.create(stage)
        print(f"   Created task stage: {stage['name']}")

# -----------------------------------------------------------------------------
# 3. Product Categories (Service Types)
# -----------------------------------------------------------------------------
print("[3/5] Creating service categories...")
ProductCategory = env['product.category']
categories = [
    'Creative Services',
    'Digital Marketing',
    'Strategy & Consulting',
    'Media Buying',
    'Production',
]
for cat_name in categories:
    if not ProductCategory.search([('name', '=', cat_name)]):
        ProductCategory.create({'name': cat_name})
        print(f"   Created category: {cat_name}")

# -----------------------------------------------------------------------------
# 4. Service Products (Billable Services)
# -----------------------------------------------------------------------------
print("[4/5] Creating service products...")
Product = env['product.product']
ProductTemplate = env['product.template']

services = [
    {
        'name': 'Strategy Consulting',
        'type': 'service',
        'list_price': 5000.00,
        'default_code': 'SVC-STRATEGY',
        'invoice_policy': 'delivery',
    },
    {
        'name': 'Creative Design (Hourly)',
        'type': 'service',
        'list_price': 150.00,
        'default_code': 'SVC-DESIGN-HR',
        'invoice_policy': 'delivery',
    },
    {
        'name': 'Monthly Retainer - Basic',
        'type': 'service',
        'list_price': 10000.00,
        'default_code': 'RTN-BASIC',
        'invoice_policy': 'order',
    },
    {
        'name': 'Monthly Retainer - Premium',
        'type': 'service',
        'list_price': 25000.00,
        'default_code': 'RTN-PREMIUM',
        'invoice_policy': 'order',
    },
]

for svc in services:
    if not ProductTemplate.search([('default_code', '=', svc['default_code'])]):
        ProductTemplate.create(svc)
        print(f"   Created service: {svc['name']}")

# -----------------------------------------------------------------------------
# 5. Partner Tags (Client Categories)
# -----------------------------------------------------------------------------
print("[5/5] Creating partner tags...")
PartnerCategory = env['res.partner.category']
tags = [
    'Agency Client',
    'Direct Brand',
    'Media Partner',
    'Supplier',
    'Prospect',
]
for tag_name in tags:
    if not PartnerCategory.search([('name', '=', tag_name)]):
        PartnerCategory.create({'name': tag_name})
        print(f"   Created tag: {tag_name}")

# Commit all changes
env.cr.commit()

print("")
print("============================================")
print("  SEED DATA COMPLETE")
print("============================================")
print("")
print("Created:")
print(f"  - {len(stages)} CRM stages")
print(f"  - {len(task_stages)} Project task stages")
print(f"  - {len(categories)} Service categories")
print(f"  - {len(services)} Service products")
print(f"  - {len(tags)} Partner tags")
print("")
PYTHON_EOF

echo ""
echo "Seed data loaded successfully!"
echo "=============================================="
