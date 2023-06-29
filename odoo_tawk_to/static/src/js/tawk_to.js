odoo.define('wk_tawk_to.wk_tawk_to', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    $(document).ready(function () {
        ajax.jsonRpc("/wk/tawk/to/", 'call', {
            }).then(function (data) {
                if (data != true)
                {
                     console.log('---------NO Tawk Site ID Defined------')
                }
            }).fail(function(err){
                    console.log('-------Error in fetching tawk site id-------',err);
        });
    });
});
