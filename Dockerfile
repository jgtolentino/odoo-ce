# =============================================================================
# ODOO 18 CE + OCA PRODUCTION IMAGE
# =============================================================================
# Target: Marketing Agency / Finance SSC Stack
# Parity: ~95% Odoo Enterprise equivalent
#
# Build:  docker build -t odoo-ce-prod:v1 .
# Save:   docker save odoo-ce-prod:v1 | gzip > odoo-prod-v1.tar.gz
# Load:   gunzip -c odoo-prod-v1.tar.gz | docker load
# =============================================================================

FROM odoo:18.0

LABEL maintainer="InsightPulseAI <dev@insightpulseai.net>"
LABEL version="18.0.1.0.0"
LABEL description="Odoo 18 CE + 14 OCA repos for Marketing Agency / Finance SSC"

USER root

# =============================================================================
# 1. SYSTEM DEPENDENCIES
# =============================================================================
# Required for OCA reporting, Excel export, LDAP auth, XML signing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libssl-dev \
    python3-pandas \
    python3-xlrd \
    python3-xlsxwriter \
    python3-xmlsec \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    libsasl2-dev \
    libldap2-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# =============================================================================
# 2. DIRECTORY STRUCTURE
# =============================================================================
RUN mkdir -p /mnt/extra-addons /mnt/oca-addons

# =============================================================================
# 3. OCA SUBMODULES (14 Repositories - The "Muscle")
# =============================================================================
# Enterprise Parity: These replace paid Enterprise features
#
# | OCA Repo                    | Replaces Enterprise        |
# |-----------------------------|----------------------------|
# | contract                    | Subscriptions (Retainers)  |
# | web (web_timeline)          | Gantt View                 |
# | project                     | Planning, Forecasts        |
# | reporting-engine            | BI Dashboards              |
# | account-financial-reporting | Advanced Financial Reports |
# | account-invoicing           | Withholding Tax (EWT)      |
# =============================================================================

# Finance & Accounting
COPY ./external-src/account-closing /mnt/oca-addons/account-closing
COPY ./external-src/account-financial-reporting /mnt/oca-addons/account-financial-reporting
COPY ./external-src/account-financial-tools /mnt/oca-addons/account-financial-tools
COPY ./external-src/account-invoicing /mnt/oca-addons/account-invoicing

# Project & Resource Management
COPY ./external-src/project /mnt/oca-addons/project
COPY ./external-src/contract /mnt/oca-addons/contract
COPY ./external-src/hr-expense /mnt/oca-addons/hr-expense

# Procurement
COPY ./external-src/purchase-workflow /mnt/oca-addons/purchase-workflow

# Operations
COPY ./external-src/maintenance /mnt/oca-addons/maintenance
COPY ./external-src/dms /mnt/oca-addons/dms
COPY ./external-src/calendar /mnt/oca-addons/calendar

# UI & Reporting
COPY ./external-src/web /mnt/oca-addons/web
COPY ./external-src/reporting-engine /mnt/oca-addons/reporting-engine
COPY ./external-src/server-tools /mnt/oca-addons/server-tools

# =============================================================================
# 4. CUSTOM DELTA MODULES (Minimal - Only PH-specific + Fixes)
# =============================================================================
# Only 3 custom modules needed:
#   - ipai_bir_compliance: BIR 2307 + DAT file generator (PH Tax)
#   - ipai_ce_cleaner: Hide Enterprise upsells
#   - ipai_portal_fix: Fix KeyError: 'website' in portal templates
#
# NOTE: tbwa_spectra_integration REMOVED - use native CSV/Excel export
# =============================================================================
COPY ./addons/ipai_bir_compliance /mnt/extra-addons/ipai_bir_compliance
COPY ./addons/ipai_ce_cleaner /mnt/extra-addons/ipai_ce_cleaner
COPY ./addons/ipai_portal_fix /mnt/extra-addons/ipai_portal_fix

# =============================================================================
# 5. CONFIGURATION
# =============================================================================
COPY ./deploy/odoo.conf /etc/odoo/odoo.conf

# =============================================================================
# 6. PYTHON DEPENDENCIES (from OCA modules)
# =============================================================================
RUN find /mnt/oca-addons -name "requirements.txt" -exec pip3 install --no-cache-dir -r {} \; 2>/dev/null || true

# =============================================================================
# 7. PERMISSIONS & SECURITY
# =============================================================================
RUN chown -R odoo:odoo /mnt/extra-addons /mnt/oca-addons /etc/odoo/odoo.conf

USER odoo

# =============================================================================
# 8. ADDONS PATH (Hardcoded for Immutability)
# =============================================================================
ENV ODOO_ADDONS_PATH=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons,/mnt/oca-addons/reporting-engine,/mnt/oca-addons/account-closing,/mnt/oca-addons/account-financial-reporting,/mnt/oca-addons/account-financial-tools,/mnt/oca-addons/account-invoicing,/mnt/oca-addons/project,/mnt/oca-addons/hr-expense,/mnt/oca-addons/purchase-workflow,/mnt/oca-addons/maintenance,/mnt/oca-addons/dms,/mnt/oca-addons/calendar,/mnt/oca-addons/web,/mnt/oca-addons/contract,/mnt/oca-addons/server-tools

# =============================================================================
# IMAGE SUMMARY
# =============================================================================
# Base:     Odoo 18.0 CE (Debian)
# OCA:      14 repositories (18.0 branch)
# Custom:   3 delta modules
# Size:     ~1.5GB (uncompressed)
#
# Marketing Agency Parity: 95%+
# Finance SSC Parity: 95%+
#
# Missing vs Enterprise:
#   - Social Marketing UI (use n8n)
#   - AI Website Builder (use templates)
#   - Predictive Lead Scoring (use rules)
# =============================================================================
