# Prompt: Integrate Supabase Expense Stack with OCR Service and Finance PPM/Odoo

You are Codex, the integration orchestrator for InsightPulse's expense platform.

## Objective
Connect the mobile expense stack (Supabase backend + Expo app) with the recently deployed OCR infrastructure and the Finance PPM/Odoo 18 CE environment, delivering a working end-to-end flow: receipt upload → OCR extraction → policy evaluation → approvals → Odoo/PPM sync.

## Systems & Ground Truth
- **Mobile/Backend**: Supabase Postgres/Auth/Storage + Edge Functions (`policy-evaluator`, `sync-odoo-expense`, new `ocr-receipt`).
- **OCR**: Existing external receipt/document extraction service (treat as canonical source of parsed data).
- **Finance PPM / Odoo 18 CE**: Finance Closing + hr_expense/analytic modules; PPM dashboards rely on exported expense sheets.
- **Security**: All secrets in Supabase secrets/DO env; never commit credentials.

## Required Deliverables
1) **OCR hookup**: Edge Function `ocr-receipt` that reads `receipts.file_url`, calls OCR endpoint (`OCR_SERVICE_URL`, `OCR_SERVICE_API_KEY`), stores normalized JSON in `receipts.ocr_raw`, and returns suggested expense defaults (date, merchant, amount, currency, tax_amount, category_guess).
2) **Policy evaluation**: Upgrade `policy-evaluator` to fetch active policies for `org_id`, evaluate warnings/blocks (e.g., max per category, receipt required over X), and persist `expenses.policy_flags`. Block submission on `severity='block'`.
3) **Odoo sync**: Implement `sync-odoo-expense` to push approved reports to Odoo as `hr.expense.sheet` + `hr.expense` lines; map analytic accounts/cost centers/projects; write back Odoo IDs to Supabase (`expense_reports.external_ref`, optional `expenses.odoo_id`). Trigger only on status transition `approved → exported`; log failures to `audit_logs`.
4) **Finance PPM visibility**: Create Supabase view/materialized view summarizing expense reports by period/org/status for PPM dashboards; expose via Odoo (FDW/read-only connection or API) so closing tasks can check exported reports.
5) **Mobile UX**: After receipt upload, call `ocr-receipt` and prefill new-expense form; surface policy warnings/blocks on create/edit and report submission.

## Execution Steps (Atomic)
1. Add env plumbing for OCR + Odoo credentials (Supabase secrets/DO env). Never hard-code.
2. Build `ocr-receipt` Edge Function:
   - Input: `{ receipt_id, org_id }` (service key).
   - Lookup `file_url` in `public.receipts` (verify org/user ownership).
   - POST to OCR service; normalize response; update `receipts.ocr_raw` and return suggestions.
3. Enhance `policy-evaluator`:
   - Fetch `policies` for `org_id`.
   - Evaluate simple rule set (max amount per category/day, receipt_required_over_amount, blacklisted merchants placeholder).
   - Return `policyFlags`; update `expenses.policy_flags`; block submit if any `block` flag.
4. Implement `sync-odoo-expense`:
   - Fetch report + expenses + mappings.
   - Resolve employee/analytic accounts; create sheet + lines via XML-RPC/JSON-RPC using env creds.
   - Update Supabase IDs; on failure log to `audit_logs` and keep status at `approved` with `sync_failed` flag.
5. PPM view + dashboard:
   - Create `view_expense_report_period_summary` aggregating totals by org/month/status.
   - Expose to Odoo/PPM widget or API endpoint for closing checkpoints.
6. Mobile updates:
   - Wire receipt upload → call `ocr-receipt` → prefill expense form.
   - Show inline policy warnings/blocks; prevent submission on block.
7. Testing/observability:
   - Add logging with request IDs/org IDs; unit tests for policy rules; integration test for OCR stub + Odoo sandbox.
   - RLS: service functions use service role; end users restricted to their data.

## Guardrails
- Do not modify Odoo core; use custom modules/controllers for any Odoo-side changes.
- Keep migrations idempotent; use snake_case; enforce RLS on new tables/views.
- Secrets never stored in repo; use Supabase secrets/DO env vars.
- Prefer small, testable increments: OCR → policy → Odoo sync → PPM dashboard.
