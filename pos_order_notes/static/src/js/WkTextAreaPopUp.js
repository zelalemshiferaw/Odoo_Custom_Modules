/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('point_of_sale.WkTextAreaPopup', function (require) {
    'use strict';
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    class WkTextAreaPopup extends AbstractAwaitablePopup {
        getPayload() {
            return this.value;
        }
        mounted() {
            $('textarea').focus();
        }
    }
    WkTextAreaPopup.template = 'WkTextAreaPopup';
    WkTextAreaPopup.defaultProps = { title: 'Confirm ?', value: '' };
    Registries.Component.add(WkTextAreaPopup);

    return WkTextAreaPopup;
});
