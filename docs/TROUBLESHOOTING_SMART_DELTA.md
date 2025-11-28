# Failure Modes & Troubleshooting Guide for AI Agents

This guide helps AI agents diagnose and resolve common issues in the InsightPulse ERP Smart Delta stack.

## Layers & Where Failures Happen

1. **Agent Layer** - prompt, tool use, or policy failures
2. **Code/Module Layer** - Python/XML/manifest/OCA-lint failures
3. **Odoo Runtime Layer** - QWeb exceptions, ACLs, cron, performance
4. **Infra Layer** - Docker, Postgres, Nginx/HTTPS, config file conflicts

---

## Agent Layer - Reasoning & Tool Failures

| Failure Mode            | Symptom / Code                                          | What the Agent Should Do                                                         |
| ----------------------- | ------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Tool/Action failure     | `exit code 127`, `command not found`, "Failed API call" | Inspect command, fix path/arguments, retry once with corrected command.          |
| Infinite reasoning loop | Repeated logs, high token usage, no progress            | Stop, summarize current state, re-plan in 3-5 steps, then execute stepwise.      |
| CE/OCA contamination    | Suggests `web_enterprise`, `iap_*`, or Enterprise menus | Abort that plan, replace with CE/OCA mapping, enforce `ipai_dev_studio_base`.    |
| LLM / API connectivity  | "Connection error", "Timeout", "Too many requests"      | Check endpoint health, retry with smaller model / fewer tokens / longer timeout. |

---

## Code / Module Layer - Install & Upgrade Failures

| Error Type              | Example Message / Symptom                                                            | Agent Response                                                                                                |
| ----------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| XML Parse / QWeb errors | `ParseError while parsing`, `QWebException`, template render failures                | Open the XML, validate `<odoo><data>` structure, check `inherit_id` / `xpath`, ensure referenced views exist. |
| Missing dependency      | `"Some modules are not loaded, some dependencies or manifest may be missing"`        | Inspect `__manifest__.py` `depends`, ensure every dependency is installable, update list, re-run `-i/-u`.     |
| OCA lint / bad patterns | `no-write-in-compute`, `invalid-commit`, `except-pass`, `print-used` from pre-commit | Rewrite to OCA standard, use `_logger`, avoid `cr.commit()`, no `except: pass`.                               |
| JS/asset crash          | Frontend error: `Error while loading ...`, console stack trace in browser            | Fix JS + XML asset definitions, bump module version, `-u` module, clear asset cache from `ir.attachment`.     |

---

## Odoo Runtime Layer - Application Failures

| Failure Type               | Symptom / Code                                     | Typical Cause & Fix                                                                                                            |
| -------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| QWeb `KeyError('website')` | 500 on `/web/login` or portal pages                | Template assumes `website` exists. Guard usage or install `website` module if allowed; otherwise patch template conditionally. |
| AccessError / MissingError | "You are not allowed to access this document"      | Missing ACL or record rule. Add proper `ir.model.access.csv` & rules, restart, re-test.                                        |
| Timeouts / Slow actions    | Requests hit `limit_time_real` or `limit_time_cpu` | Missing indexes, bad queries, or heavy reports. Profile query, add indexes, or optimize domain logic before bumping limits.    |

---

## Infra Layer - Docker / DB / Nginx / HTTPS Failures

| Failure Mode               | Symptom                                  | Fix                                                                                                             |
| -------------------------- | ---------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Mixed content / naked HTML | CSS/JS blocked when site is on HTTPS     | Ensure `proxy_mode=True`, set `web.base.url` to `https://erp.insightpulseai.net`, clear and rebuild web assets. |
| 502 Bad Gateway            | Nginx -> Odoo is down / not listening     | `docker ps`, `docker logs odoo18_ce_app`, ensure 8069 mapped, container healthy.                                |
| Config parse errors        | `DuplicateOptionError` from configparser | Deduplicate options in `odoo.conf`; each key only once.                                                         |
| Module not installing      | Module stuck "to install"                | Stop Odoo, run CLI `odoo -d <db> -i <module> --stop-after-init`, then restart service.                          |

---

## Quick Diagnostic Commands

```bash
# Check container status
docker ps -a | grep odoo

# View Odoo logs
docker logs -f odoo18_ce_app

# Check database connectivity
docker exec odoo18_ce_db pg_isready -U odoo -d ipai_prod

# Test module installation
docker compose run --rm odoo odoo -d ipai_prod -i <module> --stop-after-init

# Clear asset cache (run in Odoo shell)
docker compose run --rm odoo odoo shell -d ipai_prod -c "env['ir.attachment'].search([('url', 'like', '/web/assets/')]).unlink()"
```

---

## One-Shot Bring-Up Sequence

From repo root:

```bash
# 1) Build the image
docker build -t ghcr.io/jgtolentino/odoo-ce:18-oca-target .

# 2) Start Postgres + Odoo
docker compose up -d db
sleep 10
docker compose up -d odoo

# 3) Check logs
docker logs -f odoo18_ce_app
```

Once this is green, you've got a **canonical, agent-safe, OCA-first Odoo 18 CE target image**.

---

## Agent Contract

> "Assume `ipai_dev_studio_base` is installed.
> Never re-implement what CE/OCA already provides.
> Always go: Config -> OCA -> Delta -> Custom."
