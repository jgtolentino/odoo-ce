# Custom Odoo CE image for InsightPulse
ARG ODOO_VERSION=18.0
FROM odoo:${ODOO_VERSION}

LABEL org.opencontainers.image.source="https://github.com/jgtolentino/odoo-ce" \
      org.opencontainers.image.description="Custom Odoo CE image for InsightPulseAI" \
      org.opencontainers.image.licenses="AGPL-3.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        git \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy custom addons baked into the image; owner set to odoo for runtime safety
COPY --chown=odoo:odoo ./addons /mnt/extra-addons/

# Install Python dependencies if a requirements file exists
RUN if [ -f /mnt/extra-addons/requirements.txt ]; then \
      pip install --no-cache-dir -r /mnt/extra-addons/requirements.txt; \
    fi

# Provide default configuration inside the image (override with bind mount in compose)
COPY --chown=odoo:odoo ./deploy/odoo.conf /etc/odoo/odoo.conf

# Default environment placeholders (override at runtime via compose/ENV)
ENV HOST=db \
    PORT=5432 \
    USER=odoo \
    PASSWORD=odoo \
    DB=odoo

# Run as non-root for security
USER odoo
