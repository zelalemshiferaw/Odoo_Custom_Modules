odoo.define('stock_transfer.list_view_click_button', function (require) {
	"use strict";

	var ListController = require('web.ListController');

	ListController.include({
		renderButtons: function ($node) {
			this._super.apply(this, arguments);

			if (this.modelName === 'transfer.request') {
				this.$buttons.append('<button type="button" class="btn btn-secondary download_button">Print All</button>');
				this.$buttons.on('click', '.download_button', this._onDownloadButtonClick.bind(this));
			}
		},

		_onDownloadButtonClick: function () {
			var self = this;

			this._rpc({
				model: 'transfer.request',
				method: 'download_button',
				args: [""],
			}).then(function (result) {
				if (result) {
					self.do_action(result);
				}
			});
		},
	});
});