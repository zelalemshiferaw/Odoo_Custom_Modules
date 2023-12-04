odoo.define('Offers.OfferedItems', function(require){
    'use strict';
    var models = require('point_of_sale.models');
    var _super_product = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function(session, attributes){
            var self = this;
            models.load_fields('product.product', ['list_of_offer_products']);
            _super_product.initialize.apply(this, arguments);
        }
    });
});

odoo.define('Offers.receipt', function(require){
    "use strict";
    var models = require('point_of_sale.models');
    models.load_fields('product.product', 'list_of_offer_products');
    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        export_for_printing: function(){
            var line = _super_orderline.export_for_printing.apply(this, arguments);
            line.list_of_offer_products = this.get_product().list_of_offer_products;
            return line;
        }
    });
});