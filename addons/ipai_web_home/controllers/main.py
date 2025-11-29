# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home


class IPAIWebHome(Home):
    """
    Override /odoo route to show app grid menu instead of discuss redirect.
    """

    @http.route(['/odoo', '/odoo/'], type='http', auth="user", website=False)
    def odoo_home(self, **kw):
        """
        Override /odoo to show the app menu (home screen) instead of discuss.
        This provides a clean landing page with the app grid.
        """
        # Render the standard Odoo web client with the app menu
        # The default action will be the home menu (app grid)
        return self.web_client(s_action=None, **kw)
