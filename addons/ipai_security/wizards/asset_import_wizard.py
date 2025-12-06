# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Asset Import Wizard
===================

Wizard for bulk importing security assets from external sources.
"""
import base64
import csv
import io

from odoo import api, fields, models
from odoo.exceptions import UserError


class AssetImportWizard(models.TransientModel):
    """
    Transient model for importing assets from CSV.

    Allows bulk import of security assets with automatic field mapping.
    """

    _name = "security.asset.import.wizard"
    _description = "Asset Import Wizard"

    file_data = fields.Binary(
        string="CSV File",
        required=True,
        help="CSV file with asset data",
    )
    file_name = fields.Char(
        string="File Name",
    )
    import_type = fields.Selection(
        [
            ("csv", "CSV File"),
            ("digitalocean", "DigitalOcean API"),
        ],
        string="Import Type",
        default="csv",
        required=True,
    )
    default_environment = fields.Selection(
        [
            ("production", "Production"),
            ("staging", "Staging"),
            ("development", "Development"),
        ],
        string="Default Environment",
        default="production",
    )
    mark_in_scope = fields.Boolean(
        string="Mark All In Scope",
        default=True,
    )
    state = fields.Selection(
        [
            ("draft", "Upload"),
            ("preview", "Preview"),
            ("done", "Done"),
        ],
        string="State",
        default="draft",
    )
    preview_line_ids = fields.One2many(
        "security.asset.import.wizard.line",
        "wizard_id",
        string="Preview Lines",
    )
    imported_count = fields.Integer(
        string="Imported Count",
        readonly=True,
    )
    error_count = fields.Integer(
        string="Error Count",
        readonly=True,
    )
    error_messages = fields.Text(
        string="Errors",
        readonly=True,
    )

    def action_preview(self):
        """Parse CSV and show preview."""
        self.ensure_one()

        if not self.file_data:
            raise UserError("Please upload a file first.")

        # Decode and parse CSV
        csv_data = base64.b64decode(self.file_data).decode("utf-8")
        reader = csv.DictReader(io.StringIO(csv_data))

        # Create preview lines
        self.preview_line_ids.unlink()
        lines = []
        for row in reader:
            lines.append((0, 0, {
                "name": row.get("name", ""),
                "code": row.get("code", ""),
                "asset_type": row.get("asset_type", "application"),
                "environment": row.get("environment", self.default_environment),
                "url": row.get("url", ""),
                "raw_data": str(row),
            }))

        self.write({
            "preview_line_ids": lines,
            "state": "preview",
        })

        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_import(self):
        """Import assets from preview."""
        self.ensure_one()

        Asset = self.env["security.asset"]
        imported = 0
        errors = []

        for line in self.preview_line_ids:
            try:
                Asset.create({
                    "name": line.name,
                    "code": line.code,
                    "asset_type": line.asset_type,
                    "environment": line.environment,
                    "url": line.url,
                    "in_scope": self.mark_in_scope,
                    "status": "active",
                })
                imported += 1
            except Exception as e:
                errors.append(f"Error importing {line.name}: {str(e)}")

        self.write({
            "state": "done",
            "imported_count": imported,
            "error_count": len(errors),
            "error_messages": "\n".join(errors) if errors else "No errors",
        })

        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }


class AssetImportWizardLine(models.TransientModel):
    """Preview line for asset import."""

    _name = "security.asset.import.wizard.line"
    _description = "Asset Import Preview Line"

    wizard_id = fields.Many2one(
        "security.asset.import.wizard",
        string="Wizard",
        ondelete="cascade",
    )
    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    asset_type = fields.Selection(
        [
            ("application", "Application/Service"),
            ("agent", "AI Agent"),
            ("droplet", "Droplet/VM"),
            ("database", "Database"),
            ("bucket", "Storage Bucket"),
            ("api", "API/Endpoint"),
            ("network", "Network Component"),
            ("other", "Other"),
        ],
        string="Asset Type",
    )
    environment = fields.Selection(
        [
            ("production", "Production"),
            ("staging", "Staging"),
            ("development", "Development"),
            ("testing", "Testing"),
        ],
        string="Environment",
    )
    url = fields.Char(string="URL")
    raw_data = fields.Text(string="Raw Data")
