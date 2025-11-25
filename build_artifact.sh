#!/bin/bash
# -----------------------------------------------------------------------------
# Build Odoo CE Production Artifact
# Creates: odoo_ce_prod_YYYYMMDD.tar.gz (Docker image tarball)
# -----------------------------------------------------------------------------
set -e

IMAGE_NAME="odoo-ce-prod"
IMAGE_TAG="latest"
DATE_TAG=$(date +%Y%m%d)
ARTIFACT_NAME="odoo_ce_prod_${DATE_TAG}.tar.gz"

echo "=== Odoo CE Production Build ==="
echo "Date: $(date)"
echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""

# 1. Initialize OCA submodules
echo "[1/4] Initializing OCA submodules..."
git submodule update --init --recursive 2>/dev/null || echo "Submodules already initialized"

# 2. Build Docker image
echo "[2/4] Building Docker image..."
docker build -f Dockerfile.prod -t ${IMAGE_NAME}:${IMAGE_TAG} .

# 3. Save image to tarball
echo "[3/4] Saving image to tarball..."
docker save ${IMAGE_NAME}:${IMAGE_TAG} | gzip > ${ARTIFACT_NAME}

# 4. Calculate checksum
echo "[4/4] Calculating checksum..."
sha256sum ${ARTIFACT_NAME} > ${ARTIFACT_NAME}.sha256

echo ""
echo "=== Build Complete ==="
echo "Artifact: ${ARTIFACT_NAME}"
echo "Size: $(du -h ${ARTIFACT_NAME} | cut -f1)"
echo "SHA256: $(cat ${ARTIFACT_NAME}.sha256)"
echo ""
echo "Deploy with: ./deploy_artifact.sh ${ARTIFACT_NAME}"
