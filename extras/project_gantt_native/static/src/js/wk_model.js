/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */

odoo.define('project_gantt_native.wk_GanttModel', function (require) {
"use strict";

var AbstractModel = require('web.AbstractModel');
var concurrency = require('web.concurrency');
var core = require('web.core');
var fieldUtils = require('web.field_utils');
var session = require('web.session');

var _t = core._t;


var wk_GanttModel = AbstractModel.extend({
    /**
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);

        this.dp = new concurrency.DropPrevious();
        this.wk_mutex = new concurrency.Mutex();
    },

    
    collapseRow: function (rowId) {
        this.allRows[rowId].isOpen = false;
    },
    

    collapseRows: function () {
        this.wk_ganttData.rows.forEach(function (group) {
            group.isOpen = false;
        });
    },
    

    convertToServerTime: function (date) {
        var result = date.clone();
        if (!result.isUTC()) {
            result.subtract(session.getTZOffset(date), 'minutes');
        }
        return result.locale('en').format('YYYY-MM-DD HH:mm:ss');
    },
    
    get: function () {
        return _.extend({}, this.wk_ganttData);
    },
    
    expandRow: function (rowId) {
        this.allRows[rowId].isOpen = true;
    },
    
    expandRows: function () {
        var self = this;
        Object.keys(this.allRows).forEach(function (rowId) {
            var row = self.allRows[rowId];
            if (row.isGroup) {
                self.allRows[rowId].isOpen = true;
            }
        });
    },
    

    load: function (params) {
        this.modelName = params.modelName;
        this.fields = params.fields;
        this.domain = params.domain;
        this.context = params.context;
        this.wk_decorationFields = params.wk_decorationFields;
        this.wk_colorField = params.wk_colorField;
        this.progressField = params.progressField;
        this.wk_consolidationParams = params.wk_consolidationParams;
        this.wk_collapseFirstLevel = params.wk_collapseFirstLevel;
        this.wk_displayUnavailability = params.wk_displayUnavailability;

        this.defaultGroupBy = params.defaultGroupBy ? [params.defaultGroupBy] : [];
        if (!params.groupedBy || !params.groupedBy.length) {
            params.groupedBy = this.defaultGroupBy;
        }

        this.wk_ganttData = {
            dateStartField: params.dateStartField,
            dateStopField: params.dateStopField,
            groupedBy: params.groupedBy,
            fields: params.fields,
        };
        this._setRange(params.initialDate, params.scale);
        return this._fetchData().then(function () {
            
            return Promise.resolve();
        });
    },
    
    reload: function (handle, params) {
        if ('scale' in params) {
            this._setRange(this.wk_ganttData.focusDate, params.scale);
        }
        if ('date' in params) {
            this._setRange(params.date, this.wk_ganttData.scale);
        }
        if ('domain' in params) {
            this.domain = params.domain;
        }
        if ('groupBy' in params) {
            if (params.groupBy && params.groupBy.length) {
                this.wk_ganttData.groupedBy = params.groupBy.filter(
                    groupedByField => {
                        var fieldName = groupedByField.split(':')[0]
                        return fieldName in this.fields && this.fields[fieldName].type.indexOf('date') === -1;
                    }
                );
                if(this.wk_ganttData.groupedBy.length !== params.groupBy.length){
                    this.do_warn(_t('Invalid group by'), _t('Grouping by date is not supported, ignoring it'));
                }
            } else {
                this.wk_ganttData.groupedBy = this.defaultGroupBy;
            }
        }
        return this._fetchData()
    },
    

    copy: function (id, schedule) {
        var self = this;
        const defaults = this.rescheduleData(schedule);
        return this.wk_mutex.exec(function () {
            return self._rpc({
                model: self.modelName,
                method: 'copy',
                args: [id, defaults],
            });
        });
    },
    
    reschedule: function (ids, schedule, isUTC) {
        var self = this;
        if (!_.isArray(ids)) {
            ids = [ids];
        }
        const data = this.rescheduleData(schedule, isUTC);
        return this.wk_mutex.exec(function () {
            return self._rpc({
                model: self.modelName,
                method: 'write',
                args: [ids, data],
            });
        });
    },
   
    rescheduleData: function (schedule, isUTC) {
        const allowedFields = [
            this.wk_ganttData.dateStartField,
            this.wk_ganttData.dateStopField,
            ...this.wk_ganttData.groupedBy
        ];

        const data = _.pick(schedule, allowedFields);

        let type;
        for (let k in data) {
            type = this.fields[k].type;
            if (data[k] && (type === 'datetime' || type === 'date') && !isUTC) {
                data[k] = this.convertToServerTime(data[k]);
            }
        };
        return data
    },

   
    _fetchData: function () {
        var self = this;
        var domain = this._getDomain();
        var context = _.extend(this.context, {'group_by': this.wk_ganttData.groupedBy});

        var groupsDef;
        if (this.wk_ganttData.groupedBy.length) {
            groupsDef = this._rpc({
                model: this.modelName,
                method: 'read_group',
                fields: this._getFields(),
                domain: domain,
                context: context,
                groupBy: this.wk_ganttData.groupedBy,
                lazy: this.wk_ganttData.groupedBy.length === 1,
            });
        }

        var dataDef = this._rpc({
            route: '/web/dataset/search_read',
            model: this.modelName,
            fields: this._getFields(),
            context: context,
            domain: domain,
        });
        return this.dp.add(Promise.all([groupsDef, dataDef])).then(function (results) {
            var groups = results[0];
            var searchReadResult = results[1];
            if (groups) {
                _.each(groups, function (group) {
                    group.id = _.uniqueId('group');
                });
            }
            var oldRows = self.allRows;
            self.allRows = {};
            self.wk_ganttData.groups = groups;
            self.wk_ganttData.records = self._parseServerData(searchReadResult.records);
            self.wk_ganttData.rows = self._generateRows({
                groupedBy: self.wk_ganttData.groupedBy,
                groups: groups,
                oldRows: oldRows,
                records: self.wk_ganttData.records,
            });
            var unavailabilityProm;
            if (self.wk_displayUnavailability) {
                unavailabilityProm = self._fetchUnavailability();
            }
            return unavailabilityProm;
        });
    },
    

    _computeUnavailabilityRows: function(rows) {
        var self = this;
        return _.map(rows, function (r) {
            if (r) {
                return {
                    groupedBy: r.groupedBy,
                    records: r.records,
                    name: r.name,
                    resId: r.resId,
                    rows: self._computeUnavailabilityRows(r.rows)
                }
            } else {
                return r;
            }
        });
    },
    
    _fetchUnavailability: function () {
        var self = this;
        return this._rpc({
            model: this.modelName,
            method: 'wk_gantt_unavailability',
            args: [
                this.convertToServerTime(this.wk_ganttData.startDate),
                this.convertToServerTime(this.wk_ganttData.stopDate),
                this.wk_ganttData.scale,
                this.wk_ganttData.groupedBy,
                this._computeUnavailabilityRows(this.wk_ganttData.rows),
            ],
            context: this.context,
        }).then(function (enrichedRows) {
            
            self._updateUnavailabilityRows(self.wk_ganttData.rows, enrichedRows);
        });
    },
    
    _updateUnavailabilityRows: function (original, enriched) {
        var self = this;
        _.zip(original, enriched).forEach(function (rowPair) {
            var o = rowPair[0];
            var e = rowPair[1];
            o.unavailabilities = _.map(e.unavailabilities, function (u) {
                u.start = self._parseServerValue({ type: 'datetime' }, u.start);
                u.stop = self._parseServerValue({ type: 'datetime' }, u.stop);
                return u;
            });
            if (o.rows && e.rows) {
                self._updateUnavailabilityRows(o.rows, e.rows);
            }
        });
    },
    
    _generateRows: function (params) {
        var self = this;
        var groups = params.groups;
        var groupedBy = params.groupedBy;
        var rows;
        if (!groupedBy.length) {
            var row = {
                groupId: groups && groups.length && groups[0].id,
                id: _.uniqueId('row'),
                records: params.records,
            };
            rows = [row];
            this.allRows[row.id] = row;
        } else {
            
            var groupedByField = groupedBy[0];
            var currentLevelGroups = _.groupBy(groups, groupedByField);
            rows = Object.keys(currentLevelGroups).map(function (key) {
                var subGroups = currentLevelGroups[key];
                var groupRecords = _.filter(params.records, function (record) {
                    return _.isEqual(record[groupedByField], subGroups[0][groupedByField]);
                });

                
                var value;
                if (groupRecords.length) {
                    value = groupRecords[0][groupedByField];
                } else {
                    value = subGroups[0][groupedByField];
                }

                var path = (params.parentPath || '') + JSON.stringify(value);
                var minNbGroups = self.wk_collapseFirstLevel ? 0 : 1;
                var isGroup = groupedBy.length > minNbGroups;
                var row = {
                    name: self._getFieldFormattedValue(value, self.fields[groupedByField]),
                    groupId: subGroups[0].id,
                    groupedBy: groupedBy,
                    groupedByField: groupedByField,
                    id: _.uniqueId('row'),
                    resId: _.isArray(value) ? value[0] : value,
                    isGroup: isGroup,
                    isOpen: !_.findWhere(params.oldRows, {path: path, isOpen: false}),
                    path: path,
                    records: groupRecords,
                };

                if(!isGroup){
                    row.priority = row.records[0].priority;
                    // row.gantt_color = row.records[0].gantt_color;
                }

                if (isGroup) {
                    row.rows = self._generateRows({
                        groupedBy: groupedBy.slice(1),
                        groups: subGroups,
                        oldRows: params.oldRows,
                        parentPath: row.path + '/',
                        records: groupRecords,
                    });
                    row.childrenRowIds = [];
                    row.rows.forEach(function (subRow) {
                        row.childrenRowIds.push(subRow.id);
                        row.childrenRowIds = row.childrenRowIds.concat(subRow.childrenRowIds || []);
                    });
                }

                self.allRows[row.id] = row;

                return row;
            });
            if (!rows.length) {
                rows = [{
                    groups: [],
                    records: [],
                }];
            }
        }
        return rows;
    },
    
    _getDomain: function () {
        var domain = [
            [this.wk_ganttData.dateStartField, '<=', this.convertToServerTime(this.wk_ganttData.stopDate)],
            [this.wk_ganttData.dateStopField, '>=', this.convertToServerTime(this.wk_ganttData.startDate)],
        ];
        return this.domain.concat(domain);
    },
    
    _getFields: function () {
        var fields = ['display_name', this.wk_ganttData.dateStartField, this.wk_ganttData.dateStopField,'priority','progress','gantt_color'];
        fields = fields.concat(this.wk_ganttData.groupedBy, this.wk_decorationFields);

        if (this.progressField) {
            fields.push(this.progressField);
        }

        if (this.wk_colorField) {
            fields.push(this.wk_colorField);
        }

        if (this.wk_consolidationParams.field) {
            fields.push(this.wk_consolidationParams.field);
        }

        if (this.wk_consolidationParams.excludeField) {
            fields.push(this.wk_consolidationParams.excludeField);
        }

        return _.uniq(fields);
    },
    
    _getFieldFormattedValue: function (value, field) {
        var options = {};
        if (field.type === 'boolean') {
            options = {forceString: true};
        }
        var formattedValue = fieldUtils.format[field.type](value, field, options);
        return formattedValue || _.str.sprintf(_t('Undefined %s'), field.string);
    },
   
    _parseServerData: function (data) {
        var self = this;

        data.forEach(function (record) {
            Object.keys(record).forEach(function (fieldName) {
                record[fieldName] = self._parseServerValue(self.fields[fieldName], record[fieldName]);
            });
        });

        return data;
    },
   
    _setRange: function (focusDate, scale) {
        this.wk_ganttData.scale = scale;
        this.wk_ganttData.focusDate = focusDate;
        if(['hours','hours4','hours2'].includes(scale)){
            this.wk_ganttData.startDate = focusDate.clone().startOf('day');
            this.wk_ganttData.stopDate = focusDate.clone().endOf('day');
        }
        else{
            this.wk_ganttData.startDate = focusDate.clone().startOf(scale);
            this.wk_ganttData.stopDate = focusDate.clone().endOf(scale);
        }
    },
});

return wk_GanttModel;

});
