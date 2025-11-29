# Apache Superset - Keycloak OAuth Configuration
# Add to superset_config.py

from flask_appbuilder.security.manager import AUTH_OAUTH

# Enable OAuth
AUTH_TYPE = AUTH_OAUTH

# Keycloak OAuth Configuration
OAUTH_PROVIDERS = [
    {
        'name': 'keycloak',
        'icon': 'fa-shield',
        'token_key': 'access_token',
        'remote_app': {
            'client_id': 'superset-analytics',
            'client_secret': 'YOUR_CLIENT_SECRET_HERE',  # Get from Keycloak admin console
            'api_base_url': 'https://sso.insightpulseai.net/realms/insightpulse/protocol/openid-connect',
            'client_kwargs': {
                'scope': 'openid profile email'
            },
            'access_token_url': 'https://sso.insightpulseai.net/realms/insightpulse/protocol/openid-connect/token',
            'authorize_url': 'https://sso.insightpulseai.net/realms/insightpulse/protocol/openid-connect/auth',
            'request_token_url': None,
        }
    }
]

# Map Keycloak roles to Superset roles
AUTH_ROLE_ADMIN = 'Admin'
AUTH_ROLE_PUBLIC = 'Public'

AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = 'Gamma'

# Role mapping from Keycloak
def CUSTOM_SECURITY_MANAGER(sm):
    """Map Keycloak roles to Superset roles"""
    from superset.security import SupersetSecurityManager

    class KeycloakSecurityManager(SupersetSecurityManager):
        def oauth_user_info(self, provider, response=None):
            me = self.get_oauth_user_info(provider, response)

            # Map Keycloak roles
            if 'admin' in me.get('resource_access', {}).get('superset-analytics', {}).get('roles', []):
                me['role_keys'] = ['Admin']
            elif 'finance_director' in me.get('realm_access', {}).get('roles', []):
                me['role_keys'] = ['Alpha']
            else:
                me['role_keys'] = ['Gamma']

            return me

    return KeycloakSecurityManager
