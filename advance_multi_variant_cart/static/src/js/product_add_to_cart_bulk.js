odoo.define('product_add_to_bulk_cart.cart', function (require) {
    "use strict";
    $(document).ready(function(){
        var ajax = require('web.ajax');
        $('.add_to_cart_bulk_div').on("click",function(ev){
        ev.preventDefault();
        ev.stopPropagation();
        var allElements = []
        var $forms= $('.multi_variant_list').find('.css_quantity');

        var x = 0;
        $.when($forms.each(function( index ,element) {

            var $input = $(element).find("input.js_quantity");
            var product_id = $input.attr('data-product-id');
            var qty = $input.val();            
            if( product_id && qty>0){
            allElements.push({'product_id': product_id ,'qty' : qty})
            
           }            
        })).done(function() {

           var k = allElements.length;

           if(k>=1){
           var time_out = allElements.length;
 					ajax.jsonRpc("/shop/cart/update_json_multi_carty", 'call', {
                            'datas' : allElements,
                        }).then(function (data){

                               $("input.js_quantity").val(0);
                               if(parseInt(data)==1){                               	
								if(document.URL.indexOf("?") == -1){
									window.location.href = document.URL + '?error_multi_cart=1';
								}
								else if(document.URL.indexOf("error_multi_cart") == -1){
									window.location.href = document.URL + '&error_multi_cart=1';
								}
                               }
                               else{
                               window.location.href = document.URL.replace('error_multi_cart=1','')
                               }
                               
                        });  
          }                  
      })
      
    });
    });    
});
