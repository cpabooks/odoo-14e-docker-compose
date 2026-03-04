odoo.define('capbooks_tawk_to_livechat_global.tawk_to', function (require) {
    "use strict";
    var core = require('web.core');
    var ajax = require('web.ajax');

    var id = 10;
    var self = this;
    ajax.rpc('/web/dataset/call_kw/res.config.settings/get_tawk_to', {
        model: 'res.config.settings',
        method: 'get_tawk_to',
        args: [id],
        kwargs: {},
    }).then(function (site_id) {
        console.log("site_id::", site_id);
        var Tawk_API=Tawk_API||{}, Tawk_LoadStart=new Date();
        var s1=document.createElement("script"),s0=document.getElementsByTagName("script")[0];
        s1.async=true;
        s1.src='https://embed.tawk.to/' + site_id;
        s1.charset='UTF-8';
        s1.setAttribute('crossorigin','*');
        s0.parentNode.insertBefore(s1,s0);
    });


});
