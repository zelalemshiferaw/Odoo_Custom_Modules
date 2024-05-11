/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_order_notes.pos_order_notes', function (require) {
    "use strict";
    const posModel = require('point_of_sale.models');
    const core = require('web.core');
    const { _t } = core;
    const rpc = require('web.rpc')
    const SuperOrder = posModel.Order;
    const ProductScreen = require('point_of_sale.ProductScreen');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const SuperOrderline = posModel.Orderline;
    const PosComponent = require('point_of_sale.PosComponent');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const orderNoteString = '#order_note'

    posModel.Order = posModel.Order.extend({
        get_order_note: function () {
            return $(orderNoteString).val();
        },
        export_as_JSON: function () {
            const self = this;
            const loaded = SuperOrder.prototype.export_as_JSON.call(this);
            loaded.order_note = self.get_order_note();
            self.order_note = self.get_order_note();
            return loaded;
        },
        export_for_printing: function () {
            const self = this
            const receipt = SuperOrder.prototype.export_for_printing.call(this)
            receipt.order_note = self.order_note;
            return receipt
        }
    });

    posModel.Orderline = posModel.Orderline.extend({
        initialize: function (attr, options) {
            this.order_line_note = '';
            SuperOrderline.prototype.initialize.call(this, attr, options);
        },
        export_for_printing: function () {
            const dict = SuperOrderline.prototype.export_for_printing.call(this);
            dict.order_line_note = this.order_line_note;
            return dict;
        },
        get_order_line_comment: function () {
            const self = this;
            return self.order_line_note;
        },
        export_as_JSON: function () {
            const self = this;
            const loaded = SuperOrderline.prototype.export_as_JSON.call(this);
            loaded.order_line_note = self.get_order_line_comment();
            return loaded;
        }
    });

    class AddOrderlineNoteButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        get currentOrder() {
            return this.env.pos.get_order();
        }
        async onClick() {
            const textLimit = this.env.pos.config.note_keyword_limit;
            const isTextLimit = this.env.pos.config.set_note_keyword_limit;
            if (typeof (this.currentOrder.get_selected_orderline()) == 'object') {
                const { confirmed } = await this.showPopup('WkTextAreaPopup', {
                    title: this.env._t('Add Note'),
                    value: this.currentOrder.get_selected_orderline().order_line_note,
                });
                $("textarea").css({ "width": "92%", "height": "56%", "resize": "none" });
                if (textLimit && isTextLimit) {
                    $("textarea").attr('maxlength', textLimit.toString());
                }
                if (confirmed) {
                    const note = $('textarea').val();
                    $('ul.orderlines li.selected ul div#extra_comments').text(note);
                    this.currentOrder.get_selected_orderline().order_line_note = note;
                }
            } else {
                this.showPopup('WkAlertPopUp', {
                    'title': 'No Selected Order Line',
                    'body': 'Please add/select an orderline'
                })
            }
        }
    }
    AddOrderlineNoteButton.template = 'AddOrderlineNoteButton';
    ProductScreen.addControlButton({
        component: AddOrderlineNoteButton,
        condition: function () { return this.env.pos.config.on_product_line; },
    });
    Registries.Component.add(AddOrderlineNoteButton);


    const PosResPaymentScreen = (PaymentScreen) => class extends PaymentScreen {
        async isPOSConnectedToInternet() {
            const currentUrl = window.location.href;
            const baseUrl = `${currentUrl.split('/')[0]}//${currentUrl.split('/')[2]}`;
            const sanitizedUrl = baseUrl.replace('http://', 'www.');

            try {
                const response = await fetch(`${sanitizedUrl}/web`, { method: 'GET' });
                return response.ok;
            }
            catch (error) {
                return false;
            }
        }

        async notConnectedValidation(self, orderNote) {
            const regexString = `${self.env.pos.config.wk_mpesa_regex}`;
            const wkMpesaRegex = new RegExp(regexString);
            const wkMpesaLength = self.env.pos.config.wk_mpesa_length

            if (!wkMpesaRegex.test(orderNote) || orderNote.length !== wkMpesaLength) {
                self.showPopup('ErrorPopup', {
                    title: _t('M-PESA Code Validation Failed'),
                    body: _t('Invalid M-PESA Code'),
                });
                return false
            }
            return true;
        }

        async connectedValidation(self, orderNote) {
            const result = await rpc.query({
                model: 'pos.order',
                method: 'wk_check_mpesa_code',
                args: [{
                    "mpesa_code": orderNote,
                    "wk_mpesa_regex": self.env.pos.config.wk_mpesa_regex,
                    "wk_mpesa_length": self.env.pos.config.wk_mpesa_length,
                }]
            })

            const { error } = result;
            if (error) {
                self.showPopup('WkAlertPopUp', {
                    title: 'Mpesa Code Error',
                    body: result?.message,
                });
                return false;
            }
            return true;
        }

        async fnValidateOrder(self, orderNote) {
            const isConnected = await this.isPOSConnectedToInternet()
            if (!isConnected) {
                return self.notConnectedValidation(self, orderNote)
            }
            return self.connectedValidation(self, orderNote);
        }


        async validateOrder(isForceValidate) {
            const self = this;
            const order = this.env.pos.get_order();

            if (order.is_return_order ||
                !this.env.pos.config.wk_mpesa_length ||
                !this.env.pos.config.wk_mpesa_regex ||
                !this.env.pos.config.on_order ||
                !this.env.pos.config.on_order_mandatory) {
                return super.validateOrder(isForceValidate);
            }

            if (!$(orderNoteString).val()) {
                $(orderNoteString).addClass('text_shake')
                return false;
            }

            const orderNote = $(orderNoteString).val()
            const _validateOrder = await this.fnValidateOrder(self, orderNote)
            return _validateOrder && super.validateOrder(isForceValidate);
        }
        async wkKeydownOrderNote(ev) {
            $(orderNoteString).removeClass('text_shake')
        }
    }
    Registries.Component.extend(PaymentScreen, PosResPaymentScreen);

    return AddOrderlineNoteButton;
});
