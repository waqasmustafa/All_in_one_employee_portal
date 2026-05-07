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
        
        # Get all active leave types
        leave_types = request.env['hr.leave.type'].sudo().search([
            ('active', '=', True)
        ])
        
        # Robustly fetch and clean allocation data for Odoo 18
        balances = []
        try:
            balances_data = leave_types.get_allocation_data(employee)
            raw_balances = balances_data.get(employee, [])
            
            # Ensure raw_balances is a list or tuple we can iterate
            if not isinstance(raw_balances, (list, tuple)):
                raw_balances = [raw_balances] if raw_balances else []
                
            for item in raw_balances:
                if isinstance(item, dict):
                    balances.append(item)
                elif isinstance(item, (list, tuple)) and len(item) > 0:
                    # If it's a nested structure, try to find the dict inside
                    for sub_item in item:
                        if isinstance(sub_item, dict):
                            balances.append(sub_item)
        except Exception as e:
            # Fallback to empty list if something goes wrong
            balances = []
            
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
                'request_date_from': kw.get('date_from'),
                'request_date_to': kw.get('date_to'),
                'employee_id': employee.id,
                'request_unit_hours': False,
            })
            return request.redirect('/my/leaves?success=1')
        except Exception as e:
            return request.redirect('/my/leaves?error=%s' % str(e))

    @http.route(['/my/payroll'], type='http', auth="user", website=True)
    def portal_my_payroll(self, **kw):
        employee = request.env.user.employee_id
        if not employee:
            return request.redirect('/my')
        
        # Get payslips for the employee
        payslips = request.env['hr.payslip'].sudo().search([
            ('employee_id', '=', employee.id),
            ('state', 'in', ['done', 'paid'])
        ], order='date_from desc')
        
        values = {
            'employee': employee,
            'payslips': payslips,
            'page_name': 'payroll',
        }
        return request.render("All_in_one_employee_portal.portal_my_payroll", values)

    @http.route(['/my/payslip/download/<int:payslip_id>'], type='http', auth="user", website=True)
    def portal_payslip_download(self, payslip_id, **kw):
        employee = request.env.user.employee_id
        if not employee:
            return request.redirect('/my')
        
        # Search for the payslip belonging to this employee
        payslip = request.env['hr.payslip'].sudo().search([
            ('id', '=', payslip_id),
            ('employee_id', '=', employee.id)
        ], limit=1)
        
        if not payslip:
            return request.redirect('/my/payroll')

        # Generate the PDF report using sudo to bypass security restrictions
        pdf_content, content_type = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
            'hr_payroll.action_report_payslip', [payslip.id]
        )
        
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf_content)),
            ('Content-Disposition', 'attachment; filename="%s.pdf"' % payslip.number)
        ]
        return request.make_response(pdf_content, headers=pdfhttpheaders)

    @http.route(['/my/tasks'], type='http', auth="user", website=True)
    def portal_my_tasks(self, **kw):
        employee = request.env.user.employee_id
        if not employee:
            return request.redirect('/my')
        
        # Get tasks assigned to the employee's user
        tasks = request.env['project.task'].sudo().search([
            ('user_ids', 'in', [request.env.user.id])
        ], order='create_date desc')
        
        values = {
            'employee': employee,
            'tasks': tasks,
            'page_name': 'tasks',
        }
        return request.render("All_in_one_employee_portal.portal_my_tasks", values)

    @http.route(['/my/timesheets'], type='http', auth="user", website=True)
    def portal_my_timesheets(self, **kw):
        employee = request.env.user.employee_id
        if not employee:
            return request.redirect('/my')
        
        # Get timesheet lines for the employee
        timesheets = request.env['account.analytic.line'].sudo().search([
            ('employee_id', '=', employee.id),
            ('project_id', '!=', False)
        ], limit=20, order='date desc')
        
        # Get employee's tasks for logging
        tasks = request.env['project.task'].sudo().search([
            ('user_ids', 'in', [request.env.user.id])
        ])
        
        values = {
            'employee': employee,
            'timesheets': timesheets,
            'tasks': tasks,
            'page_name': 'timesheets',
            'success': kw.get('success'),
            'error': kw.get('error'),
        }
        return request.render("All_in_one_employee_portal.portal_my_timesheets", values)

    @http.route(['/my/timesheets/log'], type='http', auth="user", methods=['POST'], website=True)
    def portal_timesheets_log(self, **kw):
        employee = request.env.user.employee_id
        if not employee:
            return request.redirect('/my')
        
        try:
            task = request.env['project.task'].sudo().browse(int(kw.get('task_id')))
            request.env['account.analytic.line'].sudo().create({
                'name': kw.get('name') or 'Work log',
                'project_id': task.project_id.id,
                'task_id': task.id,
                'employee_id': employee.id,
                'date': kw.get('date') or fields.Date.today(),
                'unit_amount': float(kw.get('unit_amount')),
            })
            return request.redirect('/my/timesheets?success=1')
        except Exception as e:
            return request.redirect('/my/timesheets?error=%s' % str(e))
