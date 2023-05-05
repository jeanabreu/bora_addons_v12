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

from odoo import _, api, models,fields
from lxml.builder import E
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class Task(models.Model):
    _inherit = "project.task"
    _start_name = 'date_assign'
    _stop_name = 'date_deadline'

    gantt_color = fields.Char(string='Gantt Color Code',help="Here you can set a specific HTML color index (e.g. #ff0000) to display the gantt color.",default='#a9b5c1')

class Base(models.AbstractModel):
    _inherit = 'base'

    _start_name = 'date_start'       # start field to use for default gantt view
    _stop_name = 'date_stop'         # stop field to use for default gantt view


    @api.model
    def _get_default_gantt_view(self):
        """ Generates a default gantt view by trying to infer
        time-based fields from a number of pre-set attribute names

        :returns: a gantt view
        :rtype: etree._Element
        """
        view = E.gantt(string=self._description)

        gantt_field_names = {
            '_start_name': ['date_start', 'start_date', 'x_date_start', 'x_start_date'],
            '_stop_name': ['date_stop', 'stop_date', 'date_end', 'end_date', 'x_date_stop', 'x_stop_date', 'x_date_end', 'x_end_date'],
        }
        # _logger.info("---11---------test------%r---------",gantt_field_names.keys())
        for name in gantt_field_names.keys():
            # _logger.info("----22--------test------%r---------",self._fields)
            if getattr(self, name) not in self._fields:
                # _logger.info("------33------test------%r---------",name)
                for dt in gantt_field_names[name]:
                    if dt in self._fields:
                        setattr(self, name, dt)
                        break
                else:
                    raise UserError(_("Insufficient fields for Gantt View!"))
        view.set('date_start', self._start_name)
        view.set('date_stop', self._stop_name)

        return view

    @api.model
    def wk_gantt_unavailability(self, start_date, end_date, scale, group_bys=None, rows=None):
        """
        Get unavailabilities data to display in the Gantt view.

        This method is meant to be overriden by each model that want to
        implement this feature on a Gantt view.

        Example:
            * start_date = 01/01/2000, end_date = 01/07/2000, scale = 'week',
              rows = [{
                groupedBy: "project_id, user_id, stage_id",
                records: [1, 4, 2],
                name: "My Awesome Project",
                resId: 8,
                rows: [{
                    groupedBy: "user_id, stage_id",
                    records: [1, 2],
                    name: "Marcel",
                    resId: 18,
                    rows: [{
                        groupedBy: "stage_id",
                        records: [2],
                        name: "To Do",
                        resId: 3,
                        rows: []
                    }, {
                        groupedBy: "stage_id",
                        records: [1],
                        name: "Done",
                        resId: 9,
                        rows: []
                    }]
                }, {
                    groupedBy: "user_id, stage_id",
                    records: [4],
                    name: "Gilbert",
                    resId: 22,
                    rows: [{
                        groupedBy: "stage_id",
                        records: [4],
                        name: "Done",
                        resId: 9,
                        rows: []
                    }]
                }]
            }, {
                groupedBy: "project_id, user_id, stage_id",
                records: [3, 5, 7],
                name: "My Other Project",
                resId: 9,
                rows: [{
                    groupedBy: "user_id, stage_id",
                    records: [3, 5, 7],
                    name: "Undefined User",
                    resId: None,
                    rows: [{
                        groupedBy: "stage_id",
                        records: [3, 5, 7],
                        name: "To Do",
                        resId: 3,
                        rows: []
                    }]
            }, {
                groupedBy: "project_id, user_id, stage_id",
                records: [],
                name: "My group_expanded Project",
                resId: 27,
                rows: []
            }]

            * The expected return value of this function is the rows dict with
              a new 'unavailabilities' key in each row for which you want to
              display unavailabilities. Unavailablitities is a list in the form:
              [{
                  start: <start date of first unavailabity in UTC format>,
                  stop: <stop date of first unavailabity in UTC format>
              }, {
                  start: <start date of second unavailabity in UTC format>,
                  stop: <stop date of second unavailabity in UTC format>
              }, ...]

              To display that Marcel is unavailable January 2 afternoon and
              January 4 the whole day in his To Do row, this particular row in
              the rows dict should look like this when returning the dict at the
              end of this function :
              { ...
                {
                    groupedBy: "stage_id",
                    records: [2],
                    name: "To Do",
                    resId: 3,
                    rows: []
                    unavailabilities: [{
                        'start': '2018-01-02 14:00:00',
                        'stop': '2018-01-02 18:00:00'
                    }, {
                        'start': '2018-01-04 08:00:00',
                        'stop': '2018-01-04 18:00:00'
                    }]
                }
                ...
              }



        :param datetime start_date: start date
        :param datetime stop_date: stop date
        :param string scale: among "day", "week", "month" and "year"
        :param None | list[str] group_bys: group_by fields
        :param dict rows: dict describing the current rows of the gantt view
        :returns: dict of unavailability
        """
        return rows
