from collections import defaultdict
from distutils.log import error
from itertools import groupby
from re import search
import datetime

from odoo import api, fields, models,  SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
	_inherit="res.users"

	user_location=fields.Many2one('stock.location')

class Transfer_request(models.Model):
	_name = "transfer.request"
	_description = "Transfer Request"

	def action_notify_report_date(self):
		today = datetime.datetime.now().day
		now = datetime.datetime.now()
		month_name = now.strftime("%B")
		if today == 25:                       
			message =  '<p><b><font color="red">Dear Inventory Team,<br> I trust you are doing great </font><br> You have left a few days for request report, Don\'t forget:<br>1. To check requested transfer.<br>2. To edit requests.<br><br><br>Thanks.</b></p>'
			channel = self.env['mail.channel'].browse(1)
			channel.message_post(subject="Report Date Reminder", body=message, author_id=2,
									message_type='comment', subtype_id=self.env.ref('mail.mt_comment').id)

	def download_button(self):
		query = """
			SELECT sol.name AS name, sol.scheduled_date AS scheduled_date FROM transfer_request sol 
		"""
		self.env.cr.execute(query)
		res = self.env.cr.dictfetchall()

		data = dict()
		lines = []
		for record in res:
			val = {
				'name': record.get('name'),
				'scheduled_date': record.get('scheduled_date'),
			}
			lines.append(val)
			_logger.info("________________++++++++++++++++++_________________________")
			_logger.info(record.get('name'))
			_logger.info(record.get('scheduled_date'))

		data['lines'] = lines
		return self.env.ref('stock_transfer.report_transfer_request_id').report_action(self, data=data)


	name = fields.Char(
		'Reference', default='/',
		copy=False, index=True , readonly=True)
	note = fields.Text('Notes')
	state = fields.Selection([
		('draft', 'Draft'),
		('waiting', 'Waiting For Approval'),
		('approved', 'Approve'),
		('done','Recieved'),
		('cancel', 'Cancel')
	   
	], string='Status',
		copy=False, index=True, readonly=True, store=True, tracking=True,default="draft")
	date = fields.Datetime(
		'Creation Date',
		default=fields.Datetime.now, index=True, tracking=True,
		help="Creation Date, usually the time of the order",
		states={'approved': [('readonly', True)],'done': [('readonly', True)],'cancel': [('readonly', True)]})
	scheduled_date = fields.Datetime('Scheduled date', default=fields.Datetime.now , copy=False, 
								help="Date at which the transfer has been processed or cancelled.",
								states={'approved': [('readonly', True)],'done': [('readonly', True)],'cancel': [('readonly', True)]})
	location_id = fields.Many2one(
		'stock.location', "Source Location",
		default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_src_id,
		required=True,
		states={'approved': [('readonly', True)],'done': [('readonly', True)],'cancel': [('readonly', True)]})
	location_dest_id = fields.Many2one(
		'stock.location', "Destination Location",
		default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_dest_id,
		required=True,
		states={'approved': [('readonly', True)],'done': [('readonly', True)],'cancel': [('readonly', True)]})
	picking_type_id = fields.Many2one(
		'stock.picking.type', 'Operation Type',
		required=True,
		states={'approved': [('readonly', True)],'done': [('readonly', True)],'cancel': [('readonly', True)]})
	user_id = fields.Many2one(
		'res.users', 'Request_by', default=lambda self: self.env.user,readonly=True,)
	approved_id = fields.Many2one(
		'res.users', 'Approved_by',readonly=True,)
	received_id = fields.Many2one(
		'res.users', 'Received_by',readonly=True)
	canceled_id = fields.Many2one(
		'res.users', 'Canceled_by',readonly=True)


	item_ids = fields.One2many('transfer.request.item' , 'transfer_request_id', 'Items',
				states={'approved': [('readonly', True)],'cancel': [('readonly', True)],'done': [('readonly', True)]})
	stock_picking = fields.Many2one('stock.picking', 'Transfer' , readonly=True)

	def action_request(self):
	  
		for record in self:
			if self.env.user.user_location.id != False and  self.env.user.user_location.id == record.location_dest_id.id:
				picking = self.create_transfer()
				record.state = "waiting"
				record.user_id = self.env.user.id
			else:
				raise UserError("Please check the destination id of transfer request. Your location Doesn't match with destination")

	def action_receive(self):
		for record in self:
			if self.env.user.user_location.id != False and self.env.user.user_location.id == record.location_dest_id.id:
				record.state = "done"
				record.received_id = self.env.user.id
			else:
				raise UserError("Please check the destination id of transfer request. Your location Doesn't match with destination")
			
	def action_cancel(self):
		for record in self:
			if self.env.user.user_location.id != False and self.env.user.user_location.id == record.location_id.id:
				record.state = "cancel"
				record.canceled_id = self.env.user.id
			else:
				raise UserError("Please check the destination id of transfer request. Your location Doesn't match with source")

	def action_confirm(self):
		for record in self:
			if record.location_id.id != record.location_dest_id.id:
				_logger.info("confirm ******************************************")
				if self.env.user.user_location != False and self.env.user.user_location.id == record.location_id.id:
					record.state = 'approved'
					record.approved_id = self.env.user.id
					self.validate_transfer()
				else:
					raise UserError("Please check the destination id of transfer request. Your location Doesn't match with source")
				
			else:
				raise UserError("source and destination location are the same. Please Check and try again")
	def action_print(self):
		for record in self:
			_logger.info(record.stock_picking)
			if record.stock_picking != False:
				_logger.info("***********************in picking")
				return self.env.ref('stock.action_report_picking').report_action(record.stock_picking)

	@api.model
	def create(self,vals):
		res = super(Transfer_request, self).create(vals)
		name = self.env['ir.sequence'].next_by_code('transfer.request')
		res.write({'name': name})
		return res

	@api.onchange('picking_type_id')
	def onchange_picking_type(self):
		if self.picking_type_id:
			if self.picking_type_id.default_location_src_id:
				location_id = self.picking_type_id.default_location_src_id.id
			else:
				customerloc, location_id = self.env['stock.warehouse']._get_partner_locations()

			if self.picking_type_id.default_location_dest_id:
				location_dest_id = self.picking_type_id.default_location_dest_id.id
			else:
				location_dest_id, supplierloc = self.env['stock.warehouse']._get_partner_locations()

			self.location_id = location_id
			self.location_dest_id = location_dest_id
		   

	@api.onchange('location_id')
	def _compute_availability_of_products(self):
		for record in self:
			_logger.info("1ocation*****************************************")
			for line in record.item_ids:
				if len(record.location_id) != 0:
					stock_quant = self.env['stock.quant'].sudo().search([("location_id","=",record.location_id.id), ("product_id","=",line.product_id.id)])
					for quant in stock_quant:
						line.products_availability += quant.quantity
						record.products_availability_dest -= quant.reserved_quantity
					if line.products_availability < 0:
						line.products_availability = 0 
					if line.demand > line.products_availability:
						line.demand = 0
					if line.products_availability == 0:
						line.demand = 0

	@api.onchange('location_dest_id')
	def _compute_availability_of_products(self):
		for record in self:
			_logger.info("1ocation*****************************************")
			for line in record.item_ids:
				if len(record.location_dest_id) != 0:
					stock_quant = self.env['stock.quant'].sudo().search([("location_id","=",record.location_dest_id.id), ("product_id","=",line.product_id.id)])
					for quant in stock_quant:
						line.products_availability_dest += quant.quantity
						record.products_availability_dest -= quant.reserved_quantity
					if line.products_availability_dest < 0:
						line.products_availability_dest = 0 
					if line.demand > line.products_availability_dest:
						line.demand = 0
					if line.products_availability_dest == 0:
						line.demand = 0

	@api.onchange('item_ids')
	def _compute_sequence_for_items(self):
		for record in self:
			_logger.info("compute number*****************************************")
			for index , line in enumerate(record.item_ids):
				line.number = index
				if line.products_availability < 0:
					line.products_availability = 0
					line.demand = 0
				if line.products_availability_dest < 0:
					line.products_availability_dest= 0
					line.demand = 0
				
	
	def create_transfer(self):
		try:
			for record in self:     
					vals = {
						"scheduled_date": record.scheduled_date,
						"date": record.date,
						"picking_type_id": record.picking_type_id.id,
						"location_id" : record.location_id.id,
						"location_dest_id"  : record.location_dest_id.id,
						"user_id": record.write_uid.id,
						"origin": record.name
					}
					move_ids = []
					for line in record.item_ids:
						if line.available_in_store == True:
							operation_line_data = {
								"product_uom_qty": line.demand,
								"name": line.product_id.display_name,
								"product_id": line.product_id.id,
								"product_uom": line.product_id.uom_id.id
							}
							operation_line = (0, 0, operation_line_data)
							move_ids.append(operation_line)

					vals['move_lines'] = move_ids
					_logger.info(vals)
					stock_picking = self.env['stock.picking'].create(vals)
					_logger.info(stock_picking)
					record.stock_picking = stock_picking.id
					return record
		except:
			raise UserError("Creation of Transfer Has Failed")

	def validate_transfer(self):
		# try:
			stock_picking = self.stock_picking
			if stock_picking.state != 'assigned':
					stock_picking.action_confirm()
			for each_stock_move in stock_picking.move_ids_without_package:
					each_stock_move.quantity_done = each_stock_move.product_uom_qty
					stock_picking.button_validate()        
			return True

		

class Transfer_request_item(models.Model):
	_name = "transfer.request.item"
	_description = "Transfer Request item"

	number = fields.Integer('Number', default=0 , readonly=True)
	transfer_request_id = fields.Many2one('transfer.request', 'Request')
	product_id = fields.Many2one('product.product', 'Product')
	products_availability = fields.Float(
		string="Product Availability", compute='_compute_products_availability')
	products_availability_dest = fields.Float(
		string="Product Availability Destination", compute='_compute_products_availability')
	demand = fields.Float(string="Demand")
	
	available_in_store = fields.Boolean("Available", default=True , readonly=True)
	

	@api.model
	def create(self,vals):
		_logger.info("******************************************create")
		
		for record in self:
			_logger.info(record.product_id)
			if len(record.product_id) !=0  and (record.transfer_request_id == False or len(record.transfer_request_id.location_id) != 0):
				raise UserError("Please Check source Location Before Creating Request Item")
			for each_item in record.transfer_request_id.item_ids:
				if each_item.product_id == record.product_id:
					raise UserError("Product Already Exsists In the List")
		res = super(Transfer_request_item, self).create(vals)
		return res

	@api.depends('transfer_request_id', 'product_id')
	def _compute_products_availability(self):
		for record in self:
			_logger.info("*****************************************product avilability")
			_logger.info(record.transfer_request_id.location_id)
			if len(record.transfer_request_id.location_id) != 0 and len(record.transfer_request_id.location_dest_id) != 0:
				stock_quant = self.env['stock.quant'].sudo().search([("location_id","=",record.transfer_request_id.location_id.id), ("product_id","=",record.product_id.id)])
				stock_quant_dest = self.env['stock.quant'].sudo().search([("location_id","=",record.transfer_request_id.location_dest_id.id), ("product_id","=",record.product_id.id)])
				record.products_availability = 0
				record.products_availability_dest = 0
				for quant in stock_quant:
					record.products_availability += quant.quantity
					record.products_availability -= quant.reserved_quantity
				for quant in stock_quant:
					record.products_availability_dest += quant.quantity
					record.products_availability_dest -= quant.reserved_quantity
				
			else:
				raise UserError("Please choose locations first")
	@api.onchange('demand')
	def _compute_demand_is_available(self):
		for record in self:
			_logger.info("*****************************************demand")
			_logger.info(record.product_id)
			if record.demand < 0:
				record.demand = 0
				raise UserError("Demand is lower than 0")
			if len(record.product_id) != 0 and record.demand > record.products_availability:
				record.demand = 0
				raise UserError("Demand is higher than stock on hand")
			if len(record.product_id) != 0 and record.products_availability == 0:
				record.demand = 0
				raise UserError("This Product is not available in the source location")
			_logger.info("here inside change transfer top")
			if record.transfer_request_id.stock_picking != False and (record.transfer_request_id.stock_picking.state == 'draft' and (record.transfer_request_id.state == 'waiting' or  record.transfer_request_id.state == 'draft')):
				_logger.info("here inside change transfer big one")
				for lines in record.transfer_request_id.stock_picking.move_lines:
					_logger.info("looping")
					if lines.product_id == record.product_id:
						lines.product_uom_qty = record.demand
						_logger.info("change transfer lines *******************")
						break;
	
	def action_change_availability(self):
		for record in self:
			if record.available_in_store == True:
				if record.transfer_request_id.stock_picking != False:
					for lines in record.transfer_request_id.stock_picking.move_ids_without_package:
						if lines.product_id.id == record.product_id.id:
							lines.quantity_done = 0
			record.available_in_store = not record.available_in_store

