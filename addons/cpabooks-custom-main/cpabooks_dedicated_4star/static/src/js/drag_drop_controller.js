odoo.define('cpabooks_dedicated_4star.drag_drop_controller', function (require) {
    "use strict";

    var KanbanController = require('web.KanbanController');
    var rpc = require('web.rpc');

    KanbanController.include({
        custom_events: _.extend({}, KanbanController.prototype.custom_events, {
            field_moved: '_onFieldMoved',
        }),

        _onFieldMoved: function (ev) {
            var self = this;
            var fieldId = ev.data.field_id;
            var description = ev.data.description;
            var sourceField = ev.data.source_field;
            var targetField = ev.data.target_field;

            console.log('Controller handling move:', fieldId, sourceField, targetField);

            // Call server method to handle the field move
            rpc.query({
                model: 'bulk.res.partner.export.wizard',
                method: 'move_field',
                args: [this.renderer.state.context.active_id, fieldId, description, sourceField, targetField],
            }).then(function (result) {
                if (result) {
                    console.log('Field moved successfully');
                    // Reload the view to reflect changes
                    self.reload();
                }
            }).catch(function (error) {
                console.error('Error moving field:', error);
            });
        },
    });
});