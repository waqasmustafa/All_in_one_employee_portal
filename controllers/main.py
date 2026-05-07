from odoo import http, _
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
