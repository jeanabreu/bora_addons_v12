# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2017-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
##########################################################################

from . import models
from . import validation
from odoo import api, SUPERUSER_ID


def pre_init_check(cr):
    from odoo.service import common
    from odoo.exceptions import Warning
    version_info = common.exp_version()
    server_serie = version_info.get('server_serie')
    if server_serie != '12.0':
        raise Warning(
            'Module support Odoo series 12.0 found {}.'.format(server_serie))
    return True


def _reset_view(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    window_action = env.ref(
        'project.action_view_task')
    window_action.view_mode = 'kanban,tree,form,calendar,pivot,graph,activity'

    window_action_view = env.ref('project.open_view_task_list_kanban')
    window_action_view.view_mode = 'kanban'
