# InsightPulse ERP – Custom Odoo CE Image Specification

**Status:** Approved v1.0
**Owner:** InsightPulseAI – Infrastructure Team
**Repo:** `jgtolentino/odoo-ce`
**Last Updated:** 2025-11-24

---

## 1. Purpose & Context

This specification defines the architecture and requirements for the custom Odoo CE Docker image that serves as the core deployment artifact for InsightPulse ERP. The custom image implements the "Smart Customization" pattern where all custom modules and dependencies are baked into the image for immutable, consistent deployments.

## 2. Goals & Non-Goals

### 2.1 Goals

1. **Immutable Deployment Artifact**
   - Custom modules (`ipai_*`) baked into the image
   - System dependencies pre-installed
   - Consistent CI/production environment

2. **Security-First Design**
   - Non-root user execution (`USER odoo`)
   - Minimal attack surface
   - Secure base image (official `odoo:18.0`)

3. **Automated CI/CD Pipeline**
   - GitHub Actions automated build and push
   - Automated testing and validation
   - Zero-downtime deployment

4. **Multi-Environment Support**
   - Docker Compose (VPS)
   - Kubernetes (DOKS)
   - Consistent behavior across environments

### 2.2 Non-Goals

- Support for Odoo Enterprise features
- IAP or odoo.com integrations
- Manual deployment processes
- Environment-specific customizations

## 3. Architecture Overview

### 3.1 Image Structure

```
Custom Odoo CE Image
├── Base: odoo:18.0 (official)
├── System Dependencies
│   ├── build-essential
│   ├── git
│   └── libssl-dev
├── Custom Modules
│   ├── /mnt/extra-addons (ipai_* modules)
│   └── /mnt/oca-addons (OCA modules)
├── Configuration
│   └── /etc/odoo/odoo.conf
└── Security
    └── USER odoo (non-root)
```

### 3.2 Deployment Paths

1. **GitHub Actions CI/CD**
   - Build: `Dockerfile` → `ghcr.io/jgtolentino/odoo-ce:latest`
   - Push: GitHub Container Registry
   - Deploy: VPS (Docker Compose) or DOKS (Kubernetes)

2. **Docker Compose (VPS)**
   - Image: `ghcr.io/jgtolentino/odoo-ce:latest`
   - Configuration: `docker-compose.prod.yml`
   - Secrets: `.env.production`

3. **Kubernetes (DOKS)**
   - Image: `ghcr.io/jgtolentino/odoo-ce:latest`
   - Configuration: `deploy/k8s/` manifests
   - Secrets: Kubernetes Secrets

## 4. Technical Specifications

### 4.1 Dockerfile Requirements

```dockerfile
# Base image (official Odoo CE)
FROM odoo:18.0

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    libssl-dev

# Copy custom modules
COPY ./addons /mnt/extra-addons

# Copy configuration
COPY ./deploy/odoo.conf /etc/odoo/odoo.conf

# Security: non-root user
USER odoo
```

### 4.2 Image Naming Convention

- **Registry**: GitHub Container Registry (GHCR)
- **Repository**: `ghcr.io/jgtolentino/odoo-ce`
- **Tag**: `latest` (production), `sha-{commit}` (CI builds)
- **Canonical Reference**: `ghcr.io/jgtolentino/odoo-ce:v0.9.0`. A `:latest` alias MAY exist but MUST NOT be relied upon as a stable version.

### 4.3 Environment Variables

| Variable | Purpose | Required | Default |
|----------|---------|----------|---------|
| `HOST` | Database host | Yes | `db` (Docker), `postgres-service` (K8S) |
| `USER` | Database user | Yes | `odoo` |
| `PASSWORD` | Database password | Yes | - |
| `ODOO_RC` | Config file path | Yes | `/etc/odoo/odoo.conf` |

### 4.4 Volume Mounts

| Path | Purpose | Type |
|------|---------|------|
| `/mnt/extra-addons` | Custom modules | Read-only |
| `/mnt/oca-addons` | OCA modules | Read-only |
| `/etc/odoo/odoo.conf` | Configuration | Read-only |
| `/var/lib/odoo` | Filestore | Read-write |

## 5. Security Requirements

### 5.1 Base Image Security
- Use official `odoo:18.0` image
- Regular security updates
- No additional package installation unless necessary

### 5.2 Runtime Security
- Execute as non-root user (`USER odoo`)
- No privileged capabilities
- Read-only filesystem where possible

### 5.3 Secret Management
- Never embed secrets in image
- Use environment variables or external secrets
- Follow canonical secret naming from `SECRETS_NAMING_AND_STORAGE.md`

## 6. CI/CD Pipeline

### 6.1 Build Process
```yaml
# GitHub Actions workflow
- name: Build and Push
  run: |
    docker build -t ghcr.io/jgtolentino/odoo-ce:latest .
    docker push ghcr.io/jgtolentino/odoo-ce:latest
```

### 6.2 Quality Gates
- Docker image builds successfully
- No security vulnerabilities in base image
- Custom modules are present and accessible
- Configuration file is valid

### 6.3 Deployment Triggers
- Push to `main` branch → Build and deploy to production
- Pull requests → Build and test only

## 7. Configuration Management

### 7.1 Odoo Configuration
- File: `deploy/odoo.conf`
- Mounted as read-only volume
- Environment-specific overrides via environment variables

### 7.2 Database Configuration
- Canonical database name: `odoo`
- Canonical database user: `odoo`
- Connection via environment variables

## 8. Cross-References

### 8.1 Related Documentation
- [SECRETS_NAMING_AND_STORAGE.md](../docs/SECRETS_NAMING_AND_STORAGE.md)
- [DEPLOYMENT_NAMING_MATRIX.md](../docs/DEPLOYMENT_NAMING_MATRIX.md)
- [DOKS_DEPLOYMENT_SUCCESS_CRITERIA.md](../docs/DOKS_DEPLOYMENT_SUCCESS_CRITERIA.md)
- [FINAL_DEPLOYMENT_GUIDE.md](../docs/FINAL_DEPLOYMENT_GUIDE.md)

### 8.2 Implementation Files
- `Dockerfile` - Image definition
- `docker-compose.prod.yml` - VPS deployment
- `deploy/k8s/` - Kubernetes manifests
- `.github/workflows/` - CI/CD pipelines

## 9. Acceptance Criteria

### 9.1 Image Quality
- [ ] Image builds successfully in CI
- [ ] Custom modules are accessible at runtime
- [ ] Configuration file is properly mounted
- [ ] Non-root user execution works correctly

### 9.2 Deployment Success
- [ ] VPS deployment via Docker Compose works
- [ ] DOKS deployment via Kubernetes works
- [ ] Database connectivity established
- [ ] Custom modules load without errors

### 9.3 Security Compliance
- [ ] No secrets embedded in image
- [ ] Non-root user execution verified
- [ ] Base image security scans pass
- [ ] Environment variables properly used

## 10. Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2025-11-24 | Initial specification aligned with current implementation |

---

This specification ensures that the custom Odoo CE image serves as a reliable, secure, and consistent deployment artifact across all InsightPulse ERP environments.
