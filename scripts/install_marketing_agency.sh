#!/bin/bash
# =============================================================================
# ODOO 18 CE + OCA - MARKETING AGENCY MODULE INSTALLER
# =============================================================================
# This script installs all modules required for Marketing Agency parity
# with Odoo Enterprise.
#
# Usage:
#   ./scripts/install_marketing_agency.sh [DATABASE_NAME]
#
# Example:
#   ./scripts/install_marketing_agency.sh odoo
# =============================================================================

set -e

# Configuration
DB_NAME="${1:-odoo}"
CONTAINER="${ODOO_CONTAINER:-odoo-ce}"

echo "=============================================="
echo "  ODOO 18 CE - MARKETING AGENCY INSTALLER"
echo "=============================================="
echo "Database: $DB_NAME"
echo "Container: $CONTAINER"
echo ""

# -----------------------------------------------------------------------------
# Phase 1: Core Modules (Native Odoo CE)
# -----------------------------------------------------------------------------
echo "[1/5] Installing Core Modules..."
docker exec -it $CONTAINER odoo -d $DB_NAME -i \
    base,mail,contacts,utm \
    --stop-after-init

# -----------------------------------------------------------------------------
# Phase 2: CRM & Sales (Native)
# -----------------------------------------------------------------------------
echo "[2/5] Installing CRM & Sales..."
docker exec -it $CONTAINER odoo -d $DB_NAME -i \
    crm,sale_management,sale_crm \
    --stop-after-init

# -----------------------------------------------------------------------------
# Phase 3: Project & Timesheets (Native + OCA)
# -----------------------------------------------------------------------------
echo "[3/5] Installing Project & Timesheets..."
docker exec -it $CONTAINER odoo -d $DB_NAME -i \
    project,hr_timesheet,sale_timesheet \
    --stop-after-init

# -----------------------------------------------------------------------------
# Phase 4: Marketing & Events (Native)
# -----------------------------------------------------------------------------
echo "[4/5] Installing Marketing & Events..."
docker exec -it $CONTAINER odoo -d $DB_NAME -i \
    mass_mailing,event,event_sale,website,website_blog \
    --stop-after-init

# -----------------------------------------------------------------------------
# Phase 5: Finance & Custom (Native + Custom Delta)
# -----------------------------------------------------------------------------
echo "[5/5] Installing Finance & Custom Modules..."
docker exec -it $CONTAINER odoo -d $DB_NAME -i \
    account,hr_expense,ipai_ce_cleaner,ipai_portal_fix \
    --stop-after-init

# -----------------------------------------------------------------------------
# Optional: PH Tax Compliance (Only if needed)
# -----------------------------------------------------------------------------
if [ "$INSTALL_PH_TAX" = "true" ]; then
    echo "[Optional] Installing PH Tax Compliance..."
    docker exec -it $CONTAINER odoo -d $DB_NAME -i \
        ipai_bir_compliance \
        --stop-after-init
fi

echo ""
echo "=============================================="
echo "  INSTALLATION COMPLETE"
echo "=============================================="
echo ""
echo "Installed Module Categories:"
echo "  - Core: base, mail, contacts, utm"
echo "  - CRM: crm, sale_management, sale_crm"
echo "  - Project: project, hr_timesheet, sale_timesheet"
echo "  - Marketing: mass_mailing, event, event_sale"
echo "  - Website: website, website_blog"
echo "  - Finance: account, hr_expense"
echo "  - Custom: ipai_ce_cleaner, ipai_portal_fix"
echo ""
echo "OCA Modules Available (install manually if needed):"
echo "  - contract (Retainers/Subscriptions)"
echo "  - web_timeline (Gantt View)"
echo "  - bi_sql_editor (Custom Dashboards)"
echo ""
echo "Access Odoo at: http://localhost:8069"
echo "=============================================="
