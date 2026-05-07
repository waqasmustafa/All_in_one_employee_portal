{
    'name': 'All-in-One Employee Portal',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Employee Self-Service (ESS) Portal with a modern dashboard.',
    'description': """
        This module provides a complete Employee Self-Service portal where employees
        can manage their profiles, attendance, leaves, payroll, and more from a
        unified dashboard.
    """,
    'author': 'Antigravity',
    'depends': ['portal', 'hr', 'hr_attendance', 'hr_holidays', 'hr_payroll', 'project', 'hr_timesheet', 'hr_expense'],
    'data': [
        'security/ir.model.access.csv',
        'security/security_rules.xml',
        'security/ir_rule.xml',
        'views/portal_templates.xml',
        'views/profile_templates.xml',
        'views/hr_employee_views.xml',
        'views/hr_attendance_views.xml',
        'views/project_task_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'All_in_one_employee_portal/static/src/css/portal_dashboard.css',
            'All_in_one_employee_portal/static/src/js/portal_attendance.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
