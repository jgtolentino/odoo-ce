# -----------------------------------------------------------------------------
# TARGET: InsightPulse ERP - Odoo 18 CE + OCA Production Image
# Build: docker build -t ghcr.io/jgtolentino/odoo-ce:18-oca-target .
# Save:  docker save -o odoo_ce_prod.tar ghcr.io/jgtolentino/odoo-ce:18-oca-target
# -----------------------------------------------------------------------------
# Smart Delta Philosophy: Config -> OCA -> Delta -> Custom
#
# Canonical 5-Module Architecture:
# 1. ipai_dev_studio_base    - Foundation (aggregates deps, disables IAP)
# 2. ipai_workspace_core     - Notion-style workspace foundation
# 3. ipai_ce_branding        - CE/OCA branding, hide Enterprise upsells
# 4. ipai_finance_ppm        - Accounting industry pack (BIR compliance)
# 5. ipai_industry_marketing_agency - Marketing agency industry pack
# -----------------------------------------------------------------------------
FROM odoo:18.0

USER root

# 1. Install System Dependencies for OCA Modules
# (Some OCA reporting tools need xmlsec1, pandas, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
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
    && rm -rf /var/lib/apt/lists/*

# 2. Prepare Directories
RUN mkdir -p /mnt/extra-addons \
    && mkdir -p /mnt/oca-addons

# 3. Copy OCA Submodules (The "Muscle" - 14 Repositories)
# Assumes `git submodule update --init --recursive` was run locally
COPY ./external-src/reporting-engine /mnt/oca-addons/reporting-engine
COPY ./external-src/account-closing /mnt/oca-addons/account-closing
COPY ./external-src/account-financial-reporting /mnt/oca-addons/account-financial-reporting
COPY ./external-src/account-financial-tools /mnt/oca-addons/account-financial-tools
COPY ./external-src/account-invoicing /mnt/oca-addons/account-invoicing
COPY ./external-src/project /mnt/oca-addons/project
COPY ./external-src/hr-expense /mnt/oca-addons/hr-expense
COPY ./external-src/purchase-workflow /mnt/oca-addons/purchase-workflow
COPY ./external-src/maintenance /mnt/oca-addons/maintenance
COPY ./external-src/dms /mnt/oca-addons/dms
COPY ./external-src/calendar /mnt/oca-addons/calendar
COPY ./external-src/web /mnt/oca-addons/web
COPY ./external-src/contract /mnt/oca-addons/contract
COPY ./external-src/server-tools /mnt/oca-addons/server-tools

# 4. Copy Custom Delta Modules (Canonical 5 + Legacy)
# Canonical 5:
#   - ipai_dev_studio_base (Foundation)
#   - ipai_workspace_core (Notion parity)
#   - ipai_ce_branding (CE compliance)
#   - ipai_finance_ppm (Accounting industry)
#   - ipai_industry_marketing_agency (Marketing industry)
# Legacy (to be consolidated):
#   - ipai_bir_compliance, ipai_docs, tbwa_spectra_integration, etc.
COPY ./addons /mnt/extra-addons

# 5. Copy Configuration
COPY ./deploy/odoo.conf /etc/odoo/odoo.conf

# 6. Install Python Dependencies from OCA modules
RUN find /mnt/oca-addons -name "requirements.txt" -exec pip3 install --no-cache-dir -r {} \; 2>/dev/null || true

# 7. Fix Permissions
RUN chown -R odoo:odoo /mnt/extra-addons /mnt/oca-addons /etc/odoo/odoo.conf

USER odoo

# 8. Define the Addons Path via Environment Variable
# This tells Odoo where to look for modules inside the container
ENV ODOO_ADDONS_PATH=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons,/mnt/oca-addons/reporting-engine,/mnt/oca-addons/account-closing,/mnt/oca-addons/account-financial-reporting,/mnt/oca-addons/account-financial-tools,/mnt/oca-addons/account-invoicing,/mnt/oca-addons/project,/mnt/oca-addons/hr-expense,/mnt/oca-addons/purchase-workflow,/mnt/oca-addons/maintenance,/mnt/oca-addons/dms,/mnt/oca-addons/calendar,/mnt/oca-addons/web,/mnt/oca-addons/contract,/mnt/oca-addons/server-tools

# The image is now production-ready with:
# - Odoo 18 CE base
# - 14 OCA repositories (project, web, account-*, etc.)
# - Canonical 5 custom modules (Smart Delta Architecture)
#
# First-run initialization command:
# docker compose run --rm odoo odoo -d ipai_prod -i ipai_dev_studio_base,ipai_ce_branding,ipai_workspace_core,ipai_finance_ppm
