#!/bin/bash
# n8n - Keycloak OAuth Configuration
# Add these environment variables to your n8n deployment

# OAuth Settings
export N8N_AUTH_JWT_JWKS_URI="https://sso.insightpulseai.net/realms/insightpulse/protocol/openid-connect/certs"
export N8N_AUTH_JWT_ISSUER="https://sso.insightpulseai.net/realms/insightpulse"
export N8N_AUTH_JWT_AUDIENCE="n8n-automation"

# Keycloak OAuth Provider
export N8N_SSO_OIDC_ENABLED=true
export N8N_SSO_OIDC_PROVIDER="keycloak"
export N8N_SSO_OIDC_CLIENT_ID="n8n-automation"
export N8N_SSO_OIDC_CLIENT_SECRET="YOUR_CLIENT_SECRET_HERE"  # Get from Keycloak admin console
export N8N_SSO_OIDC_ISSUER="https://sso.insightpulseai.net/realms/insightpulse"
export N8N_SSO_OIDC_AUTHORIZATION_URL="https://sso.insightpulseai.net/realms/insightpulse/protocol/openid-connect/auth"
export N8N_SSO_OIDC_TOKEN_URL="https://sso.insightpulseai.net/realms/insightpulse/protocol/openid-connect/token"
export N8N_SSO_OIDC_USERINFO_URL="https://sso.insightpulseai.net/realms/insightpulse/protocol/openid-connect/userinfo"
export N8N_SSO_OIDC_SCOPE="openid profile email"

# Auto-create users from Keycloak
export N8N_SSO_JUST_IN_TIME_PROVISIONING=true

# Redirect URI (must match Keycloak client configuration)
export N8N_SSO_REDIRECT_URL="https://ipa.insightpulseai.net/rest/oauth2-credential/callback"

# Role mapping
export N8N_SSO_OIDC_ROLE_MAPPING_ENABLED=true
