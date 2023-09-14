from odoo import api, fields, models, tools, _
import logging
_logger=logging.getLogger(__name__)


class StockDate(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        super(StockDate, self)._action_done()
        if self.picking_type_code == 'outgoing' and 'Return' not in self.origin:
            self.write({"date": self.sale_id.date_order, "date_done": self.sale_id.date_order})
            self.move_lines.write({"date": self.sale_id.date_order})
            self.move_line_ids.write({"date": self.sale_id.date_order})
            
    def button_validate(self):
        if self.scheduled_date and self.picking_type_code == 'outgoing':
            return super(
                StockDate, self.with_context(force_period_date=self.scheduled_date)
            ).button_validate()           
        else:
            return super(StockDate, self).button_validate()

class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"
    _order = "id"

    create_date = fields.Datetime(related="stock_move_id.date", readonly=False)
