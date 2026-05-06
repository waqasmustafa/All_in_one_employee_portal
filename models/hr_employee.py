from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Remove the domain that restricts to Internal Users only
    user_id = fields.Many2one('res.users', string='Related User', domain="[('active', '=', True)]")

    def get_portal_dashboard_stats(self):
        """ Return stats for the portal dashboard tiles. """
        self.ensure_one()
        return {
            'attendance_status': 'checked_in' if self.attendance_state == 'checked_in' else 'checked_out',
            'leave_balance': self.show_leaves and self.allocation_count or 0,
            'upcoming_tasks': self.env['project.task'].search_count([('user_ids', 'in', self.user_id.id), ('stage_id.is_closed', '=', False)]),
        }
