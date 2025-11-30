#!/usr/bin/env bash
set -e

echo "=== InsightPulse Odoo OCA Entrypoint ==="
echo "Odoo Version: 18.0"
echo "Edition: Finance SSC with OCA Modules"

# Wait for PostgreSQL
echo "Waiting for PostgreSQL at ${ODOO_DB_HOST}:${ODOO_DB_PORT}..."
until pg_isready -h "$ODOO_DB_HOST" -p "$ODOO_DB_PORT" -U "$ODOO_DB_USER" >/dev/null 2>&1; do
  sleep 2
done
echo "PostgreSQL is up!"

# Generate odoo.conf with actual values
echo "Generating odoo.conf with environment variables..."
cat > /etc/odoo/odoo.conf << CONF
[options]
; Database configuration
db_host = ${ODOO_DB_HOST}
db_port = ${ODOO_DB_PORT}
db_user = ${ODOO_DB_USER}
db_password = ${ODOO_DB_PASSWORD}
db_name = ${ODOO_DB_NAME}
db_sslmode = require
db_maxconn = 8

; Odoo configuration
admin_passwd = ${ODOO_ADMIN_PASSWORD}
dbfilter = .*
addons_path = /mnt/extra-addons/insightpulse,/mnt/extra-addons/custom,/mnt/extra-addons/oca,/usr/lib/python3/dist-packages/odoo/addons

; Performance
workers = 0
max_cron_threads = 1
limit_memory_hard = 419430400
limit_memory_soft = 335544320
limit_time_cpu = 300
limit_time_real = 600

; Logging
log_level = info
logfile = False
log_db = False

; Other
without_demo = True
data_dir = /var/lib/odoo
CONF

echo "=== Starting Odoo ==="
echo "Command: odoo -c /etc/odoo/odoo.conf"

# Start Odoo
exec python3 odoo-bin -c /etc/odoo/odoo.conf
