odoo.define('systray.systra_planning', function (require) {
    "use strict";

    var core = require('web.core');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');

    var _t = core._t;

    /**
     * Widget for the "Add Task" Icon
     */
    var ActionMenu = Widget.extend({
        template: 'systray_odoo_referral.plan_icon',
        events: {
            'click .plan_icon': '_onClickPlanIcon',
        },

        /**
         * Handles click event on the Add Task icon
         */
        _onClickPlanIcon: function (ev) {
            ev.preventDefault();
            try {
                console.log('Add Task button clicked');
                this.do_action('cpabooks_navbar.planning_popup_action', {
                    additional_context: {},
                });
            } catch (error) {
                console.error('Error while opening Add Task:', error);
            }
        },
    });

    /**
     * Widget for the "Add Ticket" Icon
     */
    var TicketMenu = Widget.extend({
        template: 'systray_odoo_referral_ticket',
        events: {
            'click .ticket_icon': '_onClickTicketIcon',
        },

        /**
         * Handles click event on the Add Ticket icon
         */
        _onClickTicketIcon: function (ev) {
            ev.preventDefault();
            try {
                console.log('Add Ticket button clicked');
                this.do_action('cpabooks_navbar.ticket_popup_action', {
                    additional_context: {},
                });
            } catch (error) {
                console.error('Error while opening Add Ticket:', error);
            }
        },
    });

    // Add to Systray Menu
    SystrayMenu.Items.push(ActionMenu);
    SystrayMenu.Items.push(TicketMenu);

    return {
        ActionMenu: ActionMenu,
        TicketMenu: TicketMenu,
    };
});
