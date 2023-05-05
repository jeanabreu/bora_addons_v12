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

import logging
import os

from lxml import etree

from odoo.loglevels import ustr
from odoo.tools import misc, view_validation
from odoo.modules.module import get_resource_path

_logger = logging.getLogger(__name__)

_gantt_validator = None


@view_validation.validate('gantt')
def schema_gantt(arch, **kwargs):
    """ Check the gantt view against its schema

    :type arch: etree._Element
    """
    global _gantt_validator
    if _gantt_validator is None:
        with misc.file_open(os.path.join('project_gantt_native', 'views', 'gantt.rng')) as f:
            # gantt.rng needs to include common.rng from the `base/rng/` directory. The idea
            # here is to set the base url of lxml lib in order to load relative file from the
            # `base/rng` directory.
            base_url = os.path.join(get_resource_path('base', 'rng'), '')
            _gantt_validator = etree.RelaxNG(etree.parse(f, base_url=base_url))

    if _gantt_validator.validate(arch):
        return True

    for error in _gantt_validator.error_log:
        _logger.error(ustr(error))
    return False
