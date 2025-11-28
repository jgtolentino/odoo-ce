/** @odoo-module **/

import { registry } from "@web/core/registry";

const BRAND_NAME = "InsightPulse ERP";

/**
 * Service to handle InsightPulse branding replacements
 */
const brandingService = {
    start() {
        // Replace page title
        this._updateTitle();

        // Observe title changes and revert Odoo branding
        this._observeTitleChanges();

        // Remove Odoo references from DOM
        this._cleanDomOnLoad();
    },

    _updateTitle() {
        if (document.title.includes("Odoo")) {
            document.title = document.title.replace(/Odoo/gi, BRAND_NAME);
        }
        // Set default title if empty or just "Odoo"
        if (!document.title || document.title.trim() === "" || document.title === "Odoo") {
            document.title = BRAND_NAME;
        }
    },

    _observeTitleChanges() {
        const titleObserver = new MutationObserver(() => {
            this._updateTitle();
        });

        const titleElement = document.querySelector("title");
        if (titleElement) {
            titleObserver.observe(titleElement, {
                childList: true,
                characterData: true,
                subtree: true,
            });
        }
    },

    _cleanDomOnLoad() {
        // Wait for DOM to be ready
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", () => this._cleanDom());
        } else {
            this._cleanDom();
        }
    },

    _cleanDom() {
        // Hide elements with Odoo branding text (safely, without :contains)
        const elementsToCheck = document.querySelectorAll(
            "a, span, div, p, h1, h2, h3, h4, h5, h6"
        );

        elementsToCheck.forEach((el) => {
            const text = el.textContent || "";
            // Hide "Powered by Odoo" and similar
            if (
                text.includes("Powered by Odoo") ||
                text.includes("Odoo Enterprise") ||
                text.includes("Upgrade to Enterprise")
            ) {
                el.style.display = "none";
            }
        });

        // Update footer copyright if present
        const footerLinks = document.querySelectorAll(".o_footer a, footer a");
        footerLinks.forEach((link) => {
            if (link.href && link.href.includes("odoo.com")) {
                link.style.display = "none";
            }
        });
    },
};

registry.category("services").add("ipai_branding", {
    start() {
        brandingService.start();
    },
});
