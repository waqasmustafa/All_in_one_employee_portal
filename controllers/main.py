from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
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
        
        if kw:
            # Handle profile update
            values = {
                'name': kw.get('name'),
                'work_phone': kw.get('work_phone'),
                'work_email': kw.get('work_email'),
                'private_phone': kw.get('private_phone'),
                'private_email': kw.get('private_email'),
            }
            if 'image_1920' in request.httprequest.files:
                file = request.httprequest.files['image_1920']
                if file:
                    values['image_1920'] = base64.b64encode(file.read())
            
            employee.sudo().write(values)
            return request.redirect('/my/profile?success=1')

        return request.render("employee_portal_ess.portal_my_profile", {
            'employee': employee,
            'page_name': 'my_profile',
        })
