# -----------------------------------------------------------------------------
# InsightPulse ERP - Odoo 18 CE + OCA Production Image
#
# Name: ghcr.io/jgtolentino/odoo-ce:18-oca-target
#
# Build: docker build -t ghcr.io/jgtolentino/odoo-ce:18-oca-target .
# Save:  docker save -o odoo_ce_prod.tar ghcr.io/jgtolentino/odoo-ce:18-oca-target
#
# Smart Delta Philosophy: Config -> OCA -> Delta -> Custom
#
# Canonical 5-Module Architecture (ipai_addons):
#   1. ipai_dev_studio_base          - Foundation (OCA-first toolbox, disables IAP)
#   2. ipai_workspace_core           - Notion-style workspace foundation
#   3. ipai_ce_branding              - CE/OCA branding, hide Enterprise upsells
#   4. ipai_finance_ppm              - Accounting industry pack (BIR compliance)
#   5. ipai_industry_marketing_agency - Marketing agency industry pack
# -----------------------------------------------------------------------------

FROM odoo:18.0

ENV ODOO_RC=/etc/odoo/odoo.conf

USER root

# 1. Install System Dependencies for OCA Modules
RUN apt-get update && apt-get install -y --no-install-recommends \
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

# 2. Prepare Directories (Canonical paths)
RUN mkdir -p /odoo/oca_addons /odoo/ipai_addons

# -----------------------------------------------------------------------------
# 3. OCA layer (vendored OCA repos, pinned to compatible 18.0 branches)
# -----------------------------------------------------------------------------
COPY oca_addons/ /odoo/oca_addons/

# -----------------------------------------------------------------------------
# 4. Custom InsightPulse layer (exactly 5 ipai_* modules)
# -----------------------------------------------------------------------------
COPY ipai_addons/ /odoo/ipai_addons/

# -----------------------------------------------------------------------------
# 5. Config layer
# -----------------------------------------------------------------------------
COPY config/odoo.conf /etc/odoo/odoo.conf

# 6. Install Python Dependencies from OCA modules
RUN find /odoo/oca_addons -name "requirements.txt" -exec pip3 install --no-cache-dir -r {} \; 2>/dev/null || true

# 7. Ensure Odoo user owns all relevant paths
RUN chown -R odoo:odoo /odoo /etc/odoo

USER odoo

# 8. Define the Addons Path via Environment Variable
ENV ODOO_ADDONS_PATH=/usr/lib/python3/dist-packages/odoo/addons,/odoo/oca_addons,/odoo/ipai_addons

# -----------------------------------------------------------------------------
# The image is now production-ready with:
# - Odoo 18 CE base
# - 14 OCA repositories (project, web, account-*, etc.)
# - Canonical 5 custom modules (Smart Delta Architecture)
#
# First-run initialization command:
# docker compose run --rm odoo odoo -d ipai_prod \
#   -i ipai_dev_studio_base,ipai_ce_branding,ipai_workspace_core,ipai_finance_ppm \
#   --without-demo=all --load-language=en_US
# -----------------------------------------------------------------------------

CMD ["odoo", "-c", "/etc/odoo/odoo.conf"]
