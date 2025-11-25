# InsightPulse Odoo CE – Finance PPM Platform

[![Odoo 18 CE/OCA CI](https://github.com/jgtolentino/odoo-ce/actions/workflows/ci-odoo-oca.yml/badge.svg)](https://github.com/jgtolentino/odoo-ce/actions/workflows/ci-odoo-oca.yml)

**Self-hosted Odoo 18 Community Edition with OCA-first delta modules for Finance Project Portfolio Management.**

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    TARGET IMAGE (Immutable)                     │
│              ghcr.io/jgtolentino/odoo-ce:latest                 │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: IPAI Delta     │  /mnt/extra-addons (ipai_*, tbwa_*)  │
│  Layer 2: OCA Modules    │  /mnt/oca-addons                     │
│  Layer 1: Odoo Core      │  /usr/lib/.../odoo/addons            │
└─────────────────────────────────────────────────────────────────┘
```

### Key Principles

| Principle | Description |
|-----------|-------------|
| **OCA First** | Use community-vetted OCA modules before writing custom code |
| **Smart Delta** | Custom modules extend (never replace) Core/OCA functionality |
| **Immutable Image** | Production deploys pre-built image; no runtime code changes |
| **CE Only** | No Odoo Enterprise or IAP dependencies |

## Addon Locations

| Type | Development Path | Docker Path | Prefix |
|------|------------------|-------------|--------|
| **Odoo Core** | (in base image) | `/usr/lib/.../odoo/addons` | `base`, `sale`, `project` |
| **OCA Modules** | `./oca/` | `/mnt/oca-addons` | Git submodules |
| **IPAI Custom** | `./addons/` | `/mnt/extra-addons` | `ipai_*`, `tbwa_*` |

## Repository Structure

```
odoo-ce/
├── addons/                       # IPAI Custom Delta Modules
│   ├── ipai_finance_ppm/         # Finance PPM (Clarity/Notion parity)
│   ├── ipai_ppm_monthly_close/   # Monthly close scheduler
│   ├── ipai_docs/                # Document management
│   ├── tbwa_spectra_integration/ # TBWA Spectra export
│   └── ipai_ce_cleaner/          # Enterprise/IAP removal
│
├── oca/                          # OCA Modules (Git Submodules)
│   └── .gitkeep
│
├── deploy/                       # Deployment Configuration
│   ├── docker-compose.yml        # Development stack
│   ├── docker-compose.prod.yml   # Production stack (immutable image)
│   ├── odoo.conf                 # Odoo server configuration
│   └── nginx/                    # Reverse proxy configs
│
├── scripts/                      # Automation Scripts
│   ├── ci/                       # CI/CD helpers
│   └── deploy-odoo-modules.sh
│
├── docs/                         # Documentation
│   ├── IMAGE_GUIDE.md            # Target image documentation
│   └── DEPLOYMENT.md
│
├── .github/workflows/            # CI/CD Pipelines
│   ├── ci-odoo-oca.yml           # OCA compliance + tests
│   └── health-check.yml
│
├── Dockerfile                    # Target image build
├── constitution.md               # AI Spec Kit rulebook
├── .env.example                  # Environment template
├── .pre-commit-config.yaml       # OCA quality gates
└── requirements.txt              # Development dependencies
```

## Quick Start

### Production Deployment

```bash
# 1. Clone repository
git clone https://github.com/jgtolentino/odoo-ce.git
cd odoo-ce/deploy

# 2. Configure environment
cp ../.env.example .env
# Edit .env: Set DB_PASSWORD and ADMIN_PASSWD

# 3. Login to registry
echo $GHCR_TOKEN | docker login ghcr.io -u jgtolentino --password-stdin

# 4. Deploy
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### Development Setup

```bash
# 1. Clone with submodules
git clone --recurse-submodules https://github.com/jgtolentino/odoo-ce.git
cd odoo-ce

# 2. Install pre-commit hooks
pip install -r requirements.txt
pre-commit install

# 3. Start development stack
cd deploy
docker compose up -d

# 4. Access Odoo
open http://localhost:8069
```

## Custom Modules

### `ipai_finance_ppm` (Core)
Finance Project Portfolio Management with Clarity/Notion parity:
- Logical framework (Goal → Outcome → Output → Activity)
- BIR tax compliance scheduling
- Multi-level approval workflow (Prep → Review → Approval)
- ECharts dashboard visualization

### `ipai_ppm_monthly_close`
Automated monthly close scheduler:
- Task templates with SLA durations
- Business day calculations
- n8n integration for notifications
- Kanban workflow states

### `tbwa_spectra_integration`
TBWA Spectra finance system integration:
- Cash advance workflows
- Expense export (CSV)
- GL code mappings
- Approval matrix by amount

### `ipai_docs`
Internal knowledge base (Notion parity):
- Hierarchical document pages
- Document states (Draft → Published)
- Project/task linking

### `ipai_ce_cleaner`
Enterprise/IAP removal:
- Hides upgrade banners
- Removes IAP menus
- Rewires to OCA/InsightPulse links

## Module Commands

```bash
# Update module (production)
docker compose -f docker-compose.prod.yml exec odoo \
  odoo -d odoo -u ipai_finance_ppm --stop-after-init

# Install new module
docker compose -f docker-compose.prod.yml exec odoo \
  odoo -d odoo -i new_module --stop-after-init

# Odoo shell
docker compose -f docker-compose.prod.yml exec odoo \
  odoo shell -d odoo
```

## CI/CD Pipeline

The GitHub Actions workflow enforces:

| Check | Description |
|-------|-------------|
| **OCA Compliance** | Pre-commit hooks (black, isort, flake8, XML lint) |
| **Enterprise Check** | Fails on `*_enterprise` imports |
| **URL Check** | Warns on `odoo.com` links |
| **Unit Tests** | Runs `--test-enable` on all modules |
| **Coverage** | Reports test coverage percentage |

## Documentation

| Document | Description |
|----------|-------------|
| [`constitution.md`](constitution.md) | AI Spec Kit rulebook |
| [`docs/IMAGE_GUIDE.md`](docs/IMAGE_GUIDE.md) | Target image documentation |
| [`deploy/README.md`](deploy/README.md) | Deployment quick reference |
| [`.env.example`](.env.example) | Environment variables template |

## Configuration

### odoo.conf addons_path

```ini
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons,/mnt/oca-addons
#              ↑ ODOO CORE                              ↑ IPAI CUSTOM    ↑ OCA
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DB_PASSWORD` | Yes | PostgreSQL password |
| `ADMIN_PASSWD` | Yes | Odoo master password |
| `APP_IMAGE` | No | Default: `ghcr.io/jgtolentino/odoo-ce` |
| `APP_IMAGE_VERSION` | No | Default: `latest` |

See [`.env.example`](.env.example) for complete list.

## Adding OCA Modules

```bash
# Add as Git submodule (version-locked to 18.0)
git submodule add -b 18.0 https://github.com/OCA/project.git oca/project

# Update all submodules
git submodule update --init --recursive

# Rebuild image to include OCA modules
docker build -t ghcr.io/jgtolentino/odoo-ce:latest .
```

## License

- **IPAI modules** (`ipai_*`, `tbwa_*`): AGPL-3
- **OCA modules**: See respective licenses in `oca/`

## Support

- **Issues**: [GitHub Issues](https://github.com/jgtolentino/odoo-ce/issues)
- **Documentation**: `docs/` directory
- **Production URL**: `https://erp.insightpulseai.net`

---

**Target Image**: `ghcr.io/jgtolentino/odoo-ce:latest`
**Odoo Version**: 18.0 Community Edition
**Status**: Active Development | Finance PPM Phase
