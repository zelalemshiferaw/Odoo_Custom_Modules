from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)
import datetime

class MrpValidation(models.Model):
    _inherit='mrp.production'

    validation_date=fields.Datetime("Validation Date")


class TransferValidation(models.Model):
    _inherit='stock.picking'
    
    validation_date=fields.Datetime("Validation Date")


class TransferMrp(models.Model):
    _name = 'mass.validation'

    name=fields.Char("Description",required=True)
    start_date=fields.Datetime("Start Date",required=True)
    end_date=fields.Datetime("End Date",required=True)
    total_records=fields.Integer("Total Records")
    picking_records=fields.Integer("Picking Records")
    mrp_records=fields.Integer("MRP Records")
    time_consumed=fields.Integer("Execution Minutes")

    done_state_picking_count=fields.Integer("Done State Picking Count")
    done_state_mrp_count=fields.Integer("Done State MRP Count")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('counted','Counted'),
        ('done', 'Done')
        ],
        default='draft')

    def get_stock_orders(self):
        minutes_consuming_start=0
        minutes_consuming_end=0
        diff_minutes=0

        minutes_consuming_start=datetime.datetime.now()
        stock_picking = self.env['stock.picking'].search([("state", "not in", ["cancel", "done"]), ("scheduled_date", ">",self.start_date),("scheduled_date", "<", self.end_date)], order="scheduled_date")        
        mrp_orders = self.env['mrp.production'].search([("state", "not in", ["cancel", "done"]), ("date_planned_start", ">",self.start_date),("date_planned_start", "<", self.end_date)], order="date_planned_start")

        list_dicto = stock_picking.mapped(lambda x: {
            'id': x.id,
            'name': x.name,
            'date_order': x.scheduled_date,
            'type': "picking"
        })

        list_dicto += mrp_orders.mapped(lambda x: {
            'id': x.id,
            'name': x.name,
            'date_order': x.date_planned_start,
            'type': "mrp"
        })

        sorted_list = sorted(list_dicto, key=lambda x: x['date_order'])

        c=0
        for record in sorted_list:
            if record['type'] == 'picking':
                transfer_record = self.env['stock.picking'].search([('name', '=', record['name'])],limit=1)
                _logger.info("+++++++++++++++++++++  Picking  +++++++++++++++++++++++++++++++++++++++++++++++++")
                # _logger.info(record.name)
                if transfer_record.state == 'draft':
                    transfer_record.action_confirm()                    
                    transfer_record.action_assign()
                    for mv in transfer_record.move_ids_without_package:
                        mv.quantity_done = mv.product_uom_qty
                    transfer_record.button_validate()
                    transfer_record.validation_date=datetime.datetime.now()

                elif transfer_record.state=='waiting':
                    transfer_record.action_assign()
                    for mv in transfer_record.move_ids_without_package:
                        mv.quantity_done = mv.product_uom_qty
                    transfer_record.button_validate()
                    transfer_record.validation_date=datetime.datetime.now()


                elif transfer_record.state=='confirmed':
                    transfer_record.action_assign()
                    for mv in transfer_record.move_ids_without_package:
                        mv.quantity_done = mv.product_uom_qty
                    transfer_record.button_validate()
                    transfer_record.validation_date=datetime.datetime.now()

                elif transfer_record.state=='assigned':
                    for mv in transfer_record.move_ids_without_package:
                        mv.quantity_done = mv.product_uom_qty
                    transfer_record.button_validate()
                    transfer_record.validation_date=datetime.datetime.now()



            elif record['type'] == 'mrp':
                mrp_record = self.env['mrp.production'].search([('name', '=', record['name'])],limit=1)

                if mrp_record.state == 'draft':
                    _logger.info("###########################################################")
                    # _logger.info(mrp_record.name)

                    mrp_record.action_confirm()
                    x = mrp_record.button_mark_done()
                    _logger.info(x['name'])

                    if x['name'] == "Immediate Production?":
                        immediate_prod_ctx = x['context']
                        immediate_prod_ctx.update({'active_id': mrp_record.id})
                        immediate_prod_wizard = self.env[x['res_model']].with_context(immediate_prod_ctx).create({})
                        immediate_prod_wizard.process()
                        mrp_record.validation_date=datetime.datetime.now()

                    else:
                        mrp_record.button_mark_done()
                        mrp_record.validation_date=datetime.datetime.now()

                elif mrp_record.state in ('confirmed', 'progress', 'to_close'):
                    _logger.info("###########################################################")
                    # _logger.info(mrp_record.name)
                    x = mrp_record.button_mark_done()
                    _logger.info(x['name'])

                    
                    if x['name'] == "Immediate Production?":
                        immediate_prod_ctx = x['context']
                        immediate_prod_ctx.update({'active_id': mrp_record.id})
                        immediate_prod_wizard = self.env[x['res_model']].with_context(immediate_prod_ctx).create({})
                        immediate_prod_wizard.process()
                        mrp_record.validation_date=datetime.datetime.now()

                    else:
                        mrp_record.button_mark_done()
                        mrp_record.validation_date=datetime.datetime.now()
            c=c+1
            if c%5==0:
                self.env.cr.commit()

        minutes_consuming_end=datetime.datetime.now()
        diff_minutes = int((minutes_consuming_end - minutes_consuming_start).total_seconds())

        self.time_consumed=diff_minutes
        self.state="done"

        if self.done_state_mrp_count > 0 and self.done_state_picking_count > 0:
            raise ValidationError('Some picking and mrp have already been validated, which can cause discrepancies in cost records. Please validate only pending records.') 
        if self.done_state_picking_count > 0:
            raise ValidationError('Some stock pickings have already been validated, which can cause discrepancies in cost records. Please validate only pending stock pickings.') 
        if self.done_state_mrp_count > 0:
            raise ValidationError('Some stock pickings have already been validated, which can cause discrepancies in cost records. Please validate only pending stock pickings.') 
        if not self.start_date or not self.end_date:
            raise ValidationError('Please provide start and end dates')


    def get_total_records(self):
        stock_picking = self.env['stock.picking'].search([("state", "not in", ["cancel", "done"]), ("scheduled_date", ">",self.start_date),("scheduled_date", "<", self.end_date)], order="scheduled_date")        
        mrp_orders = self.env['mrp.production'].search([("state", "not in", ["cancel", "done"]), ("date_planned_start", ">",self.start_date),("date_planned_start", "<", self.end_date)], order="date_planned_start")
        
        validated_stock_picking = self.env['stock.picking'].search([("state", "in", ["done"]), ("scheduled_date", ">",self.start_date),("scheduled_date", "<", self.end_date)], order="scheduled_date")        
        validated_mrp_orders = self.env['mrp.production'].search([("state", "in", ["done"]), ("date_planned_start", ">",self.start_date),("date_planned_start", "<", self.end_date)], order="date_planned_start")
        
        count=0
        picking_count=0
        mrp_count=0
        validated_picking_count=0
        validated_mrp_count=0

        list_dicto = stock_picking.mapped(lambda x: {
            'id': x.id,
            'name': x.name,
            'date_order': x.scheduled_date,
            'type': "picking"
        })

        list_dicto += mrp_orders.mapped(lambda x: {
            'id': x.id,
            'name': x.name,
            'date_order': x.date_planned_start,
            'type': "mrp"
        })

        sorted_list = sorted(list_dicto, key=lambda x: x['date_order'])
        
        count=len(sorted_list)
        picking_count=len(stock_picking)
        mrp_count=len(mrp_orders)
        validated_picking_count=len(validated_stock_picking)
        validated_mrp_count=len(validated_mrp_orders)

        self.total_records=count
        self.picking_records=picking_count
        self.mrp_records=mrp_count
        self.done_state_picking_count=validated_picking_count
        self.done_state_mrp_count=validated_mrp_count
        self.state='counted'


class PurchaseMassValidation(models.Model):
    _name = 'purchasemass.validation'

    name=fields.Char("Description",required=True)
    start_date=fields.Datetime("Start Date",required=True)
    end_date=fields.Datetime("End Date",required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')
        ],
        default='draft')

    def purchase_mass_validation(self):
        purchase_orders = self.env['purchase.order'].search([("state", "in", ["draft"]), ("date_order", ">",self.start_date),("date_order", "<", self.end_date)], order="date_order")  
        for pro in purchase_orders:
            pro.button_confirm()      
        self.state='done'