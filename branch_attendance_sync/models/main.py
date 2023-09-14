from odoo import fields,api,models,_
import erppeek
import datetime
from datetime import datetime
import logging
import sys
_logger=logging.getLogger(__name__)
from datetime import timedelta
from odoo.tools import float_compare

class RemoteEmployee(models.Model):
    _inherit='hr.employee'

    remote_device_id=fields.Char(string="Remote Device ID")

class HrBranchsync(models.Model):
    _name='branch.sync'


    branch_ip=fields.Char(string="Branch IP",required=True)
    branch_db=fields.Char(string="Branch Database",required=True) 
    branch_user=fields.Char(string="Branch Login",required=True)
    branch_password=fields.Char(string="Branch Password",required=True)
    branch_name= fields.Many2one('res.branch',string="Branch Name", required=True)
    
    centeral_ip=fields.Char(string="Centeral IP",required=True,default="http://196.188.109.181:8069")
    centeral_db=fields.Char(string="Centeral Database", required=True,default="lewis_retails_one")
    centeral_user=fields.Char(string="Centeral Login", required=True, default="admin")
    centeral_password=fields.Char(string="Centeral Password", required=True, default="admin")

    sync_descrption=fields.Char("Description")

    def get_erppeek_instance_lewis_retails(self):
        api_lewis=erppeek.Client(self.centeral_ip,self.centeral_db,self.centeral_user,self.centeral_password)

        return api_lewis

    def get_erppeek_instance_branch(self):
        api_branch=erppeek.Client(self.branch_ip,self.branch_db,self.branch_user,self.branch_password)

        return api_branch     


    def sync_branch_attendance(self):
        api_lewis=self.get_erppeek_instance_lewis_retails()
        api_branch = self.get_erppeek_instance_branch()
        start_date=datetime.now().replace(month=7,day=1,year=2023,hour=0, minute=0, second=0)

        # Branch Data
        api_branch_attendance=api_branch.model('hr.attendance').search([])
        _logger.info("===========================================")

        # Centeral Data
        lewis_attendance_model= api_lewis.model('hr.attendance')   



        for hr_data in api_branch_attendance:  
            get_attendance = api_branch.model('hr.attendance').browse(hr_data)

            emp_i = api_lewis.model('hr.employee').search([('remote_device_id','=',get_attendance.employee_id.device_id),('branch_id','=',self.branch_name.id)],limit=1)  if get_attendance.employee_id else False;
            
            if not emp_i:
                continue

            emppp = api_lewis.model('hr.employee').browse(emp_i)
            lewis_empo_id=int(emppp.id[0]) if emp_i else False

            already_synced= lewis_attendance_model.search([
                ('branch_attendance_id', '=', get_attendance.id),
                ('check_out', '!=', False),
                ('check_in', '!=', False),
                ('branch','=',self.branch_name.id)


            ])

            ext = lewis_attendance_model.search([
                ('branch_attendance_id', '=', get_attendance.id),
                ('branch','=',self.branch_name.id),
                ('check_out', '=', False)
            ],limit=1)

            extt = lewis_attendance_model.browse(ext)
            if ext:
                extt.write({'check_out': get_attendance.check_out})


            if not ext and not already_synced:
                data={
                    'employee_id': lewis_empo_id,
                    'check_in': get_attendance.check_in,
                    'check_out': get_attendance.check_out,
                    'branch':self.branch_name.id,
                    'branch_attendance_id':get_attendance.id

                }

                res=api_lewis.model('hr.attendance').create(data)
                get_attendance.x_studio_synced=True
        return {

            'effect': {

                'fadeout': 'slow',

                'message': 'Everything is correctly Done...',

                'type': 'rainbow_man',

            }

        }


class HrAttendancesync(models.Model):
    _inherit='hr.attendance'

    # attendance_synced=fields.Boolean(string="Synced")
    branch= fields.Many2one('res.branch',string="Branch")
    branch_attendance_id = fields.Char(string="Branch attendance id")




