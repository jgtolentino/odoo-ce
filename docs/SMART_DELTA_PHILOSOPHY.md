# Smart Delta Philosophy

## Overview

Smart Delta is the architectural principle guiding InsightPulse ERP development. It minimizes custom code by leveraging existing layers in a strict priority order.

## The Priority Chain

```
Config -> OCA -> Delta -> Custom
```

### 1. Config (First Resort)

Before writing any code, check if the requirement can be met through configuration:

- System parameters (`ir.config_parameter`)
- Company settings
- Module settings
- User preferences
- Access rights and record rules

**Example:** Instead of custom code to hide a menu, use a record rule or remove the group assignment.

### 2. OCA (Second Resort)

If configuration isn't sufficient, check OCA repositories for existing solutions:

- 14 OCA repositories included in the target image
- Hundreds of production-tested modules
- Active community maintenance

**Example:** Need PDF reports? Use `reporting-engine` instead of building custom report infrastructure.

### 3. Delta (Third Resort)

If OCA doesn't have exactly what you need, extend existing modules:

- Inherit models and add fields
- Extend views with `xpath`
- Override methods with `super()`
- Use mixins from OCA modules

**Example:** Need extra fields on invoices? Inherit `account.move` instead of creating a parallel model.

### 4. Custom (Last Resort)

Only write completely new code when the above layers cannot satisfy the requirement:

- New business domain models
- Industry-specific workflows
- Integration bridges

**Example:** BIR deadline tracking is Philippines-specific and has no OCA equivalent.

## The Canonical 5-Module Architecture

To enforce Smart Delta, all custom code lives in exactly 5 modules:

| Module | Layer | Purpose |
|--------|-------|---------|
| `ipai_dev_studio_base` | Foundation | OCA-first toolbox, disables IAP |
| `ipai_workspace_core` | Core | Notion-style workspace |
| `ipai_ce_branding` | Core | CE compliance, branding |
| `ipai_finance_ppm` | Industry | Accounting/BIR |
| `ipai_industry_marketing_agency` | Industry | Marketing agency |

## Rules for AI Agents

1. **Never suggest Enterprise features** - This is a CE-only stack
2. **Never suggest IAP** - IAP is disabled via `ipai_dev_studio_base`
3. **Search OCA first** - Before writing custom code, check if OCA has a solution
4. **Extend, don't replace** - Use inheritance over duplication
5. **Minimal footprint** - Every line of custom code is technical debt

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | What to Do Instead |
|--------------|--------------|---------------------|
| Reimplementing OCA modules | Duplicates maintenance burden | Install and configure OCA |
| Creating parallel models | Data fragmentation | Inherit and extend |
| Hardcoding business logic | Inflexible | Use system parameters |
| Custom report framework | Wheel reinvention | Use `reporting-engine` |
| Enterprise feature shims | License violation risk | Accept CE limitations |

## Dependency Chain

```
base (Odoo CE)
    └── ipai_dev_studio_base (Foundation)
            ├── ipai_workspace_core (Core)
            ├── ipai_ce_branding (Core)
            ├── ipai_finance_ppm (Industry)
            └── ipai_industry_marketing_agency (Industry)
```

All `ipai_*` modules depend on `ipai_dev_studio_base`, which aggregates:
- Core CE modules (base, mail, web, contacts, project, account, etc.)
- Key OCA modules (when specified in depends)
- IAP disable configuration

## Verification Checklist

Before merging any custom code, verify:

- [ ] Configuration alone cannot solve this
- [ ] No OCA module exists for this use case
- [ ] Extending existing models was considered
- [ ] Code lives in one of the canonical 5 modules
- [ ] No Enterprise/IAP features are referenced
- [ ] `ipai_dev_studio_base` is in the dependency chain
