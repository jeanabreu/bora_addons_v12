odoo.define('pos_disable_discount.discount_control',function(require){
	"use strict"

	var screens = require('point_of_sale.screens');
	var models = require('point_of_sale.models');

	models.load_fields("pos.config",['disable_discount']);
	
	screens.NumpadWidget.include({
		applyAccessRights: function() {
			this._super();
			var has_discount_control = this.pos.config.disable_discount;
			this.$el.find('.mode-button[data-mode="discount"]')
            	.toggleClass('disabled-mode', has_discount_control)
            	.prop('disabled', has_discount_control);
			
			this.$el.find('.mode-button[data-mode="price"]')
            	.toggleClass('disabled-mode', has_discount_control)
            	.prop('disabled', has_discount_control);
			

			if (has_discount_control && this.state.get('mode')=='discount'){
            	this.state.changeMode('quantity');
      		}
			
			  
		},
	})
})