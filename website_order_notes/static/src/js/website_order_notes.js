odoo.define('website_order_notes.website_order_notes', function (require) 
{
    "use strict";
    var core = require('web.core');
    var _t = core._t;
    var ajax = require('web.ajax');
	$(document).ready(function() 
	{ 
		$('#o_payment_form_pay').on('click',function(ev)
		{
			var notes = $('.wk_notes_textarea').val();
			var desire_date = $('.wk_desire_date').val();
			var max_days = $('.wk_desire_date').attr('max_val');
			var min_days = $('.wk_desire_date').attr('min_val');
			var max_date = new Date();
			max_date.setDate(max_date.getDate()+parseInt(max_days));
			var min_date = new Date();
			min_date.setDate(min_date.getDate()+parseInt(min_days));
			var  show_pop_up = false;
			var msg = "";
			if (new Date(desire_date) < min_date){
				msg = "You are not allowed to choose your desired delivery date before "+min_days+" days from current date."
				show_pop_up = true;
			}
			if (new Date(desire_date) > max_date)
			{
				msg = "You are not allowed to choose your desired delivery date greater than "+max_days+" days from current date."
				show_pop_up = true;
			}
			if(show_pop_up)
				{
					$(this).prop("disabled", "disabled");
					var self = $(this)
					self.popover({
						content:"<center><font color='red'>"+msg+"</font></center>",
						title:"<center ><font color='red'>WARNING!!</font></center>",
						html:true,
						placement:"left",
						trigger:'focus',
					});
					self.popover('show');
					setTimeout(function() {
						self.popover('destroy');
					},3000);
				}
			else{
				ajax.jsonRpc('/website/order/notes', 'call', {'notes': notes, 'desire_date': desire_date}).then(function (res)
				{
				}).fail(function (err)
				{
					console.log(err);
				});
			}
				
		});


		$("input[name=desire_date]").on('change',function(ev)
		{
			$("#o_payment_form_pay").prop("disabled", false);
			$("#o_payment_form_pay").popover('destroy');
		});

	});
});