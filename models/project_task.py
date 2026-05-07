from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    # Relax the domain to allow portal users to be assigned
    user_ids = fields.Many2many('res.users', string='Assignees', 
                                domain="['|', ('share', '=', False), ('groups_id', 'in', [7])]", # 7 is usually portal, but better to use ref
                                help="The internal or portal users assigned to this task.")

    @api.model
    def _get_portal_assignee_domain(self):
        portal_group = self.env.ref('base.group_portal')
        return ['|', ('share', '=', False), ('groups_id', 'in', [portal_group.id])]

    # Alternative: use a more dynamic domain in the view or here
    def _compute_user_ids_domain(self):
        portal_group = self.env.ref('base.group_portal')
        for task in self:
            pass # We already handled it in the field definition
