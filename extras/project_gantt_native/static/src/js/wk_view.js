/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */

odoo.define('project_gantt_native.wk_GanttView', function (require) {
"use strict";

var AbstractView = require('web.AbstractView');
var core = require('web.core');
var GanttModel = require('project_gantt_native.wk_GanttModel');
var GanttRenderer = require('project_gantt_native.wk_GanttRenderer');
var GanttController = require('project_gantt_native.wk_GanttController');
var pyUtils = require('web.py_utils');
var view_registry = require('web.view_registry');

var _t = core._t;
var _lt = core._lt;

var wk_GanttView = AbstractView.extend({
    config: _.extend({}, AbstractView.prototype.config, {
        Model: GanttModel,
        Controller: GanttController,
        Renderer: GanttRenderer,
    }),
    display_name: _lt('Gantt'),
    icon: 'fa-tasks',
    viewType: 'gantt',

    /**
     * @override
     */
    init: function (viewInfo, params) {
        this._super.apply(this, arguments);

        this.wk_SCALES = {
            
            hours2: { string: _t('2 hour'), cellPrecisions: { full: 60, half: 30, quarter: 15 }, defaultPrecision: 'full', time: 'minutes', interval: 'hour' ,gap:2},
            hours4: { string: _t('4 hour'), cellPrecisions: { full: 60, half: 30, quarter: 15 }, defaultPrecision: 'full', time: 'minutes', interval: 'hour' ,gap:4},
            hours: { string: _t('8 hour'), cellPrecisions: { full: 60, half: 30, quarter: 15 }, defaultPrecision: 'full', time: 'minutes', interval: 'hour' ,gap:8},
            day: { string: _t('Day'), cellPrecisions: { full: 60, half: 30, quarter: 15 }, defaultPrecision: 'full', time: 'minutes', interval: 'hour' ,gap:1},
            week: { string: _t('Week'), cellPrecisions: { full: 24, half: 12 }, defaultPrecision: 'half', time: 'hours', interval: 'day' ,gap:1},
            month: { string: _t('Month'), cellPrecisions: { full: 24, half: 12 }, defaultPrecision: 'half', time: 'hours', interval: 'day' ,gap:1},
            year: { string: _t('Year'), cellPrecisions: { full: 1 }, defaultPrecision: 'full', time: 'months', interval: 'month' ,gap:1},
        };

        var arch = this.arch;

        var wk_decorationFields = [];
        _.each(arch.children, function (child) {
            if (child.tag === 'field') {
                wk_decorationFields.push(child.attrs.name);
            }
        });

        var wk_collapseFirstLevel = !!arch.attrs.collapse_first_level;

        var wk_displayUnavailability = !!arch.attrs.display_unavailability;

        var wk_colorField = arch.attrs.color;

        var wk_precisionAttrs = arch.attrs.precision ? pyUtils.py_eval(arch.attrs.precision) : {};
        var cellPrecisions = {};
        _.each(this.wk_SCALES, function (vals, key) {
            if (wk_precisionAttrs[key]) {
                var precision = wk_precisionAttrs[key].split(':'); 
                if (precision[1] && _.contains(_.keys(vals.cellPrecisions), precision[1])) {
                    cellPrecisions[key] = precision[1];
                }
            }
            cellPrecisions[key] = cellPrecisions[key] || vals.defaultPrecision;
        });

        var wk_consolidationMaxField;
        var wk_consolidationMaxValue;
        var consolidationMax = arch.attrs.consolidation_max ? pyUtils.py_eval(arch.attrs.consolidation_max) : {};
        if (Object.keys(consolidationMax).length > 0) {
            wk_consolidationMaxField = Object.keys(consolidationMax)[0];
            wk_consolidationMaxValue = consolidationMax[wk_consolidationMaxField];
            wk_collapseFirstLevel = !!wk_consolidationMaxField || wk_collapseFirstLevel;
        }

        var wk_consolidationParams = {
            field: arch.attrs.consolidation,
            maxField: wk_consolidationMaxField,
            maxValue: wk_consolidationMaxValue,
            excludeField: arch.attrs.consolidation_exclude,
        };

        var wk_formViewId = arch.attrs.form_view_id ? parseInt(arch.attrs.form_view_id, 10) : false;
        if (params.action && !wk_formViewId) { 
            var result = _.findWhere(params.action.views, { type: 'form' });
            wk_formViewId = result ? result.viewID : false;
        }
        var wk_dialogViews = [[wk_formViewId, 'form']];

        var wk_allowedScales;
        if (arch.attrs.scales) {
            var possibleScales = Object.keys(this.wk_SCALES);
            wk_allowedScales = _.reduce(arch.attrs.scales.split(','), function (wk_allowedScales, scale) {
                if (possibleScales.indexOf(scale) >= 0) {
                    wk_allowedScales.push(scale.trim());
                }
                return wk_allowedScales;
            }, []);
        } else {
            wk_allowedScales = Object.keys(this.wk_SCALES);
        }

        var scale = arch.attrs.default_scale || 'week';
        var initialDate = moment(params.initialDate || params.context.initialDate || new Date());
        var offset = arch.attrs.offset;
        if (offset && scale) {
            initialDate.add(offset, scale);
        }

        var thumbnails = this.arch.attrs.thumbnails ? pyUtils.py_eval(this.arch.attrs.thumbnails) : {};
        var wk_canPlan = this.arch.attrs.plan ? !!JSON.parse(this.arch.attrs.plan) : true;

        this.controllerParams.context = params.context || {};
        this.controllerParams.wk_dialogViews = wk_dialogViews;
        this.controllerParams.wk_SCALES = this.wk_SCALES;
        this.controllerParams.wk_allowedScales = wk_allowedScales;
        this.controllerParams.wk_collapseFirstLevel = wk_collapseFirstLevel;
        this.controllerParams.wk_createAction = arch.attrs.on_create || null;

        this.loadParams.initialDate = initialDate;
        this.loadParams.wk_collapseFirstLevel = wk_collapseFirstLevel;
        this.loadParams.wk_colorField = wk_colorField;
        this.loadParams.dateStartField = arch.attrs.date_start;
        this.loadParams.dateStopField = arch.attrs.date_stop;
        this.loadParams.progressField = arch.attrs.progress;
        this.loadParams.wk_decorationFields = wk_decorationFields;
        this.loadParams.defaultGroupBy = this.arch.attrs.default_group_by;
        this.loadParams.wk_displayUnavailability = wk_displayUnavailability;
        this.loadParams.fields = this.fields;
        this.loadParams.scale = scale;
        this.loadParams.wk_consolidationParams = wk_consolidationParams;

        this.rendererParams.canCreate = this.controllerParams.activeActions.create;
        this.rendererParams.canEdit = this.controllerParams.activeActions.edit;
        this.rendererParams.wk_canPlan = wk_canPlan && this.rendererParams.canEdit;
        this.rendererParams.fieldsInfo = viewInfo.fields;
        this.rendererParams.wk_SCALES = this.wk_SCALES;
        this.rendererParams.cellPrecisions = cellPrecisions;
        this.rendererParams.totalRow = arch.attrs.total_row || false;
        this.rendererParams.string = _t('Task Gantt View');
        this.rendererParams.popoverTemplate = _.findWhere(arch.children, {tag: 'templates'});
        this.rendererParams.wk_colorField = wk_colorField;
        this.rendererParams.progressField = arch.attrs.progress;
        this.rendererParams.wk_displayUnavailability = wk_displayUnavailability;
        this.rendererParams.wk_collapseFirstLevel = wk_collapseFirstLevel;
        this.rendererParams.wk_consolidationParams = wk_consolidationParams;
        this.rendererParams.thumbnails = thumbnails;
    },
});

view_registry.add('gantt', wk_GanttView);

return wk_GanttView;

});
