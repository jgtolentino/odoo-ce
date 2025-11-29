#!/bin/bash
set -e

echo "🚀 Deploying Keycloak SSO to DigitalOcean App Platform"

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "❌ doctl not found. Install with: brew install doctl"
    exit 1
fi

# Check if authenticated
if ! doctl auth list &> /dev/null; then
    echo "❌ Not authenticated with DigitalOcean. Run: doctl auth init"
    exit 1
fi

# Set admin password if not set
if [ -z "$KEYCLOAK_ADMIN_PASSWORD" ]; then
    echo "⚠️  KEYCLOAK_ADMIN_PASSWORD not set"
    read -sp "Enter Keycloak admin password: " KEYCLOAK_ADMIN_PASSWORD
    echo
    export KEYCLOAK_ADMIN_PASSWORD
fi

# Deploy Keycloak app
echo "📦 Creating Keycloak app..."
cd "$(dirname "$0")/.."

doctl apps create --spec keycloak-app-spec.yaml

echo "✅ Keycloak deployment initiated"
echo ""
echo "📋 Next steps:"
echo "1. Wait for deployment to complete (5-10 minutes)"
echo "2. Check status: doctl apps list | grep keycloak"
echo "3. Access Keycloak admin: https://sso.insightpulseai.net/admin"
echo "4. Login with: admin / \$KEYCLOAK_ADMIN_PASSWORD"
echo "5. Import realm: config/insightpulse-realm.json"
echo "6. Generate client secrets for each OAuth client"
echo "7. Update client_secret in configuration files"
