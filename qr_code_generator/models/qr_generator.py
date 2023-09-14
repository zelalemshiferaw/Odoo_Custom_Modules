from odoo import fields, api, models, _
from odoo.exceptions import UserError, ValidationError
import qrcode
import base64
from io import BytesIO
import logging
_logger=logging.getLogger(__name__)
import tempfile
import zipfile
import os
import io
import qrcode.constants
from PIL import Image, ImageOps, ImageDraw, ImageFont



class StoreQr(models.Model):
    _name="store.qr"


    store_ref = fields.Many2one('qr.ettagenerator','Store Name',store=True)
    name = fields.Char("Store")
    qr_code = fields.Binary("QR Code", attachment=True, store=True)
    link = fields.Char("Link")
    store_sequence = fields.Char("store seq")
    store_name_seq = fields.Char("Store Table")
    table_number = fields.Char("Table Number")
    store_id = fields.Char("store_id")

class QrGenerator(models.Model):
    _name= "qr.ettagenerator"

    name= fields.Char("Store Name")
    store_id= fields.Char("Store ID")
    table_amount = fields.Integer("Table Number")


    @api.constrains('store_id')
    def check_unique_storeid(self):
        records = self.search([('store_id', '=', self.store_id),('id', '!=', self.id)])
        if records:
            raise UserError(_('Another Store with same Store ID already exists.'))


    def view_store_qr(self):
        action = self.env.ref('qr_code_generator.action_store_qr').read()[0]
        action['domain'] = [('name', '=', self.name)]
        return action


    def generate_qr_code(self):
        common_link = "url"
        store_qr_model = self.env['store.qr']

        for sequence in range(1, self.table_amount + 1):
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            link = common_link + str(self.store_id) + "_" + str(sequence)
            st_seq=str(self.store_id) + "_" + str(sequence)
            
            if " " in str(self.name):
                formatted_name = str(self.name).replace(" ", "_")
            else:
                formatted_name = str(self.name)

            st_name_seq=formatted_name + "_" + str(sequence)
            qr.add_data(link)
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_image = base64.b64encode(temp.getvalue())

            existing = store_qr_model.search([('store_sequence','=',st_seq)])
            if not existing:
                data = {
                    'store_ref':self.env['qr.ettagenerator'].browse(self.id).id,
                    'name': self.name,
                    'link': link,
                    'qr_code': qr_image,
                    'store_sequence':st_seq,
                    "store_name_seq":st_name_seq,
                    'table_number':str(sequence)
                }
                store_qr_model.create(data)


    def download_qr_codes(self):
        # Get the base URL
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        # Create a zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            store_qr_model = self.env['store.qr']

            # Find all store QR codes related to the qr.ettagenerator record
            store_qr_codes = store_qr_model.search([('name', '=', self.name)])

            # Loop through each store QR code and add it to the zip archive
            for store_qr_code in store_qr_codes:
                qr_code_data = store_qr_code.qr_code
                qr_code_buffer = io.BytesIO(base64.b64decode(qr_code_data))

                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(qr_code_buffer.getvalue())
                    temp_file.flush()
                    os.fsync(temp_file.fileno())

                    zip_file.write(temp_file.name, f"{store_qr_code.store_name_seq}.png")

        # Create an attachment
        attachment_name=self.name + "_"+ str(self.table_amount)+".zip"

        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create({
            'name': attachment_name,
            'datas': base64.b64encode(zip_buffer.getvalue()),
            'res_model': self._name,
            'res_id': self.id,
        })

        # Prepare the download URL
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'

        # Return the download action
        return {
            'type': 'ir.actions.act_url',
            'url': str(base_url) + str(download_url),
            'target': 'new',
        }


    def unlink(self):
        store_qr_model = self.env['store.qr']
        for record in self:
            store_qr_unlink = store_qr_model.search([('name', '=', record.name)])
            store_qr_unlink.unlink()

        return super(QrGenerator, self).unlink()