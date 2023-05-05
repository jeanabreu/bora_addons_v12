/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */

odoo.define('project_gantt_native.wk_GanttController', function (require) {
"use strict";

var AbstractController = require('web.AbstractController');
var core = require('web.core');
var dialogs = require('web.view_dialogs');
var confirmDialog = require('web.Dialog').confirm;

var QWeb = core.qweb;
var _t = core._t;

var wk_GanttController = AbstractController.extend({
   
    custom_events: _.extend({}, AbstractController.prototype.custom_events, {
        add_button_clicked: 'wk_onCellAddClicked',
        plan_button_clicked: 'wk_onCellPlanClicked',
        collapse_row: 'wk_onCollapseRow',
        expand_row: 'wk_onExpandRow',
        pill_clicked: '_onPillClicked',
        pill_resized: 'wk_onPillResized',
        pill_dropped: 'wk_onPillDropped',
        updating_pill_started: 'wk_onPillUpdatingStarted',
        updating_pill_stopped: 'wk_onPillUpdatingStopped',
    }),
    
    init: function (parent, model, renderer, params) {
        this._super.apply(this, arguments);
        this.model = model;
        this.context = params.context;
        this.wk_dialogViews = params.wk_dialogViews;
        this.wk_SCALES = params.wk_SCALES;
        this.wk_allowedScales = params.wk_allowedScales;
        this.wk_collapseFirstLevel = params.wk_collapseFirstLevel;
        this.wk_createAction = params.wk_createAction;
    },

    
    renderButtons: function ($node) {
        if ($node) {
            var state = this.model.get();
            this.$buttons = $(QWeb.render('wk.buttons', {
                groupedBy: state.groupedBy,
                widget: this,
                wk_SCALES: this.wk_SCALES,
                activateScale: state.scale,
                wk_allowedScales: this.wk_allowedScales,
            }));
            // this.$buttons.click(this._onAddClicked.bind(this));
            this.$buttons.on('click', '.wk_gantt_addbtn', this._onAddClicked.bind(this));
            this.$buttons.on('click', '.wk_gantt_scale', this._onScaleClicked.bind(this));
            this.$buttons.on('click', '.wk_gantt_previous', this._onPrevPeriodClicked.bind(this));
            this.$buttons.on('click', '.wk_gantt_next', this._onNextPeriodClicked.bind(this));
            this.$buttons.on('click', '.wk_gantt_today', this._onTodayClicked.bind(this));
            this.$buttons.on('click', '.wk_gantt_expandbtn', this._onExpandClicked.bind(this));
            this.$buttons.on('click', '.wk_gantt_collapsebtn', this._onCollapseClicked.bind(this));
            this.$buttons.appendTo($node);
        }
    },

    
    _copy: function (id, schedule) {
        return this._executeAsyncOperation(
            this.model.copy.bind(this.model),
            [id, schedule]
        );
    },
   
    _executeAsyncOperation: function (operation, args) {
        const self = this;
        var prom = new Promise(function (resolve, reject) {
            var asyncOp = operation(...args);
            asyncOp.then(resolve).guardedCatch(resolve);
            self.dp.add(asyncOp).guardedCatch(reject);
        });
        return prom.then(this.reload.bind(this, {}));
    },
    
    _getDialogContext: function (date, groupId) {
        var state = this.model.get();
        var context = {};
        context[state.dateStartField] = date.clone();
        context[state.dateStopField] = date.clone().endOf(this.wk_SCALES[state.scale].interval);

        if (groupId) {
            
            _.each(state.groupedBy, function (fieldName) {
                var groupValue = _.find(state.groups, function (group) {
                    return group.id === groupId;
                });
                var value = groupValue[fieldName];
                if (_.isArray(value)) {
                    value = value[0];
                }
                context[fieldName] = value;
            });
        }

       
        for (var k in context) {
            var type = state.fields[k].type;
            if (context[k] && (type === 'datetime' || type === 'date')) {
                context[k] = this.model.convertToServerTime(context[k]);
            }
        }

        return context;
    },
    
    _openDialog: function (resID, context) {
        var title = resID ? _t("Open") : _t("Create");

        return new dialogs.FormViewDialog(this, {
            title: _.str.sprintf(title),
            res_model: this.modelName,
            view_id: this.wk_dialogViews[0][0],
            res_id: resID,
            readonly: !this.is_action_enabled('edit'),
            deletable: this.is_action_enabled('edit') && resID,
            context: _.extend({}, this.context, context),
            on_saved: this.reload.bind(this, {}),
            on_remove: this._onDialogRemove.bind(this, resID),
        }).open();
    },
   
    _onDialogRemove: function (resID) {
        var controller = this;

        var confirm = new Promise(function (resolve) {
            confirmDialog(this, _t('Are you sure to delete this record?'), {
                confirm_callback: function () {
                    resolve(true);
                },
                cancel_callback: function () {
                    resolve(false);
                },
            });
        });

        return confirm.then(function (confirmed) {
            if ((!confirmed)) {
                return Promise.resolve();
            }// else
            return controller._rpc({
                model: controller.modelName,
                method: 'unlink',
                args: [[resID,],],
            }).then(function () {
                return controller.reload();
            })
        });
    },
    
    _openPlanDialog: function (context) {
        var self = this;
        var state = this.model.get();
        var domain = [
            '|',
            [state.dateStartField, '=', false],
            [state.dateStopField, '=', false],
        ];
        new dialogs.SelectCreateDialog(this, {
            title: _t("Plan"),
            res_model: this.modelName,
            domain: this.model.domain.concat(domain),
            views: this.wk_dialogViews,
            context: _.extend({}, this.context, context),
            on_selected: function (records) {
                var ids = _.pluck(records, 'id');
                if (ids.length) {
                   
                    self._reschedule(ids, context, true);
                }
            },
        }).open();
    },
    
    _onCreate: function (context) {
        if (this.wk_createAction) {
            var fullContext = _.extend({}, this.context, context);
            this.do_action(this.wk_createAction, {
                additional_context: fullContext,
                on_close: this.reload.bind(this, {})
            });
        } else {
            this._openDialog(undefined, context);
        }
    },
    
    _reschedule: function (ids, schedule, isUTC) {
        return this._executeAsyncOperation(
            this.model.reschedule.bind(this.model),
            [ids, schedule, isUTC]
        );
    },
    
    _update: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            var nbGroups = self.model.get().groupedBy.length;
            var minNbGroups = self.wk_collapseFirstLevel ? 0 : 1;
            var displayButtons = nbGroups > minNbGroups;
            self.$buttons.find('.wk_gantt_expandbtn').toggle(displayButtons);
            self.$buttons.find('.wk_gantt_collapsebtn').toggle(displayButtons);
        });
    },

    
    wk_onCellAddClicked: function (ev) {
        ev.stopPropagation();
        var context = this._getDialogContext(ev.data.date, ev.data.groupId);
        for (var k in context) {
            context[_.str.sprintf('default_%s', k)] = context[k];
        }
        this._onCreate(context);
    },
   
    _onAddClicked: function (ev) {
        ev.preventDefault();
        var context = {};
        var state = this.model.get();
        context[state.dateStartField] = this.model.convertToServerTime(state.focusDate.clone().startOf(state.scale));
        context[state.dateStopField] = this.model.convertToServerTime(state.focusDate.clone().endOf(state.scale));
        for (var k in context) {
            context[_.str.sprintf('default_%s', k)] = context[k];
        }
        this._onCreate(context);
    },
    
    _onCollapseClicked: function (ev) {
        ev.preventDefault();
        this.model.collapseRows();
        this.update({}, { reload: false });
    },
    
    wk_onCollapseRow: function (ev) {
        ev.stopPropagation();
        this.model.collapseRow(ev.data.rowId);
        this.renderer.updateRow(this.model.get(ev.data.rowId));
    },
   
    _onExpandClicked: function (ev) {
        ev.preventDefault();
        this.model.expandRows();
        this.update({}, { reload: false });
    },
   
    wk_onExpandRow: function (ev) {
        ev.stopPropagation();
        this.model.expandRow(ev.data.rowId);
        this.renderer.updateRow(this.model.get(ev.data.rowId));
    },
    
    _onNextPeriodClicked: function (ev) {
        ev.preventDefault();
        var state = this.model.get();
        if(['hours','hours4','hours2'].includes(state.scale)){
            this.update({ date: state.focusDate.add(1, 'day') });
        }
        else{
            this.update({ date: state.focusDate.add(1, state.scale) });
        }
    },
    
    _onPillClicked: async function (ev) {
        if (!this._updating) {
            ev.data.target.addClass('o_gantt_pill_editing');

            
            await this.model.wk_mutex.getUnlockedDef();

            var dialog = this._openDialog(ev.data.target.data('id'));
            dialog.on('closed', this, function () {
                ev.data.target.removeClass('o_gantt_pill_editing');
            });
        }
    },
    
    wk_onPillDropped: function (ev) {
        ev.stopPropagation();

        var state = this.model.get();

        var schedule = {};

        var diff = ev.data.diff;
        if (diff) {
            var pill = _.findWhere(state.records, { id: ev.data.pillId });
            schedule[state.dateStartField] = pill[state.dateStartField].clone().add(diff, this.wk_SCALES[state.scale].time);
            schedule[state.dateStopField] = pill[state.dateStopField].clone().add(diff, this.wk_SCALES[state.scale].time);
        } else if (ev.data.action === 'copy') {
            const pill = _.findWhere(state.records, { id: ev.data.pillId });
            schedule[state.dateStartField] = pill[state.dateStartField].clone();
            schedule[state.dateStopField] = pill[state.dateStopField].clone();
        }

        if (ev.data.newGroupId && ev.data.newGroupId !== ev.data.oldGroupId) {
            var group = _.findWhere(state.groups, { id: ev.data.newGroupId });

            
            var fieldsToWrite = state.groupedBy.slice(0, ev.data.groupLevel + 1);
            _.each(fieldsToWrite, function (fieldName) {
                schedule[fieldName] = group[fieldName];

                if (_.isArray(schedule[fieldName])) {
                    schedule[fieldName] = schedule[fieldName][0];
                }
            });
        }
        if (ev.data.action === 'copy') {
            this._copy(ev.data.pillId, schedule);
        } else {
            this._reschedule(ev.data.pillId, schedule);
        }
    },
  
    wk_onPillResized: function (ev) {
        ev.stopPropagation();
        var schedule = {};
        schedule[ev.data.field] = ev.data.date;
        this._reschedule(ev.data.id, schedule);
    },
    
    wk_onPillUpdatingStarted: function (ev) {
        ev.stopPropagation();
        this._updating = true;
    },
    
    wk_onPillUpdatingStopped: function (ev) {
        ev.stopPropagation();
        this._updating = false;
    },
    
   
    wk_onCellPlanClicked: function (ev) {
        ev.stopPropagation();
        var context = this._getDialogContext(ev.data.date, ev.data.groupId);
        this._openPlanDialog(context);
    },
   
    _onPrevPeriodClicked: function (ev) {
        ev.preventDefault();
        var state = this.model.get();
        if(['hours','hours4','hours2'].includes(state.scale)){
            this.update({ date: state.focusDate.subtract(1, 'day') });
        }
        else{
            this.update({ date: state.focusDate.subtract(1, state.scale) });
        }
    },
   
    _onScaleClicked: function (ev) {
        ev.preventDefault();
        var $button = $(ev.currentTarget);
        this.$buttons.find('.wk_gantt_scale').removeClass('active');
        $button.addClass('active');
        this.$buttons.find('.o_gantt_dropdown_selected_scale').text($button.text());
        this.update({ scale: $button.data('value') });
    },
   
    _onTodayClicked: function (ev) {
        ev.preventDefault();
        this.update({ date: moment() });
    },
});

return wk_GanttController;

});
