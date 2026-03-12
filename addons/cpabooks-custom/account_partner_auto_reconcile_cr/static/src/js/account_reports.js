odoo.define('account_partner_auto_reconcile_cr.account_report', function (require) {
'use strict';

var core = require('web.core');
var AccountReportWidget = require('account_reports.account_report');
var QWeb = core.qweb;
var _t = core._t;

	AccountReportWidget.include({
		renderButtons: function() {
			var self = this;
			this._super.apply(this,arguments)
			_.each(this.$buttons.siblings('button'), function(el) {
				if($(el).attr('action') == 'partner_auto_reconcile') {
					$(el).unbind('click').bind().click(function(ev) {
						ev.preventDefault();
						ev.stopPropagation();
						return self._rpc({
		                      model: self.report_model,
		                      method: $(el).attr('action'),
		                      args: [self.financial_id, self.report_options],
		                      context: self.odoo_context,
		                  })
		                  .then(function(result){
		                      self.$buttons.attr('disabled', false);
		                      self.reload();
		                  })
		                  .guardedCatch(function() {
		                      self.$buttons.attr('disabled', false);
		                  });
					});
				}
			});
    	},
	})
});