# IPAI Superset Integration

## Purpose

Integrate Apache Superset dashboards directly into Odoo's main menu, allowing users to access analytics dashboards with a single click.

## Features

**Analytics Menu** (Sequence 5 - appears early in main menu):
- 📊 **Superset Home** - Main Superset welcome page
- 💰 **Finance Dashboards** - Financial analytics
- 📈 **PPM Dashboards** - Project Portfolio Management analytics
- 💳 **Expense Analytics** - Expense tracking and analysis

All links open in a **new tab** (`target="new"`) to keep Odoo session active.

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

# Update module list
models.execute_kw(db, uid, password, 'ir.module.module', 'update_list', [])

# Install
module_ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search',
    [[['name', '=', 'ipai_superset_integration']]])

if module_ids:
    models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_install', [module_ids])
    print("✅ ipai_superset_integration installed")
EOF
```

## Configuration

### Change Superset URL

Edit `data/superset_actions.xml` and update the `url` field:

```xml
<record id="action_superset_home" model="ir.actions.act_url">
    <field name="name">Superset Home</field>
    <field name="url">https://your-superset-instance.com/superset/welcome/</field>
    <field name="target">new</field>
</record>
```

### Add More Dashboards

1. **Create new action** in `data/superset_actions.xml`:
```xml
<record id="action_superset_custom" model="ir.actions.act_url">
    <field name="name">Custom Dashboard</field>
    <field name="url">https://superset.insightpulseai.net/superset/dashboard/123/</field>
    <field name="target">new</field>
</record>
```

2. **Create menu item** in `views/superset_menus.xml`:
```xml
<menuitem
    id="menu_superset_custom"
    name="Custom Dashboard"
    parent="menu_superset_root"
    action="action_superset_custom"
    sequence="50"
/>
```

3. **Upgrade module**:
```bash
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
    [[['name', '=', 'ipai_superset_integration']]])

if module_ids:
    models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_upgrade', [module_ids])
    print("✅ Module upgraded")
EOF
```

## Current Configuration

**Superset Instance**: `https://superset.insightpulseai.net`

**Menu Structure**:
- Analytics (Root) - Sequence 5
  - Superset Home - Sequence 10
  - Finance Dashboards - Sequence 20
  - PPM Dashboards - Sequence 30
  - Expense Analytics - Sequence 40

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
- Works with any Apache Superset instance
