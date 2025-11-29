/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";

// Override the default home action to show the app menu
patch(WebClient.prototype, {
    /**
     * Override loadRouterState to ensure /odoo shows the app menu (home)
     * instead of redirecting to discuss or any other app.
     */
    loadRouterState(state) {
        // If we're at /odoo with no action specified, force home menu
        if (window.location.pathname === '/odoo' || window.location.pathname === '/odoo/') {
            if (!state || !state.action) {
                // Show the app menu (home screen)
                return super.loadRouterState({
                    action: null,
                    actionStack: [],
                    menu_id: null
                });
            }
        }
        return super.loadRouterState(...arguments);
    },
});
