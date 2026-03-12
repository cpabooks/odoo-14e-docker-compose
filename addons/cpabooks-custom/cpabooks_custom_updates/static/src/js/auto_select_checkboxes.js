odoo.define('cpabooks_custom_updates.auto_select_checkboxes', function (require) {
    'use strict';

    var ListController = require('web.ListController');

    ListController.include({
        renderButtons: function ($node) {
            this._super.apply(this, arguments);

            // Ensure all records are selected after rendering the buttons
            var self = this;
            this._rpc({
                model: this.modelName,
                method: 'search_read',
                args: [[], ['id']],
            }).then(function (records) {
                if (records.length) {
                    self.$('thead .o_list_record_selector input').prop('checked', true).trigger('click');
                }
            });
        },
    });
});
