odoo.define('rdflex_pos_multi_currency.models', function (require) {
var core = require('web.core');

var models = require('point_of_sale.models');
var PosBaseWidget = require('point_of_sale.BaseWidget');
var _t = core._t;

models.load_models({
    model: 'res.currency',
    fields: ['name','symbol','position','rounding','rate'],
    loaded: function (self, currencies) {
        self.multi_currencies = currencies;
    }
});

var _super_Order = models.Order.prototype;
models.Order = models.Order.extend({
    initialize: function () {
        _super_Order.initialize.apply(this, arguments);
        this.currency = this.pos.currency;
    },
    init_from_JSON: function (json) {
        _super_Order.init_from_JSON.apply(this, arguments);
        this.currency = json.currency;
    },
    export_as_JSON: function () {
        var values = _super_Order.export_as_JSON.apply(this, arguments);
        values.currency = this.currency;
        return values;

    },
    set_currency: function (currency) {
        if (this.currency.id === currency.id) {
            return;
        }
        var form_currency = this.currency || this.pos.currency;
        var to_currency = currency;
        this.orderlines.each(function (line) {
            line.set_currency_price(form_currency, to_currency);
        });
        this.currency = currency;
    },
    get_currency: function (){
        return this.currency;
    },
    add_paymentline: function (cashregister) {
        var paymentlines = this.get_paymentlines();
        var is_multi_currency = false;
        _.each(paymentlines, function (line) {
            if (line.cashregister.currency_id[0] !== cashregister.currency_id[0]) {
                is_multi_currency = true;
            }
        });
        if (is_multi_currency) {
            this.pos.gui.show_popup('alert', {
                title : _t("Payment Error"),
                body  : _t("Payment of order should be in same currency. Payment could not be done with two different currency"),
            });
        } else {
            var journal_currency_id = cashregister.currency_id[0];
            if (this.currency.id !== journal_currency_id) {
                var currency = _.findWhere(this.pos.multi_currencies, {id:journal_currency_id})
                if (currency){
                    this.set_currency(currency);
                }
            }
            _super_Order.add_paymentline.apply(this, arguments);
        }
    },
});

models.Orderline = models.Orderline.extend({
    set_currency_price: function (form_currency, to_currency){
        var conversion_rate =  to_currency.rate / form_currency.rate;
        this.price = this.price * conversion_rate;
    },
});


PosBaseWidget.include({
    format_currency: function (amount,precision){
        var currency = (this.pos && this.pos.currency) ? this.pos.currency : {symbol:'$', position: 'after', rounding: 0.01, decimals: 2};
        amount = this.format_currency_no_symbol(amount, precision);
        currency = this.pos.get_order().currency || currency;
        if (currency.position === 'after') {
            return amount + ' ' + (currency.symbol || '');
        } else {
            return (currency.symbol || '') + ' ' + amount;
        }
    },
});


});
