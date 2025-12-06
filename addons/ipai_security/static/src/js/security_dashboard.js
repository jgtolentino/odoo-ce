/** @odoo-module **/

/**
 * Security & Compliance Workbench - Dashboard Components
 * ======================================================
 *
 * Client-side components for the security dashboard.
 */

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Security Health Score Widget
 *
 * Displays the overall security health score with color coding.
 */
class SecurityHealthScore extends Component {
    static template = "ipai_security.HealthScore";
    static props = {
        score: { type: Number },
    };

    get scoreClass() {
        const score = this.props.score;
        if (score >= 80) return "score-excellent";
        if (score >= 60) return "score-good";
        if (score >= 40) return "score-fair";
        if (score >= 20) return "score-poor";
        return "score-critical";
    }

    get scoreLabel() {
        const score = this.props.score;
        if (score >= 80) return "Excellent";
        if (score >= 60) return "Good";
        if (score >= 40) return "Fair";
        if (score >= 20) return "Needs Work";
        return "Critical";
    }
}

/**
 * Framework Coverage Widget
 *
 * Displays coverage percentage for a compliance framework.
 */
class FrameworkCoverage extends Component {
    static template = "ipai_security.FrameworkCoverage";
    static props = {
        name: { type: String },
        code: { type: String },
        coverage: { type: Number },
    };

    get coverageClass() {
        const coverage = this.props.coverage;
        if (coverage >= 80) return "coverage-high";
        if (coverage >= 50) return "coverage-medium";
        return "coverage-low";
    }
}

/**
 * Risk Summary Widget
 *
 * Displays a summary of open risks by level.
 */
class RiskSummary extends Component {
    static template = "ipai_security.RiskSummary";
    static props = {
        critical: { type: Number },
        high: { type: Number },
        medium: { type: Number },
        low: { type: Number },
    };

    get total() {
        return (
            this.props.critical +
            this.props.high +
            this.props.medium +
            this.props.low
        );
    }
}

/**
 * Security Dashboard Action
 *
 * Main dashboard view component.
 */
class SecurityDashboard extends Component {
    static template = "ipai_security.Dashboard";
    static components = {
        SecurityHealthScore,
        FrameworkCoverage,
        RiskSummary,
    };

    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.kpis = {};
        this.loading = true;
    }

    async willStart() {
        await this.loadKPIs();
    }

    async loadKPIs() {
        try {
            this.kpis = await this.rpc("/api/security/kpis", {});
            this.loading = false;
        } catch (error) {
            console.error("Failed to load security KPIs:", error);
            this.loading = false;
        }
    }

    async refreshKPIs() {
        this.loading = true;
        await this.loadKPIs();
    }

    openRisks() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Open Risks",
            res_model: "security.risk",
            view_mode: "tree,form",
            domain: [["status", "in", ["open", "in_progress"]]],
        });
    }

    openIncidents() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Recent Incidents",
            res_model: "security.incident",
            view_mode: "tree,form",
            domain: [["status", "!=", "closed"]],
        });
    }

    openAssets() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Assets",
            res_model: "security.asset",
            view_mode: "tree,form",
            domain: [["in_scope", "=", true]],
        });
    }

    openAISystems() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "AI Systems",
            res_model: "ai.system",
            view_mode: "tree,form",
            domain: [["status", "=", "production"]],
        });
    }

    async captureSnapshot() {
        try {
            const result = await this.rpc("/api/security/kpis/snapshot", {});
            this.notification.add("KPI snapshot captured successfully", {
                type: "success",
            });
            await this.refreshKPIs();
        } catch (error) {
            this.notification.add("Failed to capture snapshot", {
                type: "danger",
            });
        }
    }

    exportReport() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Export Report",
            res_model: "security.report.export.wizard",
            view_mode: "form",
            target: "new",
        });
    }
}

// Register the dashboard as a client action
registry.category("actions").add("security_dashboard", SecurityDashboard);

export { SecurityDashboard, SecurityHealthScore, FrameworkCoverage, RiskSummary };
