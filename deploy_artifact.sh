#!/bin/bash
# -----------------------------------------------------------------------------
# Deploy Odoo CE Production Artifact
# Usage: ./deploy_artifact.sh <artifact.tar.gz> [host]
# -----------------------------------------------------------------------------
set -e

ARTIFACT="${1:-odoo_ce_prod_*.tar.gz}"
HOST="${2:-159.223.75.148}"
REMOTE_USER="root"
REMOTE_PATH="/opt/odoo-artifacts"
IMAGE_NAME="odoo-ce-prod"

# Resolve glob pattern to actual file
ARTIFACT=$(ls -t ${ARTIFACT} 2>/dev/null | head -1)

if [ -z "$ARTIFACT" ] || [ ! -f "$ARTIFACT" ]; then
    echo "Error: Artifact not found. Build first with ./build_artifact.sh"
    exit 1
fi

echo "=== Odoo CE Production Deploy ==="
echo "Artifact: ${ARTIFACT}"
echo "Target: ${REMOTE_USER}@${HOST}"
echo ""

# 1. Verify checksum
echo "[1/5] Verifying checksum..."
if [ -f "${ARTIFACT}.sha256" ]; then
    sha256sum -c "${ARTIFACT}.sha256"
else
    echo "Warning: No checksum file found, skipping verification"
fi

# 2. Transfer artifact
echo "[2/5] Transferring artifact to ${HOST}..."
ssh ${REMOTE_USER}@${HOST} "mkdir -p ${REMOTE_PATH}"
scp ${ARTIFACT} ${REMOTE_USER}@${HOST}:${REMOTE_PATH}/

# 3. Load Docker image on remote
echo "[3/5] Loading Docker image on remote..."
ssh ${REMOTE_USER}@${HOST} "gunzip -c ${REMOTE_PATH}/$(basename ${ARTIFACT}) | docker load"

# 4. Restart Odoo service
echo "[4/5] Restarting Odoo service..."
ssh ${REMOTE_USER}@${HOST} "cd /opt/odoo && docker compose down odoo && docker compose up -d odoo"

# 5. Verify deployment
echo "[5/5] Verifying deployment..."
sleep 5
ssh ${REMOTE_USER}@${HOST} "docker ps | grep odoo"

echo ""
echo "=== Deploy Complete ==="
echo "Odoo should be available at: http://${HOST}:8069"
echo ""
echo "To check logs: ssh ${REMOTE_USER}@${HOST} 'docker logs -f odoo'"
