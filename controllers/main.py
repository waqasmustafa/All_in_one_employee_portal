from odoo import http, _, fields
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
import base64

class EmployeePortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        employee = request.env.user.employee_id
        if employee:
            values.update({
                'employee': employee,
                'dashboard_stats': employee.get_portal_dashboard_stats(),
            })
        return values

    @http.route(['/my/profile', '/my/profile/edit'], type='http', auth="user", website=True)
    def portal_my_profile(self, **kw):
        employee = request.env.user.employee_id
        if not employee:
            return request.redirect('/my')
        
        if http.request.httprequest.method == 'POST':
            # Handle profile update
            values = {}
            if kw.get('name'):
                values['name'] = kw.get('name')
            if kw.get('work_phone') is not None:
                values['work_phone'] = kw.get('work_phone')
            if kw.get('work_email') is not None:
                values['work_email'] = kw.get('work_email')
            if kw.get('private_phone') is not None:
                values['private_phone'] = kw.get('private_phone')
            if kw.get('private_email') is not None:
                values['private_email'] = kw.get('private_email')
            if kw.get('birthday'):
                values['birthday'] = kw.get('birthday')
            if kw.get('private_street') is not None:
                values['private_street'] = kw.get('private_street')
            
            if 'image_1920' in request.httprequest.files:
                file = request.httprequest.files['image_1920']
                if file and file.filename:
                    values['image_1920'] = base64.b64encode(file.read())
            
            if values:
                employee.sudo().write(values)
            return request.redirect('/my/profile?success=1')

        values = {
            'employee': employee,
            'page_name': 'my_profile',
            'success': kw.get('success'),
        }
        return request.render("All_in_one_employee_portal.portal_my_profile", values)

    @http.route(['/my/attendance'], type='http', auth="user", website=True)
    def portal_my_attendance(self, **kw):
        employee = request.env.user.employee_id
        if not employee:
            return request.redirect('/my')
        
        attendances = request.env['hr.attendance'].sudo().search([
            ('employee_id', '=', employee.id)
        ], limit=10, order='check_in desc')
        
        values = {
            'employee': employee,
            'attendances': attendances,
            'page_name': 'attendance',
        }
        return request.render("All_in_one_employee_portal.portal_my_attendance", values)

    @http.route(['/my/attendance/toggle'], type='json', auth="user", methods=['POST'], website=True)
    def portal_attendance_toggle(self, latitude=None, longitude=None, **kw):
        employee = request.env.user.employee_id
        if not employee:
            return {'error': 'Employee not found'}
        
        attendance = employee.action_portal_attendance_toggle(latitude, longitude)
        return {
            'status': employee.attendance_state,
            'check_in': attendance.check_in,
            'check_out': attendance.check_out,
        }

    @http.route(['/my/leaves'], type='http', auth="user", website=True)
    def portal_my_leaves(self, **kw):
        employee = request.env.user.employee_id
        if not employee:
            return request.redirect('/my')
        
        # Get leave balances
        leave_types = request.env['hr.leave.type'].sudo().search([
            ('has_valid_allocation', '=', True)
        ])
        balances = leave_types.get_allocation_data(employee)
        
        # Get leave history
        leaves = request.env['hr.leave'].sudo().search([
            ('employee_id', '=', employee.id)
        ], order='date_from desc')
        
        values = {
            'employee': employee,
            'balances': balances,
            'leaves': leaves,
            'leave_types': leave_types,
            'page_name': 'leaves',
            'success': kw.get('success'),
            'error': kw.get('error'),
        }
        return request.render("All_in_one_employee_portal.portal_my_leaves", values)

    @http.route(['/my/leaves/apply'], type='http', auth="user", methods=['POST'], website=True)
    def portal_my_leaves_apply(self, **kw):
        employee = request.env.user.employee_id
        if not employee:
            return request.redirect('/my')
        
        try:
            request.env['hr.leave'].sudo().create({
                'name': kw.get('name') or 'Leave Request',
                'holiday_status_id': int(kw.get('holiday_status_id')),
                'date_from': kw.get('date_from'),
                'date_to': kw.get('date_to'),
                'employee_id': employee.id,
                'request_unit_hours': False,
            })
            return request.redirect('/my/leaves?success=1')
        except Exception as e:
            return request.redirect('/my/leaves?error=%s' % str(e))
