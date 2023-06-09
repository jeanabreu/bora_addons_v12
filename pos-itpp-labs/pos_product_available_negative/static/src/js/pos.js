/*  Copyright 2016 Stanislav Krotov <https://it-projects.info/team/ufaks>
    Copyright 2018-2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
    License MIT (https://opensource.org/licenses/MIT). */
odoo.define("pos_product_available_negative.pos", function(require) {
    "use strict";

    var screens = require("point_of_sale.screens");
    var models = require("point_of_sale.models");
    var core = require("web.core");
    var _t = core._t;

    screens.PaymentScreenWidget.include({
        validate_order: function(force_validation) {
            var self = this;
            var _super = this._super;
            if (!this.pos.config.negative_order_manager_permission) {
                return this._super(force_validation);
            }
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            var has_negative_product = false;
            for (var i = 0; i < orderlines.length; i++) {
                var line = orderlines[i];
                if (
                    line.product.type === "product" &&
                    line.product.qty_available < line.quantity
                ) {
                    has_negative_product = true;
                    self.gui
                        .sudo_custom({
                            title: _t(
                                "El pedido tiene un producto agotado y debe ser aprobado por unos de los siguientes supervisores"
                            ),
                            special_group: this.pos.config.negative_order_group_id[0],
                            do_not_change_cashier: true,
                            arguments: {ask_untill_correct: true},
                        })
                        .done(function(user) {
                            order.negative_stock_user_id = user;
                            _super.call(self, force_validation);
                        });
                    break;
                }
            }
            if (!has_negative_product) {
                this._super(force_validation);
            }
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this, arguments);
            json.negative_stock_user_id = this.negative_stock_user_id
                ? this.negative_stock_user_id.id
                : false;
            return json;
        },
    });

    screens.ProductListWidget.include({
        init: function(parent, options) {
            var self = this;
            this._super(parent, options);
            if (!this.pos.config.negative_order_warning) {
                return;
            }

            var click_product_handler_super = this.click_product_handler;
            this.click_product_handler = function() {
                var product = self.pos.db.get_product_by_id(this.dataset.productId);
                if (product.type === "product" && product.qty_available <= 0) {
                    return self.gui.show_popup("alert", {
                        title: _t("The product is out of stock"),
                        body: _t("It's unavailable to add the product"),
                    });
                }
                _.bind(click_product_handler_super, this)();
            };
        },
    });
});
