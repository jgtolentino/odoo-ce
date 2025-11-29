# IPAI Web Home - Clean App Grid at /odoo

## Purpose

Override the default `/odoo` route to show a clean app grid menu instead of the discuss app redirect.

## What It Does

**Before (Default Odoo Behavior)**:
- `/odoo` → redirects to `/odoo/action-mail.action_discuss` (Discuss app)
- Users land in the messaging app instead of seeing available apps

**After (IPAI Web Home)**:
- `/odoo` → shows the standard Odoo app menu (clean grid of installed apps)
- Users see all available applications to choose from

## Installation

```bash
# Via XML-RPC Python script
python3 << 'EOF'
import xmlrpc.client
url = "http://localhost:8069"
db = "odoo18"
username = "admin"
password = "admin"

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
module_ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search',
    [[['name', '=', 'ipai_web_home']]])

if module_ids:
    models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_install', [module_ids])
    print("✅ ipai_web_home installed")
EOF
```

## Technical Details

### Controller Override

`controllers/main.py` overrides the `/odoo` route:

```python
@http.route(['/odoo', '/odoo/'], type='http', auth="user", website=False)
def odoo_home(self, **kw):
    """Show the app menu (home screen) instead of discuss."""
    return self.web_client(s_action=None, **kw)
```

### JavaScript Client Override

`static/src/js/web_client.js` ensures the client loads the app menu:

```javascript
loadRouterState(state) {
    if (window.location.pathname === '/odoo' || window.location.pathname === '/odoo/') {
        if (!state || !state.action) {
            return super.loadRouterState({
                action: null,
                actionStack: [],
                menu_id: null
            });
        }
    }
    return super.loadRouterState(...arguments);
}
```

## Configuration

No configuration needed. The module works automatically after installation.

## Dependencies

- `web` (Odoo CE 18.0 web module)

## License

AGPL-3

## Author

InsightPulse AI
https://insightpulseai.net

## Compatibility

- Odoo CE 18.0
- OCA compliant
