# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
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
#################################################################################
{
  "name"                 :  "Project Gantt Native Web View",
  "summary"              :  """The module adds a Gantt view to the project App so you can view the tasks and projects in through Gantt chart. Manage deadlines, tasks and projects with Gantt Chart.""",
  "category"             :  "Sales",
  "version"              :  "1.0.1",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Project-Gantt-Native-Web-View.html",
  "description"          :  """Odoo project Gantt View
        Odoo Gantt View
        Gantt View For Project
        Gant Native View
        Project gantt native
        Odoo Gantt Chart View
        Gantt Chart
        Gantt
        Chart
        Gantt view
        Web Gantt
        Web Gantt View""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=project_gantt_native",
  "depends"              :  ['hr_timesheet'],
  "data"                 :  ['views/wk_odoo_gantt_templates.xml'],
  "demo"                 :  ['data/demo.xml'],
  "qweb"                 :  ['static/src/xml/*.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  45,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
  "uninstall_hook"       :  "_reset_view",
}