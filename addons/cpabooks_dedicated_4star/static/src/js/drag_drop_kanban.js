odoo.define('cpabooks_dedicated_4star.drag_drop_kanban', function (require) {
    "use strict";

    const FormController = require('web.FormController');
    const rpc = require('web.rpc');

    FormController.include({
        /**
         * Override the render_sheet method to initialize sortable after the view has rendered.
         */
        _renderSheet: function () {
            this._super.apply(this, arguments);
            // Check if we are on the correct form view
            if (this.el.classList.contains('o_partner_export_wizard')) {
                this._makeKanbanSortable();
            }
        },

        /**
         * Initializes the jQuery UI sortable widget on the kanban columns.
         */
        _makeKanbanSortable: function () {
            const $available = this.$('.available_fields_kanban .o_kanban_view');
            const $selected = this.$('.selected_fields_kanban .o_kanban_view');
            const wizardId = this.model.get(this.handle).res_id;

            $available.sortable({
                connectWith: $selected,
                // This event fires when an item from a connected sortable is dropped
                receive: (event, ui) => this._handleDrop(ui.item, 'selected', wizardId),
            }).disableSelection();

            $selected.sortable({
                connectWith: $available,
                receive: (event, ui) => this._handleDrop(ui.item, 'available', wizardId),
            }).disableSelection();
        },

        /**
         * Handles the drop event, gets the record ID, and calls the Python method.
         * @param {jQuery} item The jQuery object for the moved kanban card.
         * @param {String} newState The target state ('available' or 'selected').
         * @param {Number} wizardId The database ID of the current wizard record.
         */
        _handleDrop: function (item, newState, wizardId) {
            const lineId = item.data('id');
            if (!lineId || !wizardId) return;

            // Call the Python method on the wizard to update the record's state
            rpc.query({
                model: 'bulk.res.partner.export.wizard',
                method: 'update_field_state',
                args: [wizardId, lineId, newState],
            }).then(() => {
                // Optional: You could show a notification or just let Odoo's UI update.
                // The view should update automatically, but you could trigger a reload
                // if needed, though it's usually not necessary.
                // this.reload();
            }).catch(err => {
                console.error("RPC call failed:", err);
                // Move the item back to its original list on failure
                $(item).sender.sortable('cancel');
            });
        },
    });
});