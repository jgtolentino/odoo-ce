#!/bin/bash
# =============================================================================
# BUILD PRODUCTION TAR IMAGE
# =============================================================================
# Creates an air-gapped deployable Docker image for Odoo 18 CE + OCA
#
# Output: odoo-prod-v1.tar.gz (~600MB compressed)
#
# Usage:
#   ./scripts/build_production_image.sh
#   ./scripts/build_production_image.sh v2  # Custom version tag
# =============================================================================

set -e

# Configuration
VERSION="${1:-v1}"
IMAGE_NAME="odoo-ce-prod"
IMAGE_TAG="${IMAGE_NAME}:${VERSION}"
OUTPUT_FILE="odoo-prod-${VERSION}.tar.gz"

echo "=============================================="
echo "  ODOO 18 CE + OCA - PRODUCTION IMAGE BUILD"
echo "=============================================="
echo "Image Tag: $IMAGE_TAG"
echo "Output: $OUTPUT_FILE"
echo ""

# -----------------------------------------------------------------------------
# Pre-flight Checks
# -----------------------------------------------------------------------------
echo "[1/5] Pre-flight checks..."

# Check if external-src has content
if [ ! -d "external-src/web" ]; then
    echo "ERROR: OCA submodules not initialized!"
    echo "Run: git submodule update --init --recursive"
    exit 1
fi

# Check if required addons exist
for addon in ipai_bir_compliance ipai_ce_cleaner ipai_portal_fix; do
    if [ ! -d "addons/$addon" ]; then
        echo "ERROR: Missing addon: addons/$addon"
        exit 1
    fi
done

echo "   All checks passed!"

# -----------------------------------------------------------------------------
# Build Image
# -----------------------------------------------------------------------------
echo ""
echo "[2/5] Building Docker image..."
docker build -t $IMAGE_TAG -f Dockerfile .

# -----------------------------------------------------------------------------
# Verify Image
# -----------------------------------------------------------------------------
echo ""
echo "[3/5] Verifying image..."
docker run --rm $IMAGE_TAG python3 -c "import pandas; print('pandas OK')"
docker run --rm $IMAGE_TAG ls /mnt/oca-addons/ | head -5

# -----------------------------------------------------------------------------
# Export & Compress
# -----------------------------------------------------------------------------
echo ""
echo "[4/5] Exporting and compressing..."
docker save $IMAGE_TAG | gzip > $OUTPUT_FILE

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo ""
echo "[5/5] Build complete!"
echo ""
echo "=============================================="
echo "  BUILD SUMMARY"
echo "=============================================="

FILE_SIZE=$(du -h $OUTPUT_FILE | cut -f1)
IMAGE_SIZE=$(docker images $IMAGE_TAG --format "{{.Size}}")

echo "Image Tag:       $IMAGE_TAG"
echo "Image Size:      $IMAGE_SIZE"
echo "Tar File:        $OUTPUT_FILE"
echo "Tar Size:        $FILE_SIZE"
echo ""
echo "Deploy Commands:"
echo "  # Transfer to server"
echo "  scp $OUTPUT_FILE ubuntu@SERVER:/opt/odoo/"
echo ""
echo "  # Load on server"
echo "  gunzip -c $OUTPUT_FILE | docker load"
echo ""
echo "  # Update docker-compose.prod.yml"
echo "  image: $IMAGE_TAG"
echo "=============================================="
