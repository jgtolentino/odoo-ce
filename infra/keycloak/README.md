# Keycloak SSO - Unified Authentication for InsightPulse AI

## Overview

Single Sign-On (SSO) implementation using Keycloak for all InsightPulse AI subdomains.

**SSO Entry Point**: `https://sso.insightpulseai.net`

## Architecture

```
┌─────────────────────────────────────┐
│   Keycloak Identity Provider        │
│   https://sso.insightpulseai.net   │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       │   OAuth 2.0   │
       │   OpenID      │
       └───────┬───────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌───▼───┐  ┌──▼────┐  ┌────▼────┐
│ Odoo  │  │Super- │  │  n8n  │  │Matter-  │
│  ERP  │  │ set   │  │Workflow│  │ most    │
└───────┘  └───────┘  └────────┘  └─────────┘
erp.       superset.  ipa.        mattermost.
```

## Integrated Applications

| Application | URL | Client ID | Status |
|-------------|-----|-----------|--------|
| **Keycloak Admin** | https://sso.insightpulseai.net/admin | - | Admin Console |
| **Odoo ERP** | https://erp.insightpulseai.net | odoo-erp | ✅ Configured |
| **Apache Superset** | https://superset.insightpulseai.net | superset-analytics | ✅ Configured |
| **n8n Workflows** | https://ipa.insightpulseai.net | n8n-automation | ✅ Configured |
| **Mattermost** | https://mattermost.insightpulseai.net | mattermost-chat | ✅ Configured |

## Unified Login Experience

### User Flow

1. **Access any subdomain** → Redirects to Keycloak login
2. **Login once** at `https://sso.insightpulseai.net`
3. **Access granted** to all integrated applications
4. **No re-authentication** required across subdomains

### Login Page Branding

**URL**: `https://sso.insightpulseai.net/realms/insightpulse/account`

**Customization** (Keycloak Admin Console):
- Realm Settings > Themes > Login Theme
- Custom logo: `https://insightpulseai.net/logo.png`
- Custom CSS: InsightPulse AI brand colors

## Deployment

### Prerequisites

- DigitalOcean account with App Platform access
- `doctl` CLI installed and authenticated
- DNS configured for `sso.insightpulseai.net`

### Step 1: Deploy Keycloak

```bash
cd infra/keycloak
./scripts/deploy-keycloak.sh
```

### Step 2: Configure Realm

1. Access Keycloak Admin Console:
   - URL: `https://sso.insightpulseai.net/admin`
   - Username: `admin`
   - Password: `[from deployment]`

2. Import Realm:
   - Realm → Create Realm → Import
   - Select: `config/insightpulse-realm.json`
   - Click: Import

3. Generate Client Secrets:
   - Navigate to each client (odoo-erp, superset-analytics, etc.)
   - Credentials tab → Regenerate Secret
   - Copy secret for configuration

### Step 3: Configure Applications

#### Odoo ERP

```bash
# Install module
cd /Users/tbwa/jgtolentino-odoo-ce
python3 << 'EOF'
import xmlrpc.client
url = "http://localhost:8069"
db = "odoo18"
username = "admin"
password = "admin"

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
models.execute_kw(db, uid, password, 'ir.module.module', 'update_list', [])

module_ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search',
    [[['name', 'in', ['auth_oauth', 'ipai_keycloak_sso']]]])

models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_install', [module_ids])
EOF

# Update client secret
# Settings > OAuth Providers > Keycloak SSO
# Set client_secret from Keycloak admin console
```

#### Apache Superset

```python
# Add to superset_config.py
from infra.keycloak.config.superset_config import *

# Update client_secret in OAUTH_PROVIDERS
```

#### n8n Workflows

```bash
# Source environment variables
source infra/keycloak/config/n8n_env.sh

# Update N8N_SSO_OIDC_CLIENT_SECRET with value from Keycloak
# Restart n8n service
```

#### Mattermost

1. System Console > Authentication > OpenID Connect
2. Enable: Yes
3. Copy settings from `config/mattermost_config.json`
4. Update Secret with value from Keycloak
5. Save and restart Mattermost

## User Management

### Roles

| Keycloak Role | Description | App Permissions |
|---------------|-------------|-----------------|
| **admin** | System Administrator | Full access to all apps |
| **finance_director** | Finance Director | Finance SSC oversight, all finance features |
| **finance_manager** | Finance Manager | Finance operations, expense approval |
| **finance_supervisor** | Finance Supervisor | Task execution, expense submission |
| **user** | Standard User | Basic access, self-service |

### Adding Users

**Via Keycloak Admin Console**:
1. Users → Add User
2. Fill: Username, Email, First Name, Last Name
3. Role Mappings → Assign realm roles
4. Credentials → Set password (temporary or permanent)
5. Save

**Via Realm Import**:
- Edit `config/insightpulse-realm.json`
- Add to `users` array
- Re-import realm

## Security Features

### Enabled by Default

- ✅ **Brute Force Protection** - Account lockout after failed attempts
- ✅ **SSL/TLS Required** - HTTPS-only authentication
- ✅ **Password Reset** - Self-service password recovery
- ✅ **Email Verification** - Verify user email addresses
- ✅ **Event Logging** - Audit trail for all auth events
- ✅ **Session Management** - Automatic timeout and re-authentication

### Recommended Enhancements

- 🔒 **Multi-Factor Authentication (MFA)** - OTP via authenticator app
- 🔒 **WebAuthn** - Hardware key support (YubiKey, etc.)
- 🔒 **Social Login** - Google, Microsoft, GitHub integration

## Monitoring

### Health Checks

```bash
# Keycloak health
curl https://sso.insightpulseai.net/health/ready

# Metrics
curl https://sso.insightpulseai.net/metrics
```

### Event Logs

Keycloak Admin Console → Events:
- Login Events: Successful/failed logins
- Admin Events: Configuration changes

## Troubleshooting

### Common Issues

**1. Redirect URI Mismatch**
```
Error: redirect_uri_mismatch
Solution: Add exact redirect URI in Keycloak client configuration
```

**2. Invalid Client Secret**
```
Error: invalid_client
Solution: Regenerate client secret and update application config
```

**3. User Not Found**
```
Error: User not registered
Solution: Enable "Just-in-Time Provisioning" or create user manually
```

### Debug Mode

Enable debug logging in Keycloak:
```bash
# Environment variable
KC_LOG_LEVEL=DEBUG
```

## Configuration Files

```
infra/keycloak/
├── keycloak-app-spec.yaml      # DigitalOcean deployment spec
├── Dockerfile                   # Keycloak container build
├── config/
│   ├── insightpulse-realm.json # Realm configuration
│   ├── superset_config.py      # Superset OAuth settings
│   ├── n8n_env.sh              # n8n environment variables
│   └── mattermost_config.json  # Mattermost OIDC settings
└── scripts/
    └── deploy-keycloak.sh      # Deployment automation

addons/ipai_keycloak_sso/       # Odoo integration module
```

## License

AGPL-3

## Support

- Keycloak Documentation: https://www.keycloak.org/documentation
- InsightPulse AI: https://insightpulseai.net
