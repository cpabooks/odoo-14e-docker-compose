odoo.define('cpabooks_custom_print_v1_ykt.sale_order_line', function(require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;

    var SaleOrderLine = require('sale.OrderLine');

    SaleOrderLine.include({
        events: _.extend({}, SaleOrderLine.prototype.events, {
            'click .add-line': '_onClickAddDescription',
        }),

        _renderAddLine: function() {
            this.$('.add-line').text(_t('Add a description'));
        },

        _onClickAddDescription: function(ev) {
            this._renderAddLine();
            this._onClickAddLine(ev);
        },
    });
});