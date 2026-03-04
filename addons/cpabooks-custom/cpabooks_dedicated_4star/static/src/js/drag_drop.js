odoo.define('cpabooks_dedicated_4star.drag_drop', function (require) {
    "use strict";

    var KanbanRenderer = require('web.KanbanRenderer');

    KanbanRenderer.include({
        events: _.extend({}, KanbanRenderer.prototype.events, {
            'dragstart .o_kanban_record': '_onDragStart',
            'dragover .o_kanban_group': '_onDragOver',
            'dragleave .o_kanban_group': '_onDragLeave',
            'drop .o_kanban_group': '_onDrop',
        }),

        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                // Make records draggable and set data attributes
                self.$('.o_kanban_record').each(function() {
                    var $record = $(this);
                    var $fields = $record.find('field');
                    var fieldId = $fields.filter('[name="field_id"]').text();
                    var description = $fields.filter('[name="field_description"]').text();

                    if (fieldId) {
                        $record.attr({
                            'draggable': 'true',
                            'data-field-id': fieldId,
                            'data-description': description
                        });
                    }
                });
                console.log('Drag and drop initialized');
            });
        },

        _onDragStart: function (ev) {
            var $record = $(ev.currentTarget);
            var fieldId = $record.data('field-id');
            var description = $record.data('description');
            var fieldName = $record.closest('.o_kanban_view').find('> field').attr('name');

            ev.originalEvent.dataTransfer.setData('text/plain', JSON.stringify({
                field_id: fieldId,
                description: description,
                field_name: fieldName
            }));
            ev.originalEvent.dataTransfer.effectAllowed = 'move';

            $record.addClass('dragging');
        },

        _onDragOver: function (ev) {
            ev.preventDefault();
            ev.originalEvent.dataTransfer.dropEffect = 'move';
            $(ev.currentTarget).addClass('drag-over');
        },

        _onDragLeave: function (ev) {
            $(ev.currentTarget).removeClass('drag-over');
        },

        _onDrop: function (ev) {
            ev.preventDefault();
            $(ev.currentTarget).removeClass('drag-over');

            try {
                var data = JSON.parse(ev.originalEvent.dataTransfer.getData('text/plain'));
                var fieldId = data.field_id;
                var description = data.description;
                var sourceField = data.field_name;
                var targetField = $(ev.currentTarget).closest('.o_kanban_view').find('> field').attr('name');

                // Remove dragging class from all records
                $('.o_kanban_record').removeClass('dragging');

                if (fieldId && sourceField !== targetField) {
                    console.log('Moving field', fieldId, 'from', sourceField, 'to', targetField);

                    // Trigger custom event to handle the move
                    this.trigger_up('field_moved', {
                        field_id: fieldId,
                        description: description,
                        source_field: sourceField,
                        target_field: targetField
                    });
                }
            } catch (error) {
                console.error('Error parsing drag data:', error);
            }
        },
    });
});